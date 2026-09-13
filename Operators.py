
import bpy
import os
from .LibraryManager import MBFA_LibraryManager

class MBFA_OT_run(bpy.types.Operator):
    bl_label = "Add Brushes From Alphas"
    bl_idname = "mbfa.run"

    def execute(self, context):
        alpha_folder = context.scene.my_folder
        asset_folder = context.scene.asset_dir_path
        
        if not alpha_folder or not asset_folder:
            self.report({'ERROR'}, "Both folders must be set.")
            return {'CANCELLED'}
       
        asset_file_path = os.path.join(asset_folder, context.scene.brushes_blend_file)
        
        MBFA_LibraryManager.ensure_asset_library_exists(asset_file_path)
        MBFA_LibraryManager.add_brushes_from_alpha(context, alpha_folder, asset_file_path)

        self.report({'INFO'}, "Brushes added to asset library.")
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