# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering
#
# Copyright (C) 2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "PrecisionSurface",
    "author": "Precision Modeling Team",
    "description": "Bridge the gap between art and engineering with precision hard surface modeling tools",
    "blender": (3, 0, 0),
    "version": (0, 1, 0),
    "location": "View3D > Sidebar > PrecisionSurface",
    "warning": "This is an early development version",
    "category": "Modeling",
    "doc_url": "",
    "tracker_url": "",
}

import bpy
import importlib
import sys
import os

from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import (
    Panel,
    Operator,
    AddonPreferences,
    PropertyGroup,
)

# Define addon modules that need to be reloaded during development
addon_modules = [
    'core.parameters',
    'core.constraints',
    'core.measurements',
    'core.units',
    'operators.precision_ops',
    'operators.pattern_ops',
    'operators.manufacturing_ops',
    'ui.panels',
    'ui.menus',
    'ui.tutorials',
    'library.components',
    'utils.geometry',
    'utils.export',
    'utils.validation',
]

# Import addon modules
if "bpy" in locals():
    # Reload modules when the addon is reloaded
    import importlib
    for module in addon_modules:
        if module in sys.modules:
            importlib.reload(sys.modules[module])

# Import addon packages
from . import core
from . import operators
from . import ui
from . import library
from . import utils

# Create preferences class
class PrecisionSurfacePreferences(AddonPreferences):
    bl_idname = __name__

    # Default units for the addon
    default_unit_system: EnumProperty(
        name="Default Unit System",
        description="Set the default unit system for measurements",
        items=[
            ('METRIC', "Metric", "Use metric units (mm, cm, m)"),
            ('IMPERIAL', "Imperial", "Use imperial units (inches, feet)"),
        ],
        default='METRIC',
    )
    
    precision_level: IntProperty(
        name="Default Precision Level",
        description="Set the default decimal precision for measurements",
        default=3,
        min=1,
        max=6
    )
    
    show_tooltips: BoolProperty(
        name="Show Tooltips",
        description="Enable context-sensitive tooltips",
        default=True,
    )
    
    enable_tutorial_mode: BoolProperty(
        name="Enable Tutorial Mode",
        description="Show interactive tutorials for beginners",
        default=True,
    )
    
    experience_level: EnumProperty(
        name="Experience Level",
        description="Set the UI complexity based on your experience",
        items=[
            ('BEGINNER', "Beginner", "Show simplified UI with extensive help"),
            ('INTERMEDIATE', "Intermediate", "Show standard UI with some help"),
            ('ADVANCED', "Advanced", "Show all features with minimal help"),
        ],
        default='BEGINNER',
    )

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Measurement Settings:")
        row = box.row()
        row.prop(self, "default_unit_system", expand=True)
        box.prop(self, "precision_level")
        
        box = layout.box()
        box.label(text="Interface Settings:")
        box.prop(self, "show_tooltips")
        box.prop(self, "enable_tutorial_mode")
        box.prop(self, "experience_level", expand=True)
        
        box = layout.box()
        box.label(text="About PrecisionSurface:")
        box.label(text="Version: 0.1.0")
        box.label(text="Bridge the gap between art and engineering")
        row = box.row()
        row.operator("wm.url_open", text="Documentation").url = "https://precisionsurface.docs"
        row.operator("wm.url_open", text="Report Issues").url = "https://github.com/precisionsurface/issues"

# List of classes to register
classes = [
    PrecisionSurfacePreferences,
]

# Module initialization
def register():
    """Register all classes and properties for the addon"""
    
    # Register this module's classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register core modules
    core.register()
    
    # Register operator modules
    operators.register()
    
    # Register UI modules
    ui.register()
    
    # Register library modules
    library.register()
    
    # Register the addon properties in the Scene
    bpy.types.Scene.precision_surface = PointerProperty(type=core.parameters.PrecisionSurfaceProperties)
    
    print("PrecisionSurface: Addon registered successfully")

def unregister():
    """Unregister all classes and properties for the addon"""
    
    # Remove the addon properties from the Scene
    del bpy.types.Scene.precision_surface
    
    # Unregister library modules
    library.unregister()
    
    # Unregister UI modules
    ui.unregister()
    
    # Unregister operator modules
    operators.unregister()
    
    # Unregister core modules
    core.unregister()
    
    # Unregister this module's classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("PrecisionSurface: Addon unregistered successfully")

# This allows you to run the script directly from Blender's Text editor
if __name__ == "__main__":
    register()
