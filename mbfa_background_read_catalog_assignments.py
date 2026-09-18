import bpy, sys, json, os

def main():
    settings_path = sys.argv[-1]
    with open(settings_path, "r", encoding="utf-8") as f: settings = json.load(f)

    asset_file_path = settings["asset_file_path"]
    result_path = settings["result_path"]
    result = {"assignments": [], "failed": []}

    if not os.path.exists(asset_file_path):
        result["failed"].append(f"Asset file not found: {asset_file_path}")
        with open(result_path, "w", encoding="utf-8") as f: json.dump(result, f, indent=4)
        return

    try:
        bpy.ops.wm.open_mainfile(filepath=asset_file_path)
        for brush in bpy.data.brushes:
            if brush.asset_data is None: 
                continue
            catalog_id = brush.asset_data.catalog_id

            if not catalog_id:
                continue

            uuid = str(catalog_id)
            
            result["assignments"].append({"brush_name": brush.name, "catalog_uuid": uuid})
            
    except Exception as e:
        result["failed"].append(str(e))

    with open(result_path, "w", encoding="utf-8") as f: 
        json.dump(result, f, indent=4)

if __name__ == "__main__": main()
