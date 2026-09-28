# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
import math
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup

# Unit system constants
UNIT_SYSTEM_METRIC = 'METRIC'
UNIT_SYSTEM_IMPERIAL = 'IMPERIAL'

# Metric units and conversion factors (to meters)
METRIC_UNITS = {
    'mm': 0.001,
    'cm': 0.01,
    'm': 1.0,
    'km': 1000.0
}

# Imperial units and conversion factors (to meters)
IMPERIAL_UNITS = {
    'in': 0.0254,
    'ft': 0.3048,
    'yd': 0.9144,
    'mi': 1609.344
}

# Unit conversion preferences
class UnitConversionPreferences(PropertyGroup):
    """Preferences for unit conversions"""
    
    unit_system: EnumProperty(
        name="Unit System",
        description="Select the unit system to use",
        items=[
            (UNIT_SYSTEM_METRIC, "Metric", "Use metric units (mm, cm, m)"),
            (UNIT_SYSTEM_IMPERIAL, "Imperial", "Use imperial units (inches, feet)"),
        ],
        default=UNIT_SYSTEM_METRIC
    )
    
    metric_unit: EnumProperty(
        name="Metric Unit",
        description="Select the default metric unit",
        items=[
            ('mm', "Millimeters (mm)", "Use millimeters"),
            ('cm', "Centimeters (cm)", "Use centimeters"),
            ('m', "Meters (m)", "Use meters"),
            ('km', "Kilometers (km)", "Use kilometers"),
        ],
        default='mm'
    )
    
    imperial_unit: EnumProperty(
        name="Imperial Unit",
        description="Select the default imperial unit",
        items=[
            ('in', "Inches (in)", "Use inches"),
            ('ft', "Feet (ft)", "Use feet"),
            ('yd', "Yards (yd)", "Use yards"),
            ('mi', "Miles (mi)", "Use miles"),
        ],
        default='in'
    )
    
    display_unit_labels: BoolProperty(
        name="Display Unit Labels",
        description="Show unit labels in the interface",
        default=True
    )
    
    precision: IntProperty(
        name="Decimal Precision",
        description="Number of decimal places to display",
        default=3,
        min=0,
        max=6
    )

# Unit conversion functions
def convert_to_meters(value, from_unit):
    """Convert a value from the specified unit to meters"""
    if from_unit in METRIC_UNITS:
        return value * METRIC_UNITS[from_unit]
    elif from_unit in IMPERIAL_UNITS:
        return value * IMPERIAL_UNITS[from_unit]
    else:
        raise ValueError(f"Unknown unit: {from_unit}")

def convert_from_meters(value, to_unit):
    """Convert a value from meters to the specified unit"""
    if to_unit in METRIC_UNITS:
        return value / METRIC_UNITS[to_unit]
    elif to_unit in IMPERIAL_UNITS:
        return value / IMPERIAL_UNITS[to_unit]
    else:
        raise ValueError(f"Unknown unit: {to_unit}")

def convert_between_units(value, from_unit, to_unit):
    """Convert a value between two units"""
    # First convert to meters
    meters = convert_to_meters(value, from_unit)
    # Then convert to target unit
    return convert_from_meters(meters, to_unit)

def get_scene_unit_system(context):
    """Get the unit system from the current scene or addon preferences"""
    # First check addon preferences
    addon_prefs = context.preferences.addons["precision_surface"].preferences
    if hasattr(addon_prefs, "unit_system"):
        return addon_prefs.unit_system
    
    # Fall back to scene units
    unit_settings = context.scene.unit_settings
    if unit_settings.system == 'METRIC':
        return UNIT_SYSTEM_METRIC
    elif unit_settings.system == 'IMPERIAL':
        return UNIT_SYSTEM_IMPERIAL
    else:
        return UNIT_SYSTEM_METRIC  # Default to metric

def get_default_unit(context):
    """Get the default unit for the current unit system"""
    unit_system = get_scene_unit_system(context)
    
    # Check addon preferences
    addon_prefs = context.preferences.addons["precision_surface"].preferences
    
    if unit_system == UNIT_SYSTEM_METRIC:
        if hasattr(addon_prefs, "metric_unit"):
            return addon_prefs.metric_unit
        return 'mm'  # Default to millimeters
    else:
        if hasattr(addon_prefs, "imperial_unit"):
            return addon_prefs.imperial_unit
        return 'in'  # Default to inches

def format_distance(value, precision=3, show_unit=True):
    """Format a distance value with appropriate units"""
    context = bpy.context
    unit = get_default_unit(context)
    converted_value = convert_from_meters(value, unit)
    
    if show_unit:
        return f"{converted_value:.{precision}f} {unit}"
    else:
        return f"{converted_value:.{precision}f}"

def format_angle(value, precision=3, show_unit=True):
    """Format an angle value with appropriate units"""
    # Convert from radians to degrees
    degrees = math.degrees(value)
    
    if show_unit:
        return f"{degrees:.{precision}f}°"
    else:
        return f"{degrees:.{precision}f}"

# List of all classes to register
classes = [
    UnitConversionPreferences,
]

def register():
    """Register all unit conversion classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add unit conversion preferences to scene
    bpy.types.Scene.precision_units = PointerProperty(type=UnitConversionPreferences)

def unregister():
    """Unregister all unit conversion classes"""
    # Remove unit conversion preferences from scene
    del bpy.types.Scene.precision_units
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
