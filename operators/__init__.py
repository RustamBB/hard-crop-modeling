# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy

# Import operator modules
from . import precision_ops
from . import pattern_ops
from . import manufacturing_ops

# List of all modules to register/unregister
modules = [
    precision_ops,
    pattern_ops,
    manufacturing_ops
]

def register():
    """Register all operator modules"""
    for module in modules:
        module.register()

def unregister():
    """Unregister all operator modules"""
    for module in reversed(modules):
        module.unregister()
