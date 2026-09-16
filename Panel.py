import bpy

from .Models import MBFA_AlphaItem, MBFA_BrushCatalogAssignment, MBFA_OverwriteSelection, MBFA_Catalog

from .Operators import (
    MBFA_OT_run,
    MBFA_OT_overwrite,
    MBFA_OT_reload_alpha_folder,
    MBFA_OT_set_all_texture_paint,
    MBFA_OT_set_all_sculpt,
    MBFA_OT_select_all,
    MBFA_OT_reset_props,
    MBFA_OT_assign_catalog,
    MBFA_OT_create_catalog,
    MBFA_OT_rename_catalog,
    MBFA_OT_delete_catalog,
    MBFA_OT_select_deselect_from_catalog,
    MBFA_OT_refresh_catalogs
)
from .LibraryManager import MBFA_UL_alpha_list, MBFA_UL_skipped_alpha_list, MBFA_LibraryManager, MBFA_UL_catalogs
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
        
        layout.operator("mbfa.run", icon="BRUSH_DATA")
        
        # ==========================================================
        # Brush Errors And Update - collapsible section
        # ==========================================================

        box = layout.box()
        
        row = box.row()
        row.scale_y = 1.4
        
        btn = row.row(align=True)
        btn.scale_x = 1.4  
        btn.scale_y = 1.2  

        btn.prop(context.scene, "mbfa_show_errors", text="",
            icon="TRIA_DOWN" if context.scene.mbfa_show_errors else "TRIA_RIGHT",
            emboss=True
        )
        row.label(text="Result")

            
        # New result notification
        # --------------------------------------------------------------------------------------
        if context.scene.mbfa_has_new_results:
            row.label(text="", icon="RECORD_ON")
        else:
            row.label(text="", icon="RECORD_OFF")

        row_innfo = layout.row()
        row_innfo.label(text="No new result info", icon="RECORD_OFF")

        row_innfo = layout.row()
        row_innfo.label(text="New result info", icon="RECORD_ON")

        # Display result info
        # --------------------------------------------------------------------------------------
        if context.scene.mbfa_show_errors:

            content = box.column(align=True)
            
            content.alert = True
            content.label(text=context.scene.mbfa_result_log)
            content.label(text="Conflicting brushes", icon="ERROR")
            content.alert = False
            if len(context.scene.mbfa_skipped_alpha_items) <= 0:
                
                placeholder = box.column(align=True)
                row = placeholder.row()
                row.alignment = "CENTER"
                row.label(text="Nothing to show yet!", icon="INFO")
                
            else:
                content.operator("mbfa.select_all", text="Select all", icon="CHECKBOX_HLT").overwrite = True
                content.template_list("MBFA_UL_skipped_alpha_list", "",
                    context.scene, "mbfa_skipped_alpha_items",
                    context.scene, "mbfa_skipped_alpha_index",
                    rows=8
                )

                row = content.row()
                row.alert = True
                row.operator("mbfa.overwrite", icon="STATUS_WARNING")
                
                MBFA_PanelUtils.show_preview(
                    context.scene.mbfa_skipped_alpha_items,
                    context.scene.mbfa_skipped_alpha_index,
                    box
                )

        # Reset all inputs and addon
        # --------------------------------------------------------------------------------------
        layout.separator()
        layout.operator("mbfa.reset_all", text="Reset all inputs and outputs", icon="FILE_REFRESH")
        
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
        layout.separator()
        
        # Asset catalogs
        # ----------------------------------------------------------
        box = layout.box()
        box.label(text="Asset Catalogs", icon="ASSET_MANAGER")

        row = box.row()
        row.template_list(
            "MBFA_UL_catalogs", "",
            context.scene, "mbfa_catalogs",
            context.scene, "mbfa_catalog_index",
            rows=4
        )

        buttons = row.column(align=True)
        buttons.operator("mbfa.select_deselect_from_catalog", text="", icon="CHECKBOX_HLT")
        buttons.operator("mbfa.create_catalog", text="", icon="ADD")
        buttons.operator("mbfa.rename_catalog", text="", icon="GREASEPENCIL")
        buttons.operator("mbfa.delete_catalog", text="", icon="REMOVE")

        box.row().operator("mbfa.refresh_catalogs", text="Refresh Catalogs", icon="FILE_REFRESH")
        box.row().operator("mbfa.assign_catalog", text="Assign Selected", icon="ASSET_MANAGER")
                    
        # --------------------------------------------------------------------------------------
        
        box = layout.box()
        box.label(text="Alpha Browser", icon="IMAGE_DATA")
        box.operator("mbfa.select_all", text="Select all", icon="CHECKBOX_HLT")

        row = box.row()
        
        row.operator("mbfa.all_texture_paint", text="All Texture Paint", icon="BRUSH_DATA")
        row.operator("mbfa.all_sculpt", text="All Sculpt", icon="SCULPTMODE_HLT")
        
        col = box.column()
        col.template_list( "MBFA_UL_alpha_list", "", context.scene, "mbfa_alpha_items", 
                          context.scene, "mbfa_alpha_index", rows=8)

        # --------------------------------------------------------------------------------------
        MBFA_PanelUtils.show_preview(context.scene.mbfa_alpha_items, context.scene.mbfa_alpha_index, box)


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
    MBFA_BrushCatalogAssignment,
    
    MBFA_Catalog,
    MBFA_UL_alpha_list,
    MBFA_UL_skipped_alpha_list,
    
    MBFA_PT_panel,
    MBFA_OT_run,
    MBFA_OT_overwrite,
    
    MBFA_OT_reload_alpha_folder,
    MBFA_OT_set_all_texture_paint,
    MBFA_OT_set_all_sculpt,
    MBFA_OT_select_all,
    MBFA_OT_reset_props,
    
    MBFA_OT_create_catalog,
    MBFA_OT_rename_catalog,
    MBFA_OT_delete_catalog,
    MBFA_OT_assign_catalog,
    MBFA_UL_catalogs,
    MBFA_OT_select_deselect_from_catalog,
    MBFA_OT_refresh_catalogs
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
        subtype="DIR_PATH",
        update=lambda self, context:
            MBFA_LibraryManager.refresh_catalog_list(context)
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
    
    bpy.types.Scene.mbfa_show_errors = bpy.props.BoolProperty(
        name="Brush Errors And Update",
        default=False
    )
    bpy.types.Scene.mbfa_has_new_results = bpy.props.BoolProperty(
    default=False
    )
    bpy.types.Scene.mbfa_result_log = bpy.props.StringProperty(
        default=""
    )

    bpy.types.Scene.mbfa_catalogs = bpy.props.CollectionProperty(
        type=MBFA_Catalog
    )
    bpy.types.Scene.mbfa_catalog_index = bpy.props.IntProperty()
    
    bpy.types.Scene.mbfa_brush_catalog_assignments = bpy.props.CollectionProperty(
    type=MBFA_BrushCatalogAssignment
)
    
def resetProps(context):
    scene = context.scene

    scene.alpha_folder = ""
    scene.asset_dir_path = ""
    scene.brushes_blend_file = "Brushes.blend"
    scene.mbfa_preview_image = None

    scene.mbfa_alpha_items.clear()
    scene.mbfa_alpha_index = 0

    scene.mbfa_skipped_alpha_items.clear()
    scene.mbfa_skipped_alpha_index = 0

    scene.mbfa_overwrite_selection.clear()

    scene.mbfa_show_errors = False
    scene.mbfa_has_new_results = False
    scene.mbfa_result_log = ""

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
        "mbfa_show_errors",
        "mbfa_has_new_results",
        "mbfa_result_log",
        "mbfa_catalogs",
        "mbfa_catalog_index",
    ):
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)

    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)