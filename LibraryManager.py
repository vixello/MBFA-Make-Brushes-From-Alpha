import bpy
import os
import json
import tempfile
import subprocess
import bpy.utils.previews
import textwrap
import hashlib
import uuid

extensions = {".jpg", ".jpeg", ".png", ".tif", ".bmp", ".psd"}


class MBFA_UL_alpha_list(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):

        layout.use_property_split = False
        layout.use_property_decorate = False

        row = layout.row(align=True)

        row.prop(item, "selected", text="")
        row.separator(factor=0.5)
        row.prop(item, "texture_paint", text="", toggle=True)
        row.label(text=item.filename, icon="IMAGE_DATA")
        
class MBFA_UL_skipped_alpha_list(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        row = layout.row(align = True)
        
        selection = None
                
        for entry in context.scene.mbfa_overwrite_selection:
            if entry.id == item.id:
                selection = entry
                break
        if selection:
            row.prop(selection, "selected", text="")
        layout.label(text=item.filename, icon="IMAGE_DATA")
        
class MBFA_UL_catalogs(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name, icon="ASSET_MANAGER")

class MBFA_LibraryManager:

    preview_collections = {}

    # CREATE / UPDATE BRUSHES
    # ---------------------------------------------------------
    @staticmethod
    def add_brushes_from_alpha(context, asset_file_path, items, overwrite = False):
        """
        Creates/updates brushes inside Brushes.blend.

        IMPORTANT:
        The user's currently open .blend is NEVER opened,
        saved, replaced, or switched away from.

        A separate background Blender process is launched to
        create/update the asset library.
        """

        # -----------------------------------------------------
        # 1. COPY ALL SETTINGS FROM CURRENT BLENDER
        # -----------------------------------------------------

        alpha_items = []

        for item in items:

            alpha_items.append({
                "id": item.id,
                "filename": item.filename,
                "image_path": os.path.abspath(item.image_path),
                "brush_name": item.brush_name,
                "texture_paint": item.texture_paint,
                "stroke_method": item.stroke_method,
                "size": item.size,
                "strength": item.strength,
                "spacing": item.spacing,
                "invert_alpha": item.invert_alpha,
            })

        if not alpha_items:
            print("MBFA: No alpha brushes to create.")
            return

        # 2. PREPARE DESTINATION
        asset_file_path = os.path.abspath(asset_file_path)
        asset_save_folder = os.path.dirname(asset_file_path)

        if asset_save_folder and not os.path.exists(asset_save_folder):
            os.makedirs(asset_save_folder)


        # 3. CREATE TEMPORARY WORK DIRECTORY
        temp_dir = tempfile.mkdtemp(prefix="MBFA_")
        addon_dir = os.path.dirname(__file__)
        
        settings_path = os.path.join(temp_dir, "mbfa_settings.json")
        result_path = os.path.join(temp_dir, "mbfa_result.json")
        external_script_path  = os.path.join(addon_dir, "mbfa_background_create_brushes.py")
        
        # 4. WRITE SETTINGS JSON
        settings = {
            "asset_file_path": asset_file_path,
            "items": alpha_items,
            "result_path": result_path,
            "overwrite" : overwrite
        }

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

        # 5. BACKGROUND BLENDER SCRIPT
        with open(external_script_path , "r", encoding="utf-8") as f: 
            script = f.read()

        # 6. FIND CURRENT BLENDER EXECUTABLE
        blender_executable = bpy.app.binary_path

        # 7. START SECOND BLENDER PROCESS
        command = [
            blender_executable,
            "--background",
            "--python",
            external_script_path ,
            "--",
            settings_path,
        ]

        print("")
        print("========================================")
        print(" MBFA: Starting background Blender")
        print("========================================")
        print("")

        print(" ".join(command))

        try:
            result = subprocess.run(command, check=True)
            scene = context.scene
            
            created = []
            skipped = []
            failed = []
            
            if os.path.exists(result_path):
                with open(result_path, "r", encoding="utf-8") as f:
                    result_data = json.load(f)
                    
                created = result_data.get("created", [])
                skipped = result_data.get("skipped", [])
                failed = result_data.get("failed", [])
                
                if len(created) > 0:
                    print("")
                    print("========================================")
                    print("MBFA: Brushes were created.")
                    print("MBFA: Committing staged catalogs.")
                    print("========================================")

                    catalog_success, catalog_error = (MBFA_LibraryManager.commit_catalogs(context))

                    if not catalog_success:
                        failed.append({"error": f"Catalog commit failed: {catalog_error}"})

                else:
                    print("")
                    print("========================================")
                    print("MBFA: No brushes were created.")
                    print("MBFA: Catalog changes NOT committed.")
                    print("MBFA: Asset catalog file remains untouched.")
                    print("========================================")
                    
            scene.mbfa_skipped_alpha_items.clear()
            scene.mbfa_overwrite_selection.clear()

            for data in skipped:

                item = scene.mbfa_skipped_alpha_items.add()

                item.id = data["id"]
                item.filename = data["filename"]
                item.image_path = data["image_path"]
                item.brush_name = data["brush_name"]
                item.texture_paint = data["texture_paint"]
                item.stroke_method = data["stroke_method"]
                item.size = data["size"]
                item.strength = data["strength"]
                item.spacing = data["spacing"]
                item.invert_alpha = data["invert_alpha"]

                selection = scene.mbfa_overwrite_selection.add()
                selection.id = data["id"]
                selection.selected = False
                
            print("")
            print("========================================")
            print("MBFA: Background Blender finished successfully.")

        except subprocess.CalledProcessError as e:
            print("")
            print("========================================")
            print("MBFA ERROR: Asset library generation failed.")

            print("Blender return code:",e.returncode)

            return


        finally:

            # CLEAN TEMP FILES
            try:
                os.remove(settings_path)
            except OSError:
                pass

            try:
                os.rmdir(temp_dir)
            except OSError:
                pass


        print("")
        print("========================================")
        print(" MBFA COMPLETE")
        print("========================================")
        print("")
        print("Brush library:", asset_file_path)
        
        return {
            "created": created,
            "skipped": skipped,
            "failed": failed,
        }

    # ASSET LIBRARY PATH
    # ---------------------------------------------------------
    @staticmethod
    def ensure_asset_library_exists(asset_file_path):
        """
        Only make sure the destination folder exists.

        We DO NOT create/open/save a Blender file here.
        The background Blender process handles that.
        """

        asset_file_path = os.path.abspath(asset_file_path)

        asset_save_folder = os.path.dirname(asset_file_path)

        if (asset_save_folder and not os.path.exists(asset_save_folder)):
            os.makedirs(asset_save_folder)

        if os.path.exists(asset_file_path):
            print("MBFA: Asset library already exists:", asset_file_path)

        else:
            print("MBFA: Asset library will be created:", asset_file_path)

    @staticmethod
    def refresh_alpha_list(context):
        scene = context.scene
        
        existing_settings = {}

        for item in scene.mbfa_alpha_items:
            existing_settings[item.id] = {
                "stroke_method": item.stroke_method,
                "texture_paint": item.texture_paint,
                "brush_name": item.brush_name,
                "size": item.size,
                "strength": item.strength,
                "spacing": item.spacing,
                "invert_alpha": item.invert_alpha,
            }
            
        scene.mbfa_alpha_items.clear()

        MBFA_LibraryManager.unregisterAlphaPreviews()

        folder = scene.alpha_folder

        if not folder:
            return

        if not os.path.isdir(folder):
            return

        for file in os.listdir(folder):
            name, ext = os.path.splitext(file)

            if ext.lower() not in extensions:
                continue
            
            image_path = os.path.join(folder, file)
            with open(image_path, "rb") as f:
                item_id = hashlib.sha1(f.read()).hexdigest()

            item = scene.mbfa_alpha_items.add()
            
            item.filename = file
            item.image_path = image_path
            item.id = item_id
            
            prev = existing_settings.get(item_id)
            
            if prev:
                item.stroke_method = prev["stroke_method"]
                item.texture_paint = prev["texture_paint"]
                item.brush_name = prev["brush_name"]
                item.size = prev["size"]
                item.strength = prev["strength"]
                item.spacing = prev["spacing"]
                item.invert_alpha = prev["invert_alpha"]
            else:
                item.stroke_method = "ANCHORED"
                item.texture_paint = False
                item.brush_name = name
                item.size = 100
                item.strength = 0.5
                item.spacing = 10
                item.invert_alpha = False

            MBFA_LibraryManager.registerAlphaPreviews(item)

    @staticmethod
    def registerAlphaPreviews(item):

        pcoll = bpy.utils.previews.new()
        pcoll.load(item.filename, item.image_path,'IMAGE')

        MBFA_LibraryManager.preview_collections[item.filename] = pcoll

    @staticmethod
    def unregisterAlphaPreviews():

        for pcoll in (MBFA_LibraryManager.preview_collections.values()):
            bpy.utils.previews.remove(pcoll)

        MBFA_LibraryManager.preview_collections.clear()
        
        # ---------------------------------------------------------
    # ASSET CATALOGS
    # ---------------------------------------------------------

    @staticmethod
    def get_catalog_file(asset_dir_path):
        return os.path.join(
            os.path.abspath(asset_dir_path),
            "blender_assets.cats.txt"
        )


    @staticmethod
    def load_catalogs(asset_dir_path):
        catalog_file = MBFA_LibraryManager.get_catalog_file(asset_dir_path)

        catalogs = []

        if not os.path.exists(catalog_file):
            return catalogs

        with open(catalog_file, "r", encoding="utf-8") as f:

            for line in f:
                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                if line == "VERSION 1":
                    continue

                parts = line.split(":", 2)

                if len(parts) != 3:
                    continue

                catalog_uuid, catalog_path, catalog_name = parts

                catalogs.append({
                    "uuid": catalog_uuid,
                    "path": catalog_path,
                    "name": catalog_name,
                })

        return catalogs


    @staticmethod
    def save_catalogs(asset_dir_path, catalogs):

        asset_dir_path = os.path.abspath(asset_dir_path)

        if not os.path.exists(asset_dir_path):
            os.makedirs(asset_dir_path)

        catalog_file = MBFA_LibraryManager.get_catalog_file(asset_dir_path)

        with open(catalog_file, "w", encoding="utf-8") as f:

            f.write("# This is an Asset Catalog Definition file for MBFA.\n")
            f.write("#\n")
            f.write("# UUID:catalog/path:simple catalog name\n")
            f.write("\n")
            f.write("VERSION 1\n")

            for catalog in catalogs:
                f.write(
                    f"{catalog['uuid']}:{catalog['path']}:{catalog['name']}\n"
                )

    @staticmethod
    def refresh_catalog_list(context):

        scene = context.scene

        scene.mbfa_catalogs.clear()

        asset_dir = scene.asset_dir_path

        if not asset_dir:
            return

        catalogs = MBFA_LibraryManager.load_catalogs(asset_dir)

        for data in catalogs:

            catalog = scene.mbfa_catalogs.add()

            catalog.name = data["name"]
            catalog.uuid = data["uuid"]
            catalog.path = data["path"]

        if scene.mbfa_catalogs:
            scene.mbfa_catalog_index = min(
                scene.mbfa_catalog_index,
                len(scene.mbfa_catalogs) - 1
            )
        else:
            scene.mbfa_catalog_index = 0
                
    @staticmethod
    def create_catalog(context, name):

        name = name.strip()

        if not name:
            return False, "Catalog name cannot be empty."

        scene = context.scene
        asset_dir = scene.asset_dir_path

        if not asset_dir:
            return False, "Set the asset library folder first."

        # Use the catalogs currently displayed in the UI.
        # Do NOT reload from disk and do NOT save to disk here.
        catalogs = [
            {
                "uuid": catalog.uuid,
                "path": catalog.path,
                "name": catalog.name,
            }
            for catalog in scene.mbfa_catalogs
        ]

        for catalog in catalogs:
            if catalog["name"].lower() == name.lower():
                return False, "A catalog with that name already exists."

        new_catalog = {
            "uuid": str(uuid.uuid4()),
            "path": name,
            "name": name,
        }

        catalog = scene.mbfa_catalogs.add()
        catalog.name = new_catalog["name"]
        catalog.uuid = new_catalog["uuid"]
        catalog.path = new_catalog["path"]

        scene.mbfa_catalog_index = len(scene.mbfa_catalogs) - 1

        print("MBFA: Catalog staged:", new_catalog["name"], new_catalog["uuid"])

        return True, new_catalog["uuid"]
    @staticmethod
    def rename_catalog(context, catalog, new_name):

        new_name = new_name.strip()

        if not new_name:
            return False, "Catalog name cannot be empty."

        scene = context.scene

        # Check against currently staged catalogs.
        for entry in scene.mbfa_catalogs:

            if entry.uuid == catalog.uuid:
                continue

            if entry.name.lower() == new_name.lower():
                return False, "A catalog with that name already exists."

        catalog.name = new_name
        catalog.path = new_name

        print("MBFA: Catalog rename staged:", catalog.uuid, "->", new_name)

        return True, ""
    
    @staticmethod
    def delete_catalog(context, catalog):

        scene = context.scene

        index = -1

        for i, entry in enumerate(scene.mbfa_catalogs):
            if entry.uuid == catalog.uuid:
                index = i
                break

        if index == -1:
            return False, "Catalog not found."

        print("MBFA: Catalog deletion staged:", catalog.name, catalog.uuid)

        scene.mbfa_catalogs.remove(index)

        if scene.mbfa_catalogs:
            scene.mbfa_catalog_index = min(
                scene.mbfa_catalog_index,
                len(scene.mbfa_catalogs) - 1
            )
        else:
            scene.mbfa_catalog_index = 0

        return True, ""   
    
    @staticmethod
    def get_staged_catalogs(context):
        scene = context.scene

        return [{
            "uuid": catalog.uuid,
            "path": catalog.path,
            "name": catalog.name,
            
        } for catalog in scene.mbfa_catalogs]

    @staticmethod
    def commit_catalogs(context):
        
        asset_dir = context.scene.asset_dir_path
        
        if not asset_dir:
            return False, "Asset library folder is not set."

        catalogs = MBFA_LibraryManager.get_staged_catalogs(context)
        MBFA_LibraryManager.save_catalogs(asset_dir, catalogs)
        
        print("MBFA: Committed", len(catalogs), "catalog(s) to blender_assets.cats.txt")

        return True, ""
    
    @staticmethod
    def assign_catalog(context, items, catalog_uuid):
        scene = context.scene

        asset_save_folder = scene.asset_dir_path

        if not asset_save_folder:
            return {
                "assigned": [],
                "missing": [],
                "failed": ["Asset library folder is not set."]
            }

        asset_file_path = os.path.join(
            asset_save_folder,
            scene.brushes_blend_file
        )

        if not os.path.exists(asset_file_path):
            return {
                "assigned": [],
                "missing": [],
                "failed": ["Asset library file does not exist."]
            }

        brush_names = []

        for item in items:
            if item.selected:
                brush_names.append(item.brush_name)

        if not brush_names:
            return {
                "assigned": [],
                "missing": [],
                "failed": ["No brushes selected."]
            }

        external_script_path = os.path.join(
            os.path.dirname(__file__),
            "mbfa_background_assign_catalog.py"
        )

        result_path = os.path.join(
            tempfile.gettempdir(),
            "mbfa_assign_catalog_result.json"
        )

        settings_path = os.path.join(
            tempfile.gettempdir(),
            "mbfa_assign_catalog_settings.json"
        )

        settings = {
            "asset_file_path": os.path.abspath(asset_file_path),
            "result_path": result_path,
            "brush_names": brush_names,
            "catalog_uuid": catalog_uuid,
        }

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

        blender_executable = bpy.app.binary_path

        command = [
            blender_executable,
            "--background",
            "--python",
            external_script_path,
            "--",
            settings_path,
        ]

        try:
            subprocess.run(
                command,
                check=True
            )
        except subprocess.CalledProcessError as e:
            return {
                "assigned": [],
                "missing": [],
                "failed": [f"Background Blender failed: {e}"]
            }

        if not os.path.exists(result_path):
            return {
                "assigned": [],
                "missing": [],
                "failed": ["No result returned from background Blender."]
            }

        try:
            with open(result_path, "r", encoding="utf-8") as f:
                result = json.load(f)
        except Exception as e:
            return {
                "assigned": [],
                "missing": [],
                "failed": [f"Could not read assignment result: {e}"]
            }
            
        if result.get("assigned"):
            MBFA_LibraryManager.refresh_brush_catalog_assignments(context)

        return result
    
    @staticmethod
    def unassign_catalog(context, items, catalog_uuid):
        scene = context.scene

        asset_save_folder = scene.asset_dir_path

        if not asset_save_folder:
            return {
                "unassigned": [],
                "missing": [],
                "failed": ["Asset library folder is not set."]
            }

        asset_file_path = os.path.join(
            asset_save_folder,
            scene.brushes_blend_file
        )

        asset_file_path = os.path.abspath(asset_file_path)

        if not os.path.exists(asset_file_path):
            return {
                "unassigned": [],
                "missing": [],
                "failed": ["Asset library file does not exist."]
            }

        brush_names = []

        for item in items:
            if item.selected:
                brush_names.append(item.brush_name)

        if not brush_names:
            return {
                "unassigned": [],
                "missing": [],
                "failed": ["No brushes selected."]
            }

        external_script_path = os.path.join(
            os.path.dirname(__file__),
            "mbfa_background_unassign_catalog.py"
        )

        # Temporary working directory
        # ---------------------------------------------------------
        temp_dir = tempfile.mkdtemp(
            prefix="MBFA_unassign_catalog_"
        )

        settings_path = os.path.join(
            temp_dir,
            "settings.json"
        )

        result_path = os.path.join(
            temp_dir,
            "result.json"
        )

        settings = {
            "asset_file_path": asset_file_path,
            "result_path": result_path,
            "brush_names": brush_names,
            "catalog_uuid": catalog_uuid
        }

        try:

            # Write settings
            # -----------------------------------------------------
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)

            blender_executable = bpy.app.binary_path

            command = [
                blender_executable,
                "--background",
                "--python",
                external_script_path,
                "--",
                settings_path,
            ]

            print("")
            print("========================================")
            print("MBFA: Starting background Blender")
            print("========================================")
            print("Command:")
            print(" ".join(command))
            print("")

            # Run Blender
            # -----------------------------------------------------
            process = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True
            )

            # Check process exit code
            # -----------------------------------------------------
            if process.returncode != 0:

                error_output = (
                    process.stderr.strip()
                    or process.stdout.strip()
                    or "Unknown background Blender error."
                )

                return {
                    "unassigned": [],
                    "missing": [],
                    "failed": [
                        f"Background Blender failed "
                        f"(exit code {process.returncode}): "
                        f"{error_output}"
                    ]
                }

            # Check result
            # -----------------------------------------------------
            if not os.path.exists(result_path):

                return {
                    "unassigned": [],
                    "missing": [],
                    "failed": [
                        "Background Blender finished, "
                        "but no result file was created."
                    ]
                }

            # Read result
            # -----------------------------------------------------
            try:

                with open(result_path, "r", encoding="utf-8") as f:
                    result = json.load(f)

            except Exception as e:

                return {
                    "unassigned": [],
                    "missing": [],
                    "failed": [
                        f"Could not read unassignment result: {e}"
                    ]
                }

            # -----------------------------------------------------
            # Refresh UI assignment data
            # -----------------------------------------------------

            if result.get("unassigned"):
                MBFA_LibraryManager.refresh_brush_catalog_assignments(
                    context
                )

            return result

        finally:

            # -----------------------------------------------------
            # Cleanup
            # -----------------------------------------------------

            for path in (
                settings_path,
                result_path,
            ):
                try:
                    os.remove(path)
                except OSError:
                    pass

            try:
                os.rmdir(temp_dir)
            except OSError:
                pass
            
    @staticmethod
    def refresh_brush_catalog_assignments(context):
        scene = context.scene
        folder = scene.asset_dir_path
        if not folder:
            scene.mbfa_brush_catalog_assignments.clear(); return False

        asset = os.path.join(folder, scene.brushes_blend_file)
        if not os.path.exists(asset):
            scene.mbfa_brush_catalog_assignments.clear(); return False

        external = os.path.join(os.path.dirname(__file__), "mbfa_background_read_catalog_assignments.py")
        temp = tempfile.mkdtemp(prefix="MBFA_catalog_read_")
        settings_path = os.path.join(temp, "settings.json")
        result_path = os.path.join(temp, "result.json")

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump({"asset_file_path": os.path.abspath(asset), "result_path": result_path}, f, indent=4)

        cmd = [bpy.app.binary_path, "--background", "--python", external, "--", settings_path]

        try:
            subprocess.run(cmd, check=True)
            if not os.path.exists(result_path): 
                return False

            with open(result_path, "r", encoding="utf-8") as f: result = json.load(f)
            
            if result.get("failed"):
                print("MBFA catalog read failed:", result["failed"]); 
                return False

            scene.mbfa_brush_catalog_assignments.clear()
            
            for a in result.get("assignments", []):
                e = scene.mbfa_brush_catalog_assignments.add()
                e.brush_name = a["brush_name"]; e.catalog_uuid = a["catalog_uuid"]

            print("MBFA: Loaded", len(scene.mbfa_brush_catalog_assignments), "catalog assignments.")
            return True

        except subprocess.CalledProcessError as e:
            print("MBFA: Background catalog read failed:", e); return False

        finally:
            for p in (settings_path, result_path):
                try: os.remove(p)
                except OSError: pass
                
            try: os.rmdir(temp)
            except OSError: pass

    @staticmethod
    def select_brushes_in_catalog(context):

        scene = context.scene

        if not scene.mbfa_catalogs:
            return

        index = scene.mbfa_catalog_index

        if index < 0 or index >= len(scene.mbfa_catalogs):
            return

        catalog = scene.mbfa_catalogs[index]

        assignments = {
            entry.brush_name
            for entry in scene.mbfa_brush_catalog_assignments
            if entry.catalog_uuid == catalog.uuid
        }

        for item in scene.mbfa_alpha_items:
            item.selected = item.brush_name in assignments