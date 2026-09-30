# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
)
from bpy.types import PropertyGroup

# Base parameter class
class ParameterPropertyGroup(PropertyGroup):
    """Base class for all parameter types"""
    
    name: StringProperty(
        name="Name",
        description="Parameter name",
        default="Parameter"
    )
    
    description: StringProperty(
        name="Description",
        description="Parameter description",
        default=""
    )
    
    is_locked: BoolProperty(
        name="Locked",
        description="Lock parameter from editing",
        default=False
    )

# Distance parameter
class DistanceParameterPropertyGroup(ParameterPropertyGroup):
    """Parameter for storing distance values"""
    
    value: FloatProperty(
        name="Value",
        description="Distance value",
        default=1.0,
        precision=4,
        unit='LENGTH'
    )
    
    min_value: FloatProperty(
        name="Minimum",
        description="Minimum allowed value",
        default=0.0,
        precision=4,
        unit='LENGTH'
    )
    
    max_value: FloatProperty(
        name="Maximum",
        description="Maximum allowed value",
        default=1000.0,
        precision=4,
        unit='LENGTH'
    )

# Angle parameter
class AngleParameterPropertyGroup(ParameterPropertyGroup):
    """Parameter for storing angle values"""
    
    value: FloatProperty(
        name="Value",
        description="Angle value",
        default=0.0,
        precision=3,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    min_value: FloatProperty(
        name="Minimum",
        description="Minimum allowed value",
        default=0.0,
        precision=3,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    max_value: FloatProperty(
        name="Maximum",
        description="Maximum allowed value",
        default=3.14159 * 2,
        precision=3,
        subtype='ANGLE',
        unit='ROTATION'
    )

# Boolean parameter
class BoolParameterPropertyGroup(ParameterPropertyGroup):
    """Parameter for storing boolean values"""
    
    value: BoolProperty(
        name="Value",
        description="Boolean value",
        default=False
    )

# Integer parameter
class IntParameterPropertyGroup(ParameterPropertyGroup):
    """Parameter for storing integer values"""
    
    value: IntProperty(
        name="Value",
        description="Integer value",
        default=0
    )
    
    min_value: IntProperty(
        name="Minimum",
        description="Minimum allowed value",
        default=0
    )
    
    max_value: IntProperty(
        name="Maximum",
        description="Maximum allowed value",
        default=100
    )

# Enum parameter
class EnumParameterPropertyGroup(ParameterPropertyGroup):
    """Parameter for storing enum values"""
    
    # This is a simplified enum implementation
    # In a real implementation, you'd need to handle dynamic enum items
    items: StringProperty(
        name="Items",
        description="Comma-separated list of enum items",
        default="Option 1,Option 2,Option 3"
    )
    
    value: StringProperty(
        name="Value",
        description="Selected enum value",
        default="Option 1"
    )

# Vector parameter
class VectorParameterPropertyGroup(ParameterPropertyGroup):
    """Parameter for storing vector values"""
    
    value: FloatVectorProperty(
        name="Value",
        description="Vector value",
        default=(0.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )

# Main addon properties
class PrecisionSurfaceProperties(PropertyGroup):
    """Properties for the PrecisionSurface addon"""
    
    # Active tool selection
    active_tool: EnumProperty(
        name="Active Tool",
        description="Currently active precision tool",
        items=[
            ('NONE', "None", "No tool selected"),
            ('PRECISION_MOVE', "Precision Move", "Move objects with precise control"),
            ('PRECISION_ROTATE', "Precision Rotate", "Rotate objects with precise control"),
            ('PRECISION_SCALE', "Precision Scale", "Scale objects with precise control"),
            ('DIMENSION', "Dimension", "Add dimension annotations"),
            ('CONSTRAINT', "Constraint", "Add geometric constraints"),
        ],
        default='NONE'
    )
    
    # Grid settings
    grid_size: FloatProperty(
        name="Grid Size",
        description="Size of the precision grid",
        default=1.0,
        min=0.001,
        max=1000.0,
        precision=3,
        unit='LENGTH'
    )
    
    snap_to_grid: BoolProperty(
        name="Snap to Grid",
        description="Enable snapping to precision grid",
        default=True
    )
    
    # Measurement settings
    show_measurements: BoolProperty(
        name="Show Measurements",
        description="Display measurement annotations in the viewport",
        default=True
    )
    
    precision_level: IntProperty(
        name="Precision Level",
        description="Number of decimal places for measurements",
        default=3,
        min=1,
        max=6
    )
    
    # UI settings
    display_mode: EnumProperty(
        name="Display Mode",
        description="Control the amount of information displayed",
        items=[
            ('BASIC', "Basic", "Show only essential controls"),
            ('STANDARD', "Standard", "Show standard level of detail"),
            ('ADVANCED', "Advanced", "Show all available options"),
        ],
        default='STANDARD'
    )
    
    show_help: BoolProperty(
        name="Show Help",
        description="Display help text for tools",
        default=True
    )

# List of all classes to register
classes = [
    ParameterPropertyGroup,
    DistanceParameterPropertyGroup,
    AngleParameterPropertyGroup,
    BoolParameterPropertyGroup,
    IntParameterPropertyGroup,
    EnumParameterPropertyGroup,
    VectorParameterPropertyGroup,
    PrecisionSurfaceProperties,
]

def register():
    """Register all parameter classes"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all parameter classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
