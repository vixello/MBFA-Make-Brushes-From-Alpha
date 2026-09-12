import bpy
import os

extensions = {".jpg", ".jpeg", ".png", ".tif", ".bmp", ".psd"}
bpy.types.Scene.my_folder = bpy.props.StringProperty(name="Alpha Folder", subtype="DIR_PATH")
bpy.types.Scene.asset_dir_path = bpy.props.StringProperty(name="Brushes Asset Library Folder", subtype="DIR_PATH")
bpy.types.Scene.brushes_blend_file = bpy.props.StringProperty(
    name="Brushes File",
    description="Name of the .blend file where brushes will be saved",
    default="Brushes.blend"
)



class MBFA_PT_panel(bpy.types.Panel):
    bl_label = "Make Brush From Alpha"
    bl_idname = "MBFA_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MBFA"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False 
        
        layout.label(text="Make Brush From Alpha")
        
        box = layout.box()
        box.label(text="Alpha Folder", icon="FILE_FOLDER")
        box.prop(context.scene, "my_folder",text="")
        
        box = layout.box()
        box.label(text="Brushes Asset Library Folder", icon="ASSET_MANAGER")
        box.prop(context.scene, "asset_dir_path",text="")
        
        box = layout.box()
        box.label(text="Brushes Blend File Name", icon="FILE_BLEND")
        box.prop(context.scene, "brushes_blend_file", text="")

        layout.operator("mbfa.run", icon="BRUSH_DATA")


class MBFA_OT_run(bpy.types.Operator):
    bl_label = "Add Brushes Function"
    bl_idname = "mbfa.run"

    def execute(self, context):
        alpha_folder = context.scene.my_folder
        asset_folder = context.scene.asset_dir_path
        
        if not alpha_folder or not asset_folder:
            self.report({'ERROR'}, "Both folders must be set.")
            return {'CANCELLED'}
       
        asset_file_path = os.path.join(asset_folder, context.scene.brushes_blend_file)
        
        ensure_asset_library_exists(asset_file_path)
        add_brushes_from_alpha(alpha_folder, asset_file_path)

        self.report({'INFO'}, "Brushes added to asset library.")
        return {"FINISHED"}

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
        
def add_brushes_from_alpha(alpha_folder, asset_file_path):
    """Create brushes from alphas and save them into the asset library."""
    
    if not bpy.data.filepath:
        temp_path = os.path.join(bpy.app.tempdir, "default_name.blend")
        bpy.ops.wm.save_mainfile(filepath=temp_path)
        original_file = temp_path
    else:
        original_file = bpy.data.filepath
        
    bpy.ops.wm.open_mainfile(filepath=asset_file_path)

    for file in os.listdir(alpha_folder):
        name, ext = os.path.splitext(file)
        if ext.lower() not in extensions:
            continue

        path = os.path.join(alpha_folder, file)

        # Load image
        img = bpy.data.images.load(path)

        # Create texture
        tex = bpy.data.textures.new(name + "_tex", type="IMAGE")
        tex.image = img

        # Create brush
        brush = bpy.data.brushes.new(name=name)
        brush.use_paint_sculpt = True
        brush.stroke_method = "ANCHORED"

        # --- ASSIGN TEXTURE (Blender 5.1 way) ---
        if not brush.texture_slot:
            brush.texture_slot = brush.texture_slots.add()

        brush.texture_slot.texture = tex
        brush.texture_slot.map_mode = "VIEW_PLANE"  # ← FIXED HERE

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

print("⚠ Now manually mark brushes as assets in the Asset Browser.")
print("⚠ Then save this .blend inside your Asset Library folder.")


classes = (
    MBFA_PT_panel,
    MBFA_OT_run,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
