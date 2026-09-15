import bpy

from .Models import MBFA_AlphaItem, MBFA_OverwriteSelection
from .Operators import MBFA_OT_run, MBFA_OT_reload_alpha_folder, MBFA_OT_set_all_texture_paint, MBFA_OT_set_all_sculpt
from .LibraryManager import MBFA_UL_alpha_list, MBFA_UL_skipped_alpha_list, MBFA_LibraryManager
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
        # --------------------------------------------------------------------------------------
        layout.label(text="Brush Errors and Update")
    
        # --------------------------------------------------------------------------------------
        
        box = layout.box()
        box.label(text="Alpha Folder", icon="FILE_FOLDER")
        box.prop(context.scene, "alpha_folder",text="")
        
        layout.operator("mbfa.reload", icon="FILE_REFRESH")
        
        box = layout.box()
        box.label(text="Brushes Asset Library Folder", icon="ASSET_MANAGER")
        box.prop(context.scene, "asset_dir_path",text="")
        
        box = layout.box()
        box.label(text="Brushes Blend File Name", icon="FILE_BLEND")
        box.prop(context.scene, "brushes_blend_file", text="")

        # --------------------------------------------------------------------------------------
        
        box = layout.box()
        box.label(text="Alpha Browser", icon="IMAGE_DATA")

        row = box.row()
        
        row.operator("mbfa.all_texture_paint", text="All Texture Paint", icon="BRUSH_DATA")
        row.operator("mbfa.all_sculpt", text="All Sculpt", icon="SCULPTMODE_HLT")
        
        col = box.column()
        col.template_list( "MBFA_UL_alpha_list", "", context.scene, "mbfa_alpha_items", 
                          context.scene, "mbfa_alpha_index", rows=8)

        # --------------------------------------------------------------------------------------
        MBFA_PanelUtils.show_preview(context.scene.mbfa_alpha_items, context.scene.mbfa_alpha_index, box)

class MBFA_PT_BrushErrorsAndUpdate(bpy.types.Panel):
    bl_label = "Brush Errors And Update"
    bl_idname = "MBFA_PT_BrushErrorsAndUpdate"
    bl_parent_id = "MBFA_PT_panel" 
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MBFA"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        col = box.column()
        col.template_list( "MBFA_UL_skipped_alpha_list", "", context.scene, "mbfa_skipped_alpha_items", 
                          context.scene, "mbfa_skipped_alpha_index", rows=8)
        layout.alert = True
        layout.operator("mbfa.overwrite", icon="STATUS_WARNING")
        layout.alert = False

        MBFA_PanelUtils.show_preview(context.scene.mbfa_skipped_alpha_items, context.scene.mbfa_skipped_alpha_index, box)

class MBFA_PanelUtils:
    @staticmethod
    def show_preview(items, index, parentBox):
        if items:
            item = items[index]

            preview_box = parentBox.box()
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
                
            stroke_method_box = parentBox.box()
            
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
    MBFA_OverwriteSelection,
    MBFA_UL_alpha_list,
    MBFA_UL_skipped_alpha_list,
    MBFA_PT_panel,
    MBFA_PT_BrushErrorsAndUpdate,
    MBFA_OT_run,
    MBFA_OT_reload_alpha_folder,
    MBFA_OT_set_all_texture_paint,
    MBFA_OT_set_all_sculpt
)
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.alpha_folder = bpy.props.StringProperty(
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
    bpy.types.Scene.mbfa_skipped_alpha_items = bpy.props.CollectionProperty(type=MBFA_AlphaItem)
    bpy.types.Scene.mbfa_skipped_alpha_index = bpy.props.IntProperty()
    
    bpy.types.Scene.mbfa_overwrite_selection = bpy.props.CollectionProperty(
        type=MBFA_OverwriteSelection
    )

def unregister():

    MBFA_LibraryManager.unregisterAlphaPreviews()

    for prop in (
        "alpha_folder",
        "asset_dir_path",
        "brushes_blend_file",
        "mbfa_preview_image",
        "mbfa_alpha_items",
        "mbfa_alpha_index",
        "mbfa_skipped_alpha_items",
        "mbfa_skipped_alpha_index",
        "mbfa_overwrite_selection",
    ):
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)

    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)