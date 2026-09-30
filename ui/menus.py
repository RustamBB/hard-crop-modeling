# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
from bpy.types import Menu

# Main menu class for PrecisionSurface
class PRECISION_SURFACE_MT_Main(Menu):
    """Main menu for PrecisionSurface addon"""
    bl_idname = "PRECISION_SURFACE_MT_Main"
    bl_label = "PrecisionSurface"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator_context = 'INVOKE_DEFAULT'
        
        # Precision tools submenu
        layout.menu("PRECISION_SURFACE_MT_PrecisionTools", icon='ORIENTATION_LOCAL')
        
        # Parametric shapes submenu
        layout.menu("PRECISION_SURFACE_MT_ParametricShapes", icon='MESH_CUBE')
        
        # Patterns submenu
        layout.menu("PRECISION_SURFACE_MT_Patterns", icon='LIGHTPROBE_GRID')
        
        # Manufacturing submenu
        layout.menu("PRECISION_SURFACE_MT_Manufacturing", icon='MODIFIER')
        
        layout.separator()
        
        # Settings
        layout.operator("wm.call_panel", text="Precision Settings").name = "PRECISION_SURFACE_PT_Main"
        
        # Help
        layout.operator("wm.url_open", text="Online Documentation").url = "https://precisionsurface.docs"

# Precision tools menu
class PRECISION_SURFACE_MT_PrecisionTools(Menu):
    """Menu for precision modeling tools"""
    bl_idname = "PRECISION_SURFACE_MT_PrecisionTools"
    bl_label = "Precision Tools"
    
    def draw(self, context):
        layout = self.layout
        
        # Transformation operators
        layout.operator("precision.precise_move", icon='ORIENTATION_LOCAL')
        layout.operator("precision.precise_rotate", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        layout.operator("precision.precise_scale", icon='FULLSCREEN_ENTER')
        
        layout.separator()
        
        # Measurement operators
        layout.operator("precision.add_dimension", icon='DRIVER_DISTANCE')

# Parametric shapes menu
class PRECISION_SURFACE_MT_ParametricShapes(Menu):
    """Menu for parametric shape creation"""
    bl_idname = "PRECISION_SURFACE_MT_ParametricShapes"
    bl_label = "Parametric Shapes"
    
    def draw(self, context):
        layout = self.layout
        
        # Shape creation operators
        layout.operator("precision.create_parametric_cube", icon='MESH_CUBE')
        layout.operator("precision.create_parametric_cylinder", icon='MESH_CYLINDER')
        
        layout.separator()
        
        # Parameters panel shortcut
        layout.operator("wm.call_panel", text="Edit Parameters").name = "PRECISION_SURFACE_PT_ParametricShapes"

# Patterns menu
class PRECISION_SURFACE_MT_Patterns(Menu):
    """Menu for pattern creation tools"""
    bl_idname = "PRECISION_SURFACE_MT_Patterns"
    bl_label = "Patterns"
    
    def draw(self, context):
        layout = self.layout
        
        # Pattern creation operators
        layout.operator("pattern.linear_array", icon='LIGHTPROBE_GRID')
        layout.operator("pattern.circular_array", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        layout.operator("pattern.honeycomb_pattern", icon='MESH_GRID')

# Manufacturing menu
class PRECISION_SURFACE_MT_Manufacturing(Menu):
    """Menu for manufacturing tools"""
    bl_idname = "PRECISION_SURFACE_MT_Manufacturing"
    bl_label = "Manufacturing"
    
    def draw(self, context):
        layout = self.layout
        
        # Analysis tools
        layout.operator("manufacturing.check_printability", icon='MODIFIER')
        
        layout.separator()
        
        # Manufacturing preparation tools
        layout.operator("manufacturing.add_fillet", icon='MESH_CIRCLE')
        layout.operator("manufacturing.add_chamfer", icon='MESH_PLANE')
        
        layout.separator()
        
        # Export tools
        layout.operator("manufacturing.export_for_manufacturing", icon='EXPORT')

# Add PrecisionSurface to main 3D View menu
def draw_precision_surface_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("PRECISION_SURFACE_MT_Main", icon='MESH_CUBE')

# List of all classes to register
classes = [
    PRECISION_SURFACE_MT_Main,
    PRECISION_SURFACE_MT_PrecisionTools,
    PRECISION_SURFACE_MT_ParametricShapes,
    PRECISION_SURFACE_MT_Patterns,
    PRECISION_SURFACE_MT_Manufacturing,
]

def register():
    """Register all menu classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add PrecisionSurface to main 3D View menu
    bpy.types.VIEW3D_MT_editor_menus.append(draw_precision_surface_menu)

def unregister():
    """Unregister all menu classes"""
    # Remove PrecisionSurface from main 3D View menu
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_precision_surface_menu)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
