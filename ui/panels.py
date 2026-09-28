# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
from bpy.types import Panel

# Base panel class for PrecisionSurface
class PRECISION_SURFACE_PT_Base(Panel):
    """Base panel for all PrecisionSurface panels"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PrecisionSurface'
    
    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH'}

# Main panel
class PRECISION_SURFACE_PT_Main(PRECISION_SURFACE_PT_Base):
    """Main panel for PrecisionSurface"""
    bl_idname = "PRECISION_SURFACE_PT_Main"
    bl_label = "Precision Surface"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.precision_surface
        
        # Logo and version info
        row = layout.row()
        row.label(text="PrecisionSurface v0.1.0")
        
        # Mode selector
        box = layout.box()
        row = box.row()
        row.label(text="Experience Level:")
        row = box.row()
        row.prop(props, "display_mode", expand=True)
        
        # Help toggle
        row = layout.row()
        row.prop(props, "show_help", icon='QUESTION')

# Precision Tools panel
class PRECISION_SURFACE_PT_PrecisionTools(PRECISION_SURFACE_PT_Base):
    """Panel for precision modeling tools"""
    bl_parent_id = "PRECISION_SURFACE_PT_Main"
    bl_label = "Precision Tools"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.precision_surface
        
        # Tool selection
        row = layout.row(align=True)
        row.label(text="Active Tool:")
        row.prop(props, "active_tool", text="")
        
        # Precision settings
        box = layout.box()
        box.label(text="Precision Settings:")
        row = box.row(align=True)
        row.prop(props, "grid_size", text="Grid Size")
        row.prop(props, "snap_to_grid", text="", icon='SNAP_GRID')
        
        row = box.row(align=True)
        row.prop(props, "precision_level", text="Precision")
        row.prop(props, "show_measurements", text="", icon='RULER')
        
        # Precision transformation tools
        col = layout.column(align=True)
        col.label(text="Precision Transformations:")
        row = col.row(align=True)
        row.operator("precision.precise_move", text="Move", icon='ORIENTATION_LOCAL')
        row.operator("precision.precise_rotate", text="Rotate", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        row.operator("precision.precise_scale", text="Scale", icon='FULLSCREEN_ENTER')
        
        # Help text if enabled
        if props.show_help:
            box = layout.box()
            box.label(text="Help:", icon='QUESTION')
            box.label(text="Use precision tools for exact")
            box.label(text="positioning and measurement")
            box.label(text="of your 3D models.")

# Parametric Shapes panel
class PRECISION_SURFACE_PT_ParametricShapes(PRECISION_SURFACE_PT_Base):
    """Panel for parametric shape creation"""
    bl_parent_id = "PRECISION_SURFACE_PT_Main"
    bl_label = "Parametric Shapes"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.precision_surface
        
        # Shape creation operators
        col = layout.column(align=True)
        col.label(text="Create Shapes:")
        row = col.row(align=True)
        row.operator("precision.create_parametric_cube", text="Cube", icon='MESH_CUBE')
        row.operator("precision.create_parametric_cylinder", text="Cylinder", icon='MESH_CYLINDER')
        
        # Parameter editing for selected object
        if context.active_object and "parametric_type" in context.active_object:
            box = layout.box()
            box.label(text=f"Edit {context.active_object.name}:")
            
            param_type = context.active_object["parametric_type"]
            
            if param_type == "cube":
                col = box.column(align=True)
                col.prop(context.active_object, '["parametric_width"]', text="Width")
                col.prop(context.active_object, '["parametric_depth"]', text="Depth")
                col.prop(context.active_object, '["parametric_height"]', text="Height")
                
                # Add update button
                box.operator("precision.update_parametric_object", text="Update Cube")
                
            elif param_type == "cylinder":
                col = box.column(align=True)
                col.prop(context.active_object, '["parametric_radius"]', text="Radius")
                col.prop(context.active_object, '["parametric_height"]', text="Height")
                col.prop(context.active_object, '["parametric_vertices"]', text="Vertices")
                
                # Add update button
                box.operator("precision.update_parametric_object", text="Update Cylinder")
        
        # Help text if enabled
        if props.show_help:
            box = layout.box()
            box.label(text="Help:", icon='QUESTION')
            box.label(text="Parametric shapes remain")
            box.label(text="editable after creation.")
            box.label(text="Select a shape to edit parameters.")

# Measurement panel
class PRECISION_SURFACE_PT_Measurements(PRECISION_SURFACE_PT_Base):
    """Panel for measurement tools"""
    bl_parent_id = "PRECISION_SURFACE_PT_Main"
    bl_label = "Measurements"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.precision_surface
        
        # Measurement tools
        col = layout.column(align=True)
        col.label(text="Add Measurements:")
        row = col.row(align=True)
        row.operator("precision.add_dimension", text="Distance", icon='DRIVER_DISTANCE')
        
        # Display measurement list if measurements exist
        if hasattr(scene, "precision_measurements") and scene.precision_measurements.measurements:
            box = layout.box()
            box.label(text="Current Measurements:")
            
            for i, measurement in enumerate(scene.precision_measurements.measurements):
                row = box.row()
                row.prop(measurement, "name", text="")
                row.prop(measurement, "is_visible", text="", icon='HIDE_OFF' if measurement.is_visible else 'HIDE_ON')
                
                # Add operator to remove measurement
                op = row.operator("precision.remove_measurement", text="", icon='X')
                op.index = i
        
        # Help text if enabled
        if props.show_help:
            box = layout.box()
            box.label(text="Help:", icon='QUESTION')
            box.label(text="Add measurements between")
            box.label(text="vertices, edges, or objects.")
            box.label(text="Select elements before adding.")

# Pattern panel
class PRECISION_SURFACE_PT_Patterns(PRECISION_SURFACE_PT_Base):
    """Panel for pattern creation tools"""
    bl_parent_id = "PRECISION_SURFACE_PT_Main"
    bl_label = "Patterns"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.precision_surface
        
        # Pattern creation tools
        col = layout.column(align=True)
        col.label(text="Create Patterns:")
        row = col.row(align=True)
        row.operator("pattern.linear_array", text="Linear", icon='LIGHTPROBE_GRID')
        row.operator("pattern.circular_array", text="Circular", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        
        col.separator()
        col.operator("pattern.honeycomb_pattern", text="Honeycomb", icon='MESH_GRID')
        
        # Help text if enabled
        if props.show_help:
            box = layout.box()
            box.label(text="Help:", icon='QUESTION')
            box.label(text="Create precise patterns by")
            box.label(text="duplicating selected objects.")
            box.label(text="Select object before creating.")

# Manufacturing panel
class PRECISION_SURFACE_PT_Manufacturing(PRECISION_SURFACE_PT_Base):
    """Panel for manufacturing tools"""
    bl_parent_id = "PRECISION_SURFACE_PT_Main"
    bl_label = "Manufacturing"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.precision_surface
        
        # Analysis tools
        box = layout.box()
        box.label(text="Analysis:")
        col = box.column(align=True)
        col.operator("manufacturing.check_printability", text="Check Printability", icon='MODIFIER')
        
        # Manufacturing preparation tools
        box = layout.box()
        box.label(text="Preparation:")
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("manufacturing.add_fillet", text="Add Fillet", icon='MESH_CIRCLE')
        row.operator("manufacturing.add_chamfer", text="Add Chamfer", icon='MESH_PLANE')
        
        # Export tools
        box = layout.box()
        box.label(text="Export:")
        col = box.column(align=True)
        col.operator("manufacturing.export_for_manufacturing", text="Export Model", icon='EXPORT')
        
        # Help text if enabled
        if props.show_help:
            box = layout.box()
            box.label(text="Help:", icon='QUESTION')
            box.label(text="Prepare models for manufacturing")
            box.label(text="with analysis and export tools.")
            box.label(text="Select model before using tools.")

# Tutorials panel
class PRECISION_SURFACE_PT_Tutorials(PRECISION_SURFACE_PT_Base):
    """Panel for tutorials and help"""
    bl_parent_id = "PRECISION_SURFACE_PT_Main"
    bl_label = "Tutorials & Help"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Tutorial sections
        box = layout.box()
        box.label(text="Getting Started:")
        col = box.column(align=True)
        col.operator("tutorial.precision_basics", text="Precision Basics", icon='HELP')
        col.operator("tutorial.parametric_modeling", text="Parametric Modeling", icon='HELP')
        
        box = layout.box()
        box.label(text="Advanced Topics:")
        col = box.column(align=True)
        col.operator("tutorial.pattern_creation", text="Pattern Creation", icon='HELP')
        col.operator("tutorial.manufacturing_prep", text="Manufacturing Prep", icon='HELP')
        
        # Documentation link
        layout.separator()
        layout.operator("wm.url_open", text="Online Documentation").url = "https://precisionsurface.docs"

# List of all classes to register
classes = [
    PRECISION_SURFACE_PT_Main,
    PRECISION_SURFACE_PT_PrecisionTools,
    PRECISION_SURFACE_PT_ParametricShapes,
    PRECISION_SURFACE_PT_Measurements,
    PRECISION_SURFACE_PT_Patterns,
    PRECISION_SURFACE_PT_Manufacturing,
    PRECISION_SURFACE_PT_Tutorials,
]

def register():
    """Register all panel classes"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all panel classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
