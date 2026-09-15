import bpy
import os
import json
import tempfile
import subprocess
import bpy.utils.previews
import textwrap
import hashlib

extensions = {".jpg", ".jpeg", ".png", ".tif", ".bmp", ".psd"}


class MBFA_UL_alpha_list(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        row = layout.row(align = True)
        
        row.prop(item, "texture_paint", text="")
        layout.label(text=item.filename, icon="IMAGE_DATA")

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
        
class MBFA_LibraryManager:

    preview_collections = {}

    # ---------------------------------------------------------
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
            
            created = []
            skipped = []
            failed = []
            
            if os.path.exists(result_path):
                with open(result_path, "r", encoding="utf-8") as f:
                    result_data = json.load(f)
                    
                created = result_data.get("created", [])
                skipped = result_data.get("skipped", [])
                failed = result_data.get("failed", [])
                scene = context.scene

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


    # ---------------------------------------------------------
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

            item = scene.mbfa_alpha_items.add()
            
            item.filename = file
            item.stroke_method = "ANCHORED"
            item.image_path = os.path.join(folder, file)
            with open(item.image_path, "rb") as f:    
                item.id = hashlib.sha1(f.read()).hexdigest() # Permament ID for the alpha content
         
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