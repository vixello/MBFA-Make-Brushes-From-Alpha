import bpy
import os
import bpy.utils.previews
    
extensions = {".jpg", ".jpeg", ".png", ".tif", ".bmp", ".psd"}
    
class MBFA_UL_alpha_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.filename, icon="IMAGE_DATA")


class MBFA_LibraryManager:
    preview_collections = {}

    @staticmethod
    def add_brushes_from_alpha(context, alpha_folder, asset_file_path):
        """Create brushes from alphas and save them into the asset library."""
        
        if not bpy.data.filepath:
            temp_path = os.path.join(bpy.app.tempdir, "default_name.blend")
            bpy.ops.wm.save_mainfile(filepath=temp_path)
            original_file = temp_path
        else:
            original_file = bpy.data.filepath
            
        bpy.ops.wm.open_mainfile(filepath=asset_file_path)

        for item in context.scene.mbfa_alpha_items:
            name = item.brush_name

            # Load image
            img = bpy.data.images.load(item.image_path)

            # Create texture
            tex = bpy.data.textures.new(name + "_tex", type="IMAGE")
            tex.image = img

            # Create brush
            brush = bpy.data.brushes.new(name=name)
            brush.use_paint_sculpt = True
            brush.stroke_method = item.stroke_method
            brush.size = item.size
            brush.strength = item.strength
            brush.spacing = item.spacing
            
            # --- ASSIGN TEXTURE (Blender 5.1 way) ---
            if not brush.texture_slot:
                brush.texture_slot = brush.texture_slots.add()

            brush.texture_slot.texture = tex
            brush.texture_slot.map_mode = "VIEW_PLANE"  

            # --- PREVIEW (Blender requires 256x256) ---
            preview_img = bpy.data.images.new(name + "_preview", 256, 256)

            img.scale(256, 256)
            preview_img.pixels = img.pixels[:]

            preview = brush.preview_ensure()
            preview.image_size = (256, 256)
            preview.image_pixels_float = preview_img.pixels[:]


            # Mark as asset
            brush.asset_mark()
            print("✔ Created brush + texture + preview:", name)

        # Save asset library
        bpy.ops.wm.save_mainfile(filepath=asset_file_path)

        # Return to original file
        if original_file:
            bpy.ops.wm.open_mainfile(filepath=original_file)
        
    @staticmethod    
    def ensure_asset_library_exists(asset_file_path):
        """Create empty asset library file if missing."""
        
        if os.path.exists(asset_file_path):
            return

        print("Asset library does not exist. Creating:", asset_file_path)
        original_file = bpy.data.filepath
        
        bpy.data.filepath

        # Open empty Blender file
        bpy.ops.wm.read_homefile(use_empty=True)

        # Save empty file as asset library
        bpy.ops.wm.save_mainfile(filepath=asset_file_path)

        # Return to original file (if it exists)
        if original_file:
            bpy.ops.wm.open_mainfile(filepath=original_file)

        print("✔ Created empty asset library:", asset_file_path)
        
    @staticmethod    
    def refresh_alpha_list(context):
        scene = context.scene
        scene.mbfa_alpha_items.clear()
        MBFA_LibraryManager.unregisterAlphaPreviews()
        
        folder = scene.my_folder
        if not folder or not os.path.isdir(folder):
            return

        for file in os.listdir(folder):
            name, ext = os.path.splitext(file)
            if ext.lower() in extensions:
                item = scene.mbfa_alpha_items.add()
                item.filename = file
                item.stroke_method = "ANCHORED"   # default
                item.image_path = os.path.join(folder, file)
                item.brush_name = name
                
                item.size = 100
                item.strength = 0.5
                item.spacing = 10
                item.invert_alpha = False
                MBFA_LibraryManager.registerAlphaPreviews(item)
                
    @staticmethod
    def registerAlphaPreviews(item):
        pcoll = bpy.utils.previews.new()
        
        # path to the folder where the icon is
        # the path is calculated relative to this py file inside the addon folder
        pcoll.load(item.filename, item.image_path, 'IMAGE')
        MBFA_LibraryManager.preview_collections[item.filename] = pcoll

    @staticmethod
    def unregisterAlphaPreviews():
        for pcoll in MBFA_LibraryManager.preview_collections.values():
            bpy.utils.previews.remove(pcoll)
            
        MBFA_LibraryManager.preview_collections.clear()
        
    #print("⚠ Now manually mark brushes as assets in the Asset Browser.")
    #print("⚠ Then save this .blend inside your Asset Library folder.")
