# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
from bpy.utils import register_class, unregister_class

# Import core modules
from . import parameters
from . import constraints
from . import measurements
from . import units

# List of all modules to register/unregister
modules = [
    parameters,
    constraints,
    measurements,
    units
]

def register():
    """Register all core modules"""
    for module in modules:
        module.register()

def unregister():
    """Unregister all core modules"""
    for module in reversed(modules):
        module.unregister()
