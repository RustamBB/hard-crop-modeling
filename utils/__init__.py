# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy

# Import utility modules
from . import geometry
from . import export
from . import validation

# List of all modules to register/unregister
modules = [
    geometry,
    export,
    validation
]

def register():
    """Register all utility modules"""
    for module in modules:
        if hasattr(module, "register"):
            module.register()

def unregister():
    """Unregister all utility modules"""
    for module in reversed(modules):
        if hasattr(module, "unregister"):
            module.unregister()
