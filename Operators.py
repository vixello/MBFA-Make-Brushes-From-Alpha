
import bpy
import os
from .LibraryManager import MBFA_LibraryManager

class MBFA_OT_run(bpy.types.Operator):
    bl_label = "Add Brushes From Alphas"
    bl_idname = "mbfa.run"

    def execute(self, context):
        alpha_folder = context.scene.alpha_folder
        asset_save_folder = context.scene.asset_dir_path
        
        if not alpha_folder or not asset_save_folder:
            self.report({'ERROR'}, "Both folders must be set.")
            return {'CANCELLED'}
       
        asset_file_path = os.path.join(asset_save_folder, context.scene.brushes_blend_file)
        
        MBFA_LibraryManager.ensure_asset_library_exists(asset_file_path)
        result = MBFA_LibraryManager.add_brushes_from_alpha(context, asset_file_path, context.scene.mbfa_alpha_items, False)

        if result is None:
            self.report( {'WARNING'}, "No alpha brushes to create.")
            return {'CANCELLED'}

        self.report( {'INFO'},
            f"Created {len(result['created'])} brushes, "
            f"skipped {len(result['skipped'])} existing brushes."
        )
        return {"FINISHED"}
    
class MBFA_OT_overwrite(bpy.types.Operator):
    bl_label = "Overwrite Selected Brushes Data"
    bl_idname = "mbfa.overwrite"

    def execute(self, context):
        alpha_folder = context.scene.alpha_folder
        asset_save_folder = context.scene.asset_dir_path
        
        if not alpha_folder or not asset_save_folder:
            self.report({'ERROR'}, "Both folders must be set.")
            return {'CANCELLED'}
       
        asset_file_path = os.path.join(asset_save_folder, context.scene.brushes_blend_file)
        
        MBFA_LibraryManager.ensure_asset_library_exists(asset_file_path)
        
        selected_items = []
        
        for item in context.scene.mbfa_skipped_alpha_items:
            for selection in context.scene.mbfa_overwrite_selection:
                if selection.id == item.id and selection.selected:
                    selected_items.append(item)
                    break
                
        result = MBFA_LibraryManager.add_brushes_from_alpha(context, asset_file_path, selected_items, True)

        if result is None:
            self.report({'WARNING'}, "No brushes were selected.")
            return {'CANCELLED'}

        self.report( {'INFO'}, f"Overwritten {len(result['created'])} brushes." )
        return {"FINISHED"}
    
class MBFA_OT_reload_alpha_folder(bpy.types.Operator):
    bl_label = "Reload Alpha Folder"
    bl_idname = "mbfa.reload"
    
    def execute(self, context):
        MBFA_LibraryManager.refresh_alpha_list(context)
        
        self.report({'INFO'}, "Alpha folder reloaded.")
        return {'FINISHED'}
    
class MBFA_OT_set_all_texture_paint(bpy.types.Operator):

    bl_label = "All Texture Paint"
    bl_idname = "mbfa.all_texture_paint"

    def execute(self, context):

        for item in context.scene.mbfa_alpha_items:
            item.texture_paint = True
            item.brush_type = "TEXTURE_PAINT"

        self.report(
            {'INFO'},
            "All brushes set to Texture Paint."
        )

        return {'FINISHED'}
    
class MBFA_OT_set_all_sculpt(bpy.types.Operator):

    bl_label = "All Sculpt"
    bl_idname = "mbfa.all_sculpt"

    def execute(self, context):

        for item in context.scene.mbfa_alpha_items:
            item.texture_paint = False
            item.brush_type = "SCULPT"

        self.report(
            {'INFO'},
            "All brushes set to Sculpt."
        )

        return {'FINISHED'}