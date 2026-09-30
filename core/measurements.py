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
    CollectionProperty,
)
from bpy.types import PropertyGroup, Object
from mathutils import Vector

# Import the unit conversion system
from . import units

# Measurement property group
class MeasurementPropertyGroup(PropertyGroup):
    """Base class for all measurement types"""
    
    name: StringProperty(
        name="Name",
        description="Measurement name",
        default="Measurement"
    )
    
    is_visible: BoolProperty(
        name="Visible",
        description="Show the measurement in the 3D viewport",
        default=True
    )
    
    color: FloatVectorProperty(
        name="Color",
        description="Display color for the measurement",
        default=(0.0, 0.0, 1.0, 1.0),
        size=4,
        min=0.0,
        max=1.0,
        subtype='COLOR'
    )
    
    measurement_type: EnumProperty(
        name="Type",
        description="Type of measurement",
        items=[
            ('DISTANCE', "Distance", "Measure distance between elements"),
            ('ANGLE', "Angle", "Measure angle between elements"),
            ('RADIUS', "Radius", "Measure radius of a curve"),
            ('DIAMETER', "Diameter", "Measure diameter of a circle"),
            ('AREA', "Area", "Measure surface area"),
            ('VOLUME', "Volume", "Measure volume"),
        ],
        default='DISTANCE'
    )
    
    precision: IntProperty(
        name="Precision",
        description="Number of decimal places to display",
        default=3,
        min=0,
        max=6
    )
    
    display_units: BoolProperty(
        name="Display Units",
        description="Show units with the measurement value",
        default=True
    )

# Distance measurement
class DistanceMeasurementPropertyGroup(MeasurementPropertyGroup):
    """Measurement for distances between elements"""
    
    start_point: FloatVectorProperty(
        name="Start Point",
        description="Starting point of the measurement",
        default=(0.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    end_point: FloatVectorProperty(
        name="End Point",
        description="Ending point of the measurement",
        default=(1.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    first_element: PointerProperty(
        name="First Element",
        description="First element being measured",
        type=Object
    )
    
    second_element: PointerProperty(
        name="Second Element",
        description="Second element being measured",
        type=Object
    )

    def calculate_value(self):
        """Calculate the distance between start and end points"""
        start = Vector(self.start_point)
        end = Vector(self.end_point)
        distance = (end - start).length
        return distance

    def format_display_value(self, context):
        """Format the measurement for display with appropriate units"""
        value = self.calculate_value()
        return units.format_distance(value, self.precision, self.display_units)

# Angle measurement
class AngleMeasurementPropertyGroup(MeasurementPropertyGroup):
    """Measurement for angles between elements"""
    
    center_point: FloatVectorProperty(
        name="Center Point",
        description="Center point of the angle",
        default=(0.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    point1: FloatVectorProperty(
        name="First Point",
        description="First point defining the angle",
        default=(1.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    point2: FloatVectorProperty(
        name="Second Point",
        description="Second point defining the angle",
        default=(0.0, 1.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    first_element: PointerProperty(
        name="First Element",
        description="First element being measured",
        type=Object
    )
    
    second_element: PointerProperty(
        name="Second Element",
        description="Second element being measured",
        type=Object
    )

    def calculate_value(self):
        """Calculate the angle between the two vectors"""
        center = Vector(self.center_point)
        vec1 = Vector(self.point1) - center
        vec2 = Vector(self.point2) - center
        
        # Normalize vectors
        if vec1.length > 0:
            vec1 = vec1.normalized()
        if vec2.length > 0:
            vec2 = vec2.normalized()
        
        # Calculate angle
        dot_product = min(max(vec1.dot(vec2), -1.0), 1.0)  # Clamp to avoid precision errors
        angle = math.acos(dot_product)
        
        return angle

    def format_display_value(self, context):
        """Format the angle for display with appropriate units"""
        value = self.calculate_value()
        return units.format_angle(value, self.precision, self.display_units)

# Collection to store all measurements
class MeasurementCollection(PropertyGroup):
    """Collection of all measurements in the scene"""
    
    measurements: CollectionProperty(
        name="Measurements",
        description="All measurements in the scene",
        type=MeasurementPropertyGroup
    )
    
    active_measurement_index: IntProperty(
        name="Active Measurement",
        description="Index of the active measurement",
        default=0
    )

# List of all classes to register
classes = [
    MeasurementPropertyGroup,
    DistanceMeasurementPropertyGroup,
    AngleMeasurementPropertyGroup,
    MeasurementCollection,
]

def register():
    """Register all measurement classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add measurements collection to scene
    bpy.types.Scene.precision_measurements = PointerProperty(type=MeasurementCollection)

def unregister():
    """Unregister all measurement classes"""
    # Remove measurements collection from scene
    del bpy.types.Scene.precision_measurements
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# Utility functions for measurement handling
def add_distance_measurement(scene, start_point, end_point, name=None):
    """Add a new distance measurement between two points"""
    measurements = scene.precision_measurements.measurements
    new_measurement = measurements.add()
    
    if name:
        new_measurement.name = name
    else:
        new_measurement.name = f"Distance {len(measurements)}"
    
    new_measurement.measurement_type = 'DISTANCE'
    new_measurement.start_point = start_point
    new_measurement.end_point = end_point
    
    return new_measurement

def add_angle_measurement(scene, center_point, point1, point2, name=None):
    """Add a new angle measurement between two vectors"""
    measurements = scene.precision_measurements.measurements
    new_measurement = measurements.add()
    
    if name:
        new_measurement.name = name
    else:
        new_measurement.name = f"Angle {len(measurements)}"
    
    new_measurement.measurement_type = 'ANGLE'
    new_measurement.center_point = center_point
    new_measurement.point1 = point1
    new_measurement.point2 = point2
    
    return new_measurement

def update_measurements(scene):
    """Update all measurements in the scene"""
    # This function would typically be called in a frame change handler
    for measurement in scene.precision_measurements.measurements:
        if measurement.is_visible:
            # Implementation would depend on how measurements are visualized
            pass
