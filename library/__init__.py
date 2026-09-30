# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy

# Import library modules
from . import components

# List of all modules to register/unregister
modules = [
    components,
]

def register():
    """Register all library modules"""
    for module in modules:
        module.register()

def unregister():
    """Unregister all library modules"""
    for module in reversed(modules):
        module.unregister()
