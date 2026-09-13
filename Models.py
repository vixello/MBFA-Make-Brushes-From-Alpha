import bpy

class MBFA_AlphaItem(bpy.types.PropertyGroup):
    filename: bpy.props.StringProperty()
    image_path: bpy.props.StringProperty()
    brush_name: bpy.props.StringProperty()

    texture_paint: bpy.props.BoolProperty(
        name="Texture Paint",
        description="Create this alpha as a Texture Paint brush",
        default=False
    )
    stroke_method: bpy.props.EnumProperty(
        name="Stroke",
        items=[
            ("DOTS", "Dots", ""),
            ("DRAG_DOT", "Drag Dot", ""),
            ("SPACE", "Space", ""),
            ("AIRBRUSH", "Airbrush", ""),
            ("ANCHORED", "Anchored", ""),
            ("LINE", "Line", ""),
            ("CURVE", "Curve", "")
        ],
        default="ANCHORED"
    )
    
    size: bpy.props.IntProperty(
        name="Size",
        default=100,
        min=1,
        max=1000
    )

    strength: bpy.props.FloatProperty(
        name="Strength",
        default=0.5,
        min=0.0,
        max=1.0
    )

    spacing: bpy.props.IntProperty(
        name="Spacing",
        default=10,
        min=1,
        max=100
    )

    invert_alpha: bpy.props.BoolProperty(
        name="Invert Alpha",
        default=False
    )
