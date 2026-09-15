import bpy
import json
import os
import sys

# READ SETTINGS
settings_path = sys.argv[-1]
with open(settings_path, "r", encoding="utf-8") as f:
    settings = json.load(f)

asset_file_path = settings["asset_file_path"]
result_path = settings["result_path"]

items = settings["items"]
overwrite = settings.get("overwrite", False)

created_brushes = []
skipped_brushes = []
failed_brushes = []


print("")
print("========================================")
print(" MBFA ASSET LIBRARY GENERATOR")
print("========================================")
print("")
print("Asset library:", asset_file_path)
print("Brush count:", len(items))
print("")

# DISABLE BLEND BACKUPS
bpy.context.preferences.filepaths.save_version = 0

# OPEN OR CREATE ASSET LIBRARY
if os.path.exists(asset_file_path):
    print("Opening existing asset library:", asset_file_path)
    bpy.ops.wm.open_mainfile(filepath=asset_file_path)
else:
    print("Creating new asset library:", asset_file_path)
    bpy.ops.wm.read_factory_settings(use_empty=True)

# CREATE / UPDATE BRUSHES
for data in items:

    name = data["brush_name"]
    if not name:
        name = os.path.splitext(data["filename"])[0]

    image_path = data["image_path"]

    print("")
    print("----------------------------------------")
    print("Processing brush:", name)
    print("----------------------------------------")

    # REMOVE EXISTING BRUSH
    # old_brush = bpy.data.brushes.get(name)
    # if old_brush:
    #     print("Updating existing brush:", name)
    #     bpy.data.brushes.remove(old_brush, do_unlink=True)


    try:
        # CHECK IF BRUSH EXISTS
        existing_brush = bpy.data.brushes.get(name)
        
        if existing_brush and not overwrite:
            print("Brush already exists, skipping:", name)
            skipped_brushes.append(data)
            continue
        
        if existing_brush and overwrite:
            print("Overwriting existing brush:", name)
            bpy.data.brushes.remove(
                existing_brush,
                do_unlink=True
            )
            
        # LOAD IMAGE
        print("Loading image:", image_path)
        img = bpy.data.images.load(image_path, check_existing=False)
        img.name = name + "_Alpha"

        # INVERT ALPHA
        if data.get("invert_alpha", False):
            print("Inverting alpha:", name)
            pixels = list(img.pixels)
            for i in range(0, len(pixels), 4):
                pixels[i]     = 1.0 - pixels[i]
                pixels[i + 1] = 1.0 - pixels[i + 1]
                pixels[i + 2] = 1.0 - pixels[i + 2]
                pixels[i + 3] = 1.0 - pixels[i + 3]
            img.pixels = pixels

        # CREATE TEXTURE
        tex = bpy.data.textures.new(name + "_tex", type="IMAGE")
        tex.image = img

        # CREATE BRUSH
        brush = bpy.data.brushes.new(name=name)
        
        if data["texture_paint"] == False:
            brush.use_paint_sculpt = True
            brush.use_paint_vertex = False                
            
        elif data["texture_paint"] == True:
            brush.use_paint_sculpt = False
            brush.use_paint_image = True
            
        brush.stroke_method = data["stroke_method"]
        brush.size = data["size"]
        brush.strength = data["strength"]
        brush.spacing = data["spacing"]

        # ASSIGN TEXTURE
        if not brush.texture_slot:
            brush.texture_slot = brush.texture_slots.add()

        brush.texture_slot.texture = tex
        brush.texture_slot.map_mode = "VIEW_PLANE"

        # PREVIEW IMAGE
        preview_img = bpy.data.images.new(name + "_preview", 256, 256)

        preview_source = img.copy()
        preview_source.name = name + "_PreviewSource"
        preview_source.scale(256, 256)

        preview_img.pixels = preview_source.pixels[:]

        preview = brush.preview_ensure()
        preview.image_size = (256, 256)
        preview.image_pixels_float = preview_img.pixels[:]

        # MARK AS ASSET
        brush.asset_mark()
        
        created_brushes.append(data)
        
        print("========================================")
        print("Created asset brush:", name)
        print("========================================")
    except Exception as e:
        print("========================================")
        print("MBFA ERROR while creating brush:", name)
        print("Reason:", e)
        print("Skipping this file.")
        print("========================================")
        failed_brushes.append(data)
        
        
# SAVE ASSET LIBRARY
print("")
print("========================================")
print("Saving asset library...")
print("========================================")
print(asset_file_path)

result = {
    "created": created_brushes,
    "skipped": skipped_brushes,
    "failed": failed_brushes,
}

with open(result_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=0)
    
bpy.ops.wm.save_as_mainfile(filepath=asset_file_path, check_existing=False)

print("")
print("========================================")
print(" MBFA ASSET LIBRARY COMPLETE")
print("========================================")
print("")