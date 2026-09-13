import bpy

from .Models import MBFA_AlphaItem
from .Operators import MBFA_OT_run, MBFA_OT_reload_alpha_folder
from .LibraryManager import MBFA_UL_alpha_list, MBFA_LibraryManager
import os

class MBFA_PT_panel(bpy.types.Panel):
    bl_label = "Make Brush From Alpha"
    bl_idname = "MBFA_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MBFA"

    def draw(self, context):
        layout = self.layout
        
        if not hasattr(context.scene, "mbfa_alpha_items"):
            layout.label(text="MBFA not initialized yet")
            return
        layout.use_property_split = True
        layout.use_property_decorate = False 
        
        layout.label(text="Make Brush From Alpha")
        layout.operator("mbfa.run", icon="BRUSH_DATA")
        
        box = layout.box()
        box.label(text="Alpha Folder", icon="FILE_FOLDER")
        box.prop(context.scene, "my_folder",text="")
        
        layout.operator("mbfa.reload", icon="FILE_REFRESH")
        
        box = layout.box()
        box.label(text="Brushes Asset Library Folder", icon="ASSET_MANAGER")
        box.prop(context.scene, "asset_dir_path",text="")
        
        box = layout.box()
        box.label(text="Brushes Blend File Name", icon="FILE_BLEND")
        box.prop(context.scene, "brushes_blend_file", text="")

        box = layout.box()
        box.label(text="Alpha Browser", icon="IMAGE_DATA")

        row = box.row()
        row.template_list("MBFA_UL_alpha_list", "", context.scene, "mbfa_alpha_items", 
                          context.scene, "mbfa_alpha_index", rows=8)

        if context.scene.mbfa_alpha_items:
            item = context.scene.mbfa_alpha_items[context.scene.mbfa_alpha_index]

            preview_box = box.box()
            preview_col = preview_box.column(align=True)

            row = preview_col.row()
            row.alignment = "CENTER"
            row.label(text="Preview")

            row = preview_col.row()
            row.alignment = "CENTER"
            row.label(text=item.filename)
            
            try:
                pcoll = MBFA_LibraryManager.preview_collections[item.filename]
                my_icon = pcoll[item.filename]

                row = preview_col.row()
                row.alignment = "CENTER"
                row.template_icon(my_icon.icon_id, scale=8)

            except:
                row = preview_col.row()
                row.alignment = "CENTER"
                row.label(text="Cannot load preview", icon="ERROR")

                row = preview_col.row()
                row.alignment = "CENTER"
                row.label(text="Please add or reload the alpha folder")
                
            stroke_method_box = box.box()
            
            stroke_method_box.label(text="Brush settings")
                        
            stroke_method_box.label(text="Brush name")
            stroke_method_box.prop(item, "brush_name", text="")
            
            stroke_method_box.label(text="Stroke method")
            stroke_method_box.prop(item, "stroke_method", text="")

            row = stroke_method_box.row()
            row.use_property_split = False
            row.prop(item, "size", text="Size")

            row = stroke_method_box.row()
            row.use_property_split = False
            row.prop(item, "strength", text="Strength")

            row = stroke_method_box.row()
            row.use_property_split = False
            row.prop(item, "spacing", text="Spacing")
                        


classes = (
    MBFA_AlphaItem,
    MBFA_UL_alpha_list,
    MBFA_PT_panel,
    MBFA_OT_run,
    MBFA_OT_reload_alpha_folder
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.my_folder = bpy.props.StringProperty(
        name="Alpha Folder", 
        subtype="DIR_PATH", 
        update=lambda self, 
        context: MBFA_LibraryManager.refresh_alpha_list(context)
        )
    bpy.types.Scene.asset_dir_path = bpy.props.StringProperty(
        name="Brushes Asset Library Folder", 
        subtype="DIR_PATH"
        )
    bpy.types.Scene.brushes_blend_file = bpy.props.StringProperty(
        name="Brushes File",
        description="Name of the .blend file where brushes will be saved",
        default="Brushes.blend"
        )
    bpy.types.Scene.mbfa_preview_image = bpy.props.PointerProperty(type=bpy.types.Image)
   
    bpy.types.Scene.mbfa_alpha_items = bpy.props.CollectionProperty(type=MBFA_AlphaItem)
    bpy.types.Scene.mbfa_alpha_index = bpy.props.IntProperty()


def unregister():

    MBFA_LibraryManager.unregisterAlphaPreviews()

    for prop in (
        "my_folder",
        "asset_dir_path",
        "brushes_blend_file",
        "mbfa_preview_image",
        "mbfa_alpha_items",
        "mbfa_alpha_index",
    ):
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)

    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)