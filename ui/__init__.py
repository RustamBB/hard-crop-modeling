# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy

# Import UI modules
from . import panels
from . import menus
from . import tutorials

# List of all modules to register/unregister
modules = [
    panels,
    menus,
    tutorials
]

def register():
    """Register all UI modules"""
    for module in modules:
        module.register()

def unregister():
    """Unregister all UI modules"""
    for module in reversed(modules):
        module.unregister()
