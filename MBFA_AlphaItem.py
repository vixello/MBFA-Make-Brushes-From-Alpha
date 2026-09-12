import bpy

class MBFA_AlphaItem(bpy.types.PropertyGroup):
    filename: bpy.props.StringProperty()
    image_path: bpy.props.StringProperty()
    
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
