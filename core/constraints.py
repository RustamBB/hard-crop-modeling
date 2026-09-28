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
from bpy.types import PropertyGroup, Object

# Base constraint class
class ConstraintPropertyGroup(PropertyGroup):
    """Base class for all geometric constraints"""
    
    name: StringProperty(
        name="Name",
        description="Constraint name",
        default="Constraint"
    )
    
    is_active: BoolProperty(
        name="Active",
        description="Enable or disable the constraint",
        default=True
    )
    
    is_visible: BoolProperty(
        name="Visible",
        description="Show the constraint in the 3D viewport",
        default=True
    )
    
    constraint_type: EnumProperty(
        name="Type",
        description="Type of geometric constraint",
        items=[
            ('DISTANCE', "Distance", "Maintain specific distance between elements"),
            ('ANGLE', "Angle", "Maintain specific angle between elements"),
            ('PARALLEL', "Parallel", "Keep elements parallel"),
            ('PERPENDICULAR', "Perpendicular", "Keep elements perpendicular"),
            ('COINCIDENT', "Coincident", "Keep elements coincident"),
            ('HORIZONTAL', "Horizontal", "Keep elements horizontal"),
            ('VERTICAL', "Vertical", "Keep elements vertical"),
            ('SYMMETRIC', "Symmetric", "Keep elements symmetric"),
        ],
        default='DISTANCE'
    )
    
    error_margin: FloatProperty(
        name="Error Margin",
        description="Allowable deviation for the constraint",
        default=0.001,
        min=0.0,
        max=1.0,
        precision=5
    )

# Distance constraint
class DistanceConstraintPropertyGroup(ConstraintPropertyGroup):
    """Constraint to maintain a specific distance between elements"""
    
    distance: FloatProperty(
        name="Distance",
        description="Target distance to maintain",
        default=1.0,
        precision=4,
        unit='LENGTH'
    )
    
    first_element: PointerProperty(
        name="First Element",
        description="First element in the constraint",
        type=Object
    )
    
    second_element: PointerProperty(
        name="Second Element",
        description="Second element in the constraint",
        type=Object
    )
    
    maintain_exact: BoolProperty(
        name="Exact Distance",
        description="Maintain exact distance vs. minimum distance",
        default=True
    )

# Angle constraint
class AngleConstraintPropertyGroup(ConstraintPropertyGroup):
    """Constraint to maintain a specific angle between elements"""
    
    angle: FloatProperty(
        name="Angle",
        description="Target angle to maintain",
        default=0.0,
        precision=3,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    first_element: PointerProperty(
        name="First Element",
        description="First element in the constraint",
        type=Object
    )
    
    second_element: PointerProperty(
        name="Second Element",
        description="Second element in the constraint",
        type=Object
    )

# Parallel constraint
class ParallelConstraintPropertyGroup(ConstraintPropertyGroup):
    """Constraint to keep elements parallel"""
    
    first_element: PointerProperty(
        name="First Element",
        description="First element in the constraint",
        type=Object
    )
    
    second_element: PointerProperty(
        name="Second Element",
        description="Second element in the constraint",
        type=Object
    )

# Perpendicular constraint
class PerpendicularConstraintPropertyGroup(ConstraintPropertyGroup):
    """Constraint to keep elements perpendicular"""
    
    first_element: PointerProperty(
        name="First Element",
        description="First element in the constraint",
        type=Object
    )
    
    second_element: PointerProperty(
        name="Second Element",
        description="Second element in the constraint",
        type=Object
    )

# Collection to store all constraints
class ConstraintCollection(PropertyGroup):
    """Collection of all constraints in the scene"""
    
    constraints: CollectionProperty(
        name="Constraints",
        description="All geometric constraints in the scene",
        type=ConstraintPropertyGroup
    )
    
    active_constraint_index: IntProperty(
        name="Active Constraint",
        description="Index of the active constraint",
        default=0
    )

# List of all classes to register
classes = [
    ConstraintPropertyGroup,
    DistanceConstraintPropertyGroup,
    AngleConstraintPropertyGroup,
    ParallelConstraintPropertyGroup,
    PerpendicularConstraintPropertyGroup,
    ConstraintCollection,
]

def register():
    """Register all constraint classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add constraints collection to scene
    bpy.types.Scene.precision_constraints = PointerProperty(type=ConstraintCollection)

def unregister():
    """Unregister all constraint classes"""
    # Remove constraints collection from scene
    del bpy.types.Scene.precision_constraints
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# Utility functions for constraint handling
def add_distance_constraint(scene, first_element, second_element, distance=1.0):
    """Add a new distance constraint between two elements"""
    constraints = scene.precision_constraints.constraints
    new_constraint = constraints.add()
    new_constraint.name = f"Distance {len(constraints)}"
    new_constraint.constraint_type = 'DISTANCE'
    
    # Cast to the specific constraint type
    distance_constraint = new_constraint.as_pointer()
    distance_constraint.distance = distance
    distance_constraint.first_element = first_element
    distance_constraint.second_element = second_element
    
    return new_constraint

def update_constraints(scene):
    """Update all constraints in the scene"""
    for constraint in scene.precision_constraints.constraints:
        if constraint.is_active:
            # Implementation would depend on the constraint solver
            pass
