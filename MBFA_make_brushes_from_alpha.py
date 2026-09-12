import bpy
import os

extensions = {".jpg", ".jpeg", ".png", ".tif", ".bmp", ".psd"}
bpy.types.Scene.my_folder = bpy.props.StringProperty(name="Folder", subtype="DIR_PATH")


class MBFA_PT_panel(bpy.types.Panel):
    bl_label = "Make Brush From Alpha"
    bl_idname = "MBFA_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MyAddon"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Make Brush From Alpha")
        # label needed
        layout.prop(context.scene, "my_folder")

        # label needed
        layout.operator("mbfa.run")


class MBFA_OT_run(bpy.types.Operator):
    bl_label = "Add Brushes Function"
    bl_idname = "mbfa.run"

    def execute(self, context):
        folder = context.scene.my_folder
        print("Selected folder: ", folder)
        add_brushes_from_alpha(folder)

        return {"FINISHED"}

def add_brushes_from_alpha(folderPath):

    for file in os.listdir(folderPath):
        name, ext = os.path.splitext(file)
        if ext.lower() not in extensions:
            continue

        path = os.path.join(folderPath, file)

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

        print("✔ Created brush + texture + preview:", name)

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


if __name__ == "__main__":
    register()
