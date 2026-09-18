
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
            context.scene.mbfa_result_log = "No alpha brushes to create."
            return {'CANCELLED'}

        self.report( {'INFO'},
            f"Created {len(result['created'])} brushes, "
            f"skipped {len(result['skipped'])} existing brushes."
        )
        context.scene.mbfa_result_log = f"{len(result['skipped'])} brushes have conflicts."
        context.scene.mbfa_has_new_results = True
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
    
class MBFA_OT_select_all(bpy.types.Operator):

    bl_label = "Select all"
    bl_idname = "mbfa.select_all"
    
    overwrite: bpy.props.BoolProperty(
        default=False
    )
    
    def execute(self, context):

        if self.overwrite:
            for selection in context.scene.mbfa_overwrite_selection:
                selection.selected = not selection.selected

            self.report(
                {'INFO'},
                "All brushes selected to be overwritten."
            )
        else:
            for item in context.scene.mbfa_alpha_items:
                item.selected = not item.selected

        return {'FINISHED'}
    
class MBFA_OT_reset_props(bpy.types.Operator):
    bl_label = "Reset All Inputs"
    bl_idname = "mbfa.reset_all"
    
    def execute(Self, context):
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
        
        return {'FINISHED'}
        
class MBFA_OT_create_catalog(bpy.types.Operator):

    bl_label = "Create Catalog"
    bl_idname = "mbfa.create_catalog"

    name: bpy.props.StringProperty(name="Catalog Name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        success, result = MBFA_LibraryManager.create_catalog(context, self.name)

        if not success:
            self.report({'ERROR'}, result)
            return {'CANCELLED'}

        self.report(
            {'INFO'},
            f"Created catalog: {self.name}"
        )

        return {'FINISHED'}
    
class MBFA_OT_rename_catalog(bpy.types.Operator):

    bl_label = "Rename Catalog"
    bl_idname = "mbfa.rename_catalog"

    name: bpy.props.StringProperty(name="New Name")

    def invoke(self, context, event):

        catalogs = context.scene.mbfa_catalogs

        if not catalogs:
            return {'CANCELLED'}

        catalog = catalogs[context.scene.mbfa_catalog_index]

        self.name = catalog.name

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        catalogs = context.scene.mbfa_catalogs

        if not catalogs:
            return {'CANCELLED'}

        catalog = catalogs[context.scene.mbfa_catalog_index]

        success, message = MBFA_LibraryManager.rename_catalog(
            context,
            catalog,
            self.name
        )

        if not success:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        self.report({'INFO'}, "Catalog renamed.")

        return {'FINISHED'}
    
class MBFA_OT_delete_catalog(bpy.types.Operator):

    bl_label = "Delete Catalog"
    bl_idname = "mbfa.delete_catalog"

    def execute(self, context):

        catalogs = context.scene.mbfa_catalogs

        if not catalogs:
            return {'CANCELLED'}

        index = context.scene.mbfa_catalog_index
        catalog = catalogs[index]

        success, message = MBFA_LibraryManager.delete_catalog(context, catalog)

        if not success:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        self.report(
            {'INFO'},
            "Catalog deleted."
        )

        return {'FINISHED'}
    
class MBFA_OT_assign_catalog(bpy.types.Operator):
    bl_label = "Assign Selected"
    bl_idname = "mbfa.assign_catalog"

    def execute(self, context):
        scene = context.scene
        catalogs = scene.mbfa_catalogs
        if not catalogs: self.report({'ERROR'}, "No catalogs available."); return {'CANCELLED'}

        idx = scene.mbfa_catalog_index
        if idx < 0 or idx >= len(catalogs): self.report({'ERROR'}, "No catalog selected."); return {'CANCELLED'}

        catalog = catalogs[idx]
        selected_items = [item for item in scene.mbfa_alpha_items if item.selected]
        if not selected_items: self.report({'ERROR'}, "No brushes selected."); return {'CANCELLED'}

        result = MBFA_LibraryManager.assign_catalog(context, selected_items, catalog.uuid)
        assigned = result.get("assigned", []); missing = result.get("missing", []); failed = result.get("failed", [])
        
        if failed:
            details = []

            for failure in failed:
                if isinstance(failure, dict):
                    details.append(f"{failure.get('name', 'Unknown')}: {failure.get('error', 'Unknown error')}")
                else:
                    details.append(str(failure))

            self.report({'ERROR'}, f"Catalog assignment failed: {' | '.join(details)[:250]}")
        if assigned: 
            self.report({'INFO'}, f"Assigned {len(assigned)} brush(es) to '{catalog.name}'.")
        if missing: 
            self.report({'WARNING'}, f"{len(missing)} brush(es) were not found.")
        
        if not assigned and not missing and not failed: 
            self.report({'WARNING'}, "Nothing was assigned.")

        return {'FINISHED'}
    
class MBFA_OT_unassign_catalog(bpy.types.Operator):
    bl_label = "Unassign Selected"
    bl_idname = "mbfa.unassign_catalog"

    def execute(self, context):
        scene = context.scene
        catalogs = scene.mbfa_catalogs
        if not catalogs: self.report({'ERROR'}, "No catalogs available."); return {'CANCELLED'}

        idx = scene.mbfa_catalog_index
        if idx < 0 or idx >= len(catalogs): self.report({'ERROR'}, "No catalog selected."); return {'CANCELLED'}

        catalog = catalogs[idx]
        selected_items = [item for item in scene.mbfa_alpha_items if item.selected]
        if not selected_items: self.report({'ERROR'}, "No brushes selected."); return {'CANCELLED'}

        result = MBFA_LibraryManager.unassign_catalog(context, selected_items, catalog.uuid)
        unassigned = result.get("unassigned", []); missing = result.get("missing", []); failed = result.get("failed", [])
        
        if failed:
            details = []

            for failure in failed:
                if isinstance(failure, dict):
                    details.append(f"{failure.get('name', 'Unknown')}: {failure.get('error', 'Unknown error')}")
                else:
                    details.append(str(failure))

            self.report({'ERROR'}, f"Catalog unassignment failed: {' | '.join(details)[:250]}")
        if unassigned: 
            self.report({'INFO'}, f"Unassigned {len(unassigned)} brush(es) from '{catalog.name}'.")
        if missing: 
            self.report({'WARNING'}, f"{len(missing)} brush(es) were not found.")
        
        if not unassigned and not missing and not failed: 
            self.report({'WARNING'}, "Nothing was unassigned.")

        return {'FINISHED'}
    
class MBFA_OT_select_deselect_from_catalog(bpy.types.Operator):
    bl_label = "Select/deselect from catalog"
    bl_idname = "mbfa.select_deselect_from_catalog"
    
    def execute(self, context):
        MBFA_LibraryManager.select_brushes_in_catalog(context)
        return {'FINISHED'}
    
class MBFA_OT_refresh_catalogs(bpy.types.Operator):
    bl_label = "Refresh catalogs"
    bl_idname = "mbfa.refresh_catalogs"
    bl_description = "Discard staged catalog changes and reload the committed catalogs from disk."
    
    def execute(self, context):
        MBFA_LibraryManager.refresh_catalog_list(context)
        MBFA_LibraryManager.refresh_brush_catalog_assignments(context)
        return {'FINISHED'}
    
       
    