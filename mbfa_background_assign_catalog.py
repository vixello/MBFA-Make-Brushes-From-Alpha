import bpy
import sys
import json
import os


def main():
    settings_path = sys.argv[-1]

    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    asset_file_path = settings["asset_file_path"]
    result_path = settings["result_path"]
    brush_names = settings["brush_names"]
    catalog_uuid = settings["catalog_uuid"]

    result = {
        "assigned": [],
        "missing": [],
        "failed": [],
    }

    # Open the asset library blend file
    if not os.path.exists(asset_file_path):
        result["failed"].append({
            "error": f"Asset file not found: {asset_file_path}"
        })

        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)

        return

    bpy.ops.wm.open_mainfile(filepath=asset_file_path)

    for brush_name in brush_names:
        brush = bpy.data.brushes.get(brush_name)

        if brush is None:
            result["missing"].append(brush_name)
            continue

        try:
            # Make sure it is an asset
            if brush.asset_data is None:
                brush.asset_mark()

            brush.asset_data.catalog_id = catalog_uuid

            result["assigned"].append(brush_name)

        except Exception as e:
            result["failed"].append({
                "name": brush_name,
                "error": str(e),
            })

    # Save the modified asset library
    bpy.ops.wm.save_as_mainfile(filepath=asset_file_path)

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    main()