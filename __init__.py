bl_info = {
    "name": "MBFA",
    "author": "viXello",
    "version": (1, 0, 0),
    "blender": (5, 2, 1),
    "location": "View3D > Sidebar",
    "description": "Make Brush From Alpha",
    "category": "Paint",
}

from .Panel import register, unregister


if __name__ == "__main__":
    register()
