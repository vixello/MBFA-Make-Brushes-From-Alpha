import bpy
import os
import json
import tempfile
import subprocess
import bpy.utils.previews
import textwrap

extensions = {".jpg", ".jpeg", ".png", ".tif", ".bmp", ".psd"}


class MBFA_UL_alpha_list(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        
        row = layout.row(align = True)
        
        row.prop(item, "texture_paint", text="")
        layout.label(text=item.filename, icon="IMAGE_DATA")


class MBFA_LibraryManager:

    preview_collections = {}

    # ---------------------------------------------------------
    # CREATE / UPDATE BRUSHES
    # ---------------------------------------------------------

    @staticmethod
    def add_brushes_from_alpha(context, alpha_folder, asset_file_path):
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

        for item in context.scene.mbfa_alpha_items:

            alpha_items.append({
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
        asset_folder = os.path.dirname(asset_file_path)

        if asset_folder and not os.path.exists(asset_folder):
            os.makedirs(asset_folder)


        # 3. CREATE TEMPORARY WORK DIRECTORY
        temp_dir = tempfile.mkdtemp(prefix="MBFA_")

        settings_path = os.path.join(temp_dir, "mbfa_settings.json")
        script_path = os.path.join(temp_dir, "mbfa_create_brushes.py")

        # 4. WRITE SETTINGS JSON
        settings = {
            "asset_file_path": asset_file_path,
            "items": alpha_items,
        }

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)


        # 5. BACKGROUND BLENDER SCRIPT
        script = textwrap.dedent(r'''
            import bpy
            import json
            import os
            import sys

            # READ SETTINGS
            settings_path = sys.argv[-1]
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            asset_file_path = settings["asset_file_path"]
            items = settings["items"]

            print("")
            print("========================================")
            print(" MBFA ASSET LIBRARY GENERATOR")
            print("========================================")
            print("")
            print("Asset library:", asset_file_path)
            print("Brush count:", len(items))
            print("")

            # DISABLE BLEND BACKUPS
            bpy.context.preferences.filepaths.save_version = 0

            # OPEN OR CREATE ASSET LIBRARY
            if os.path.exists(asset_file_path):
                print("Opening existing asset library:", asset_file_path)
                bpy.ops.wm.open_mainfile(filepath=asset_file_path)
            else:
                print("Creating new asset library:", asset_file_path)
                bpy.ops.wm.read_factory_settings(use_empty=True)

            # CREATE / UPDATE BRUSHES
            for data in items:

                name = data["brush_name"]
                if not name:
                    name = os.path.splitext(data["filename"])[0]

                image_path = data["image_path"]

                print("")
                print("----------------------------------------")
                print("Processing brush:", name)
                print("----------------------------------------")

                # REMOVE EXISTING BRUSH
                old_brush = bpy.data.brushes.get(name)
                if old_brush:
                    print("Updating existing brush:", name)
                    bpy.data.brushes.remove(old_brush, do_unlink=True)

                # LOAD IMAGE
                print("Loading image:", image_path)
                img = bpy.data.images.load(image_path, check_existing=False)
                img.name = name + "_Alpha"

                # INVERT ALPHA
                if data.get("invert_alpha", False):
                    print("Inverting alpha:", name)
                    pixels = list(img.pixels)
                    for i in range(0, len(pixels), 4):
                        pixels[i]     = 1.0 - pixels[i]
                        pixels[i + 1] = 1.0 - pixels[i + 1]
                        pixels[i + 2] = 1.0 - pixels[i + 2]
                        pixels[i + 3] = 1.0 - pixels[i + 3]
                    img.pixels = pixels

                # CREATE TEXTURE
                tex = bpy.data.textures.new(name + "_tex", type="IMAGE")
                tex.image = img

                # CREATE BRUSH
                brush = bpy.data.brushes.new(name=name)
                
                if data["texture_paint"] == False:
                    brush.use_paint_sculpt = True
                    brush.use_paint_vertex = False                
                    
                elif data["texture_paint"] == True:
                    brush.use_paint_sculpt = False
                    brush.use_paint_image = True
                    
                brush.stroke_method = data["stroke_method"]
                brush.size = data["size"]
                brush.strength = data["strength"]
                brush.spacing = data["spacing"]

                # ASSIGN TEXTURE
                if not brush.texture_slot:
                    brush.texture_slot = brush.texture_slots.add()

                brush.texture_slot.texture = tex
                brush.texture_slot.map_mode = "VIEW_PLANE"

                # PREVIEW IMAGE
                preview_img = bpy.data.images.new(name + "_preview", 256, 256)

                preview_source = img.copy()
                preview_source.name = name + "_PreviewSource"
                preview_source.scale(256, 256)

                preview_img.pixels = preview_source.pixels[:]

                preview = brush.preview_ensure()
                preview.image_size = (256, 256)
                preview.image_pixels_float = preview_img.pixels[:]

                # MARK AS ASSET
                brush.asset_mark()

                print("Created asset brush:", name)

            # SAVE ASSET LIBRARY
            print("")
            print("Saving asset library...")
            print(asset_file_path)

            bpy.ops.wm.save_as_mainfile(filepath=asset_file_path, check_existing=False)

            print("")
            print("========================================")
            print(" MBFA ASSET LIBRARY COMPLETE")
            print("========================================")
            print("")
            ''')

        # -----------------------------------------------------
        # 6. WRITE BACKGROUND SCRIPT
        # -----------------------------------------------------
        with open(script_path, "w", encoding="utf-8") as f: 
            f.write(script)


        # -----------------------------------------------------
        # 7. FIND CURRENT BLENDER EXECUTABLE
        # -----------------------------------------------------
        blender_executable = bpy.app.binary_path


        # -----------------------------------------------------
        # 8. START SECOND BLENDER PROCESS
        # -----------------------------------------------------
        command = [
            blender_executable,
            "--background",
            "--python",
            script_path,
            "--",
            settings_path,
        ]


        print("")
        print(" MBFA: Starting background Blender")
        print("")

        print(" ".join(command))


        try:
            result = subprocess.run(command, check=True)
            print("")
            print("MBFA: Background Blender finished successfully.")

        except subprocess.CalledProcessError as e:
            print("")
            print("MBFA ERROR: Asset library generation failed.")

            print("Blender return code:",e.returncode)

            return


        finally:

            # CLEAN TEMP FILES
            try:
                os.remove(script_path)
            except OSError:
                pass

            try:
                os.remove(settings_path)
            except OSError:
                pass

            try:
                os.rmdir(temp_dir)
            except OSError:
                pass


        print("")
        print(" MBFA COMPLETE")
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

        asset_folder = os.path.dirname(asset_file_path)

        if (asset_folder and not os.path.exists(asset_folder)):
            os.makedirs(asset_folder)

        if os.path.exists(asset_file_path):
            print("MBFA: Asset library already exists:", asset_file_path)

        else:
            print("MBFA: Asset library will be created:", asset_file_path)


    @staticmethod
    def refresh_alpha_list(context):
        scene = context.scene

        scene.mbfa_alpha_items.clear()

        MBFA_LibraryManager.unregisterAlphaPreviews()

        folder = scene.my_folder

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