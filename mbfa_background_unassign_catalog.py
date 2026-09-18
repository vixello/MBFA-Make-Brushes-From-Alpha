import bpy
import sys
import json
import os
import traceback

print("MBFA: *** BACKGROUND UNASSIGN SCRIPT LOADED ***")
print("MBFA: sys.argv =", sys.argv)

def write_result(result_path, result):
    print("MBFA: Writing result to:")
    print(result_path)

    try:
        result_dir = os.path.dirname(result_path)

        if result_dir:
            os.makedirs(result_dir, exist_ok=True)

        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)

        print("MBFA: Result file created:", os.path.exists(result_path))

        if os.path.exists(result_path):
            print(
                "MBFA: Result file size:",
                os.path.getsize(result_path)
            )

    except Exception:
        print("MBFA: Could not write result file:")
        traceback.print_exc()
        
def get_settings_path():
    if "--" not in sys.argv:
        raise RuntimeError(
            f"MBFA: No '--' separator found in arguments: {sys.argv}"
        )

    args = sys.argv[sys.argv.index("--") + 1:]

    if not args:
        raise RuntimeError(
            f"MBFA: No settings path supplied after '--': {sys.argv}"
        )

    return args[0]

def main():
    result_path = None

    try:
        settings_path = get_settings_path()

        print("MBFA: Settings path:", settings_path)
        print("MBFA: Settings exists:", os.path.exists(settings_path))

        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        asset_file_path = settings["asset_file_path"]
        result_path = settings["result_path"]
        brush_names = settings["brush_names"]
        catalog_uuid = settings["catalog_uuid"]

        result = {
            "unassigned": [],
            "missing": [],
            "failed": [],
        }

        print("========================================")
        print("MBFA UNASSIGN")
        print("========================================")
        print("Asset:", asset_file_path)
        print("Catalog:", catalog_uuid)
        print("Brushes:", brush_names)
        print("Result:", result_path)
        print("")

        # Check asset file
        # -----------------------------------------------------
        if not os.path.exists(asset_file_path):
            result["failed"].append({"error": f"Asset file not found: {asset_file_path}"})

            write_result(result_path, result)
            return

        # Open asset library
        # -----------------------------------------------------
        open_result = bpy.ops.wm.open_mainfile(
            filepath=asset_file_path
        )

        print("open_mainfile result:", open_result)

        if "FINISHED" not in open_result:
            result["failed"].append({"error": "Blender failed to open the asset library."})

            write_result(result_path, result)
            return

        # Process brushes
        # -----------------------------------------------------
        for brush_name in brush_names:

            brush = bpy.data.brushes.get(brush_name)

            if brush is None:
                result["missing"].append(brush_name)
                continue

            try:

                # Brush must be an asset
                # -------------------------------------------------
                if not brush.asset_data:
                    result["missing"].append(brush_name)
                    continue

                current_catalog_id = brush.asset_data.catalog_id

                if not current_catalog_id:
                    print(f"MBFA: '{brush_name}' has no catalog.")

                    result["missing"].append(brush_name)
                    continue

                current_catalog_uuid = str(current_catalog_id)

                print(
                    f"MBFA: '{brush_name}' current catalog = {current_catalog_uuid}"
                )

                # Only unassign if it belongs to the selected catalog
                # -------------------------------------------------
                if current_catalog_uuid != catalog_uuid:

                    print(f"MBFA: '{brush_name}' is not in selected catalog."
                    )

                    result["missing"].append(brush_name)
                    continue

                # Remove catalog assignment
                # -------------------------------------------------
                print(
                    f"MBFA: Removing catalog '{catalog_uuid}' from '{brush_name}'"
                )

                brush.asset_data.catalog_id = ""

                result["unassigned"].append(brush_name)

            except Exception as e:

                result["failed"].append({
                    "name": brush_name,
                    "error": str(e),
                })

        # Save modified asset library
        # -----------------------------------------------------
        save_result = bpy.ops.wm.save_as_mainfile(
            filepath=asset_file_path
        )

        print(
            "save_as_mainfile result:",
            save_result
        )

        if "FINISHED" not in save_result:
            result["failed"].append({
                "error": "Blender failed to save the asset library."
            })

        # Write result
        # -----------------------------------------------------
        write_result(
            result_path,
            result
        )

        print("")
        print("========================================")
        print("MBFA UNASSIGN RESULT")
        print("========================================")
        print(json.dumps(result, indent=4))
        print("")

    except Exception as e:

        print("========================================")
        print("MBFA UNASSIGN BACKGROUND ERROR")
        print("========================================")

        traceback.print_exc()

        if result_path:
            write_result(
                result_path,
                {
                    "unassigned": [],
                    "missing": [],
                    "failed": [{
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }],
                }
            )

        raise


if __name__ == "__main__":
    main()