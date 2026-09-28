# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
import math
import bmesh
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import Operator
from mathutils import Vector, Matrix

from ..core import units

# Base class for precision operators
class PrecisionOperator(Operator):
    """Base class for all precision operators"""
    bl_options = {'REGISTER', 'UNDO'}
    
    # Common properties for all precision operators
    use_snapping: BoolProperty(
        name="Use Snapping",
        description="Enable precision snapping during the operation",
        default=True
    )
    
    precision_level: IntProperty(
        name="Precision Level",
        description="Level of precision for the operation",
        default=3,
        min=1,
        max=6
    )
    
    def get_precision_settings(self, context):
        """Get precision settings from addon preferences"""
        addon_prefs = context.preferences.addons["precision_surface"].preferences
        return {
            "precision_level": addon_prefs.precision_level,
            "unit_system": addon_prefs.default_unit_system,
        }

# Precise Move operator
class PRECISION_OT_precise_move(PrecisionOperator):
    """Move objects with precise control over position"""
    bl_idname = "precision.precise_move"
    bl_label = "Precise Move"
    bl_description = "Move objects with precise numerical control"
    
    # Distance values for each axis
    distance_x: FloatProperty(
        name="X",
        description="Distance to move along X axis",
        default=0.0,
        precision=4,
        unit='LENGTH'
    )
    
    distance_y: FloatProperty(
        name="Y",
        description="Distance to move along Y axis",
        default=0.0,
        precision=4,
        unit='LENGTH'
    )
    
    distance_z: FloatProperty(
        name="Z",
        description="Distance to move along Z axis",
        default=0.0,
        precision=4,
        unit='LENGTH'
    )
    
    use_local_space: BoolProperty(
        name="Local Space",
        description="Move in local space instead of world space",
        default=False
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        # Create transform vector
        move_vector = Vector((self.distance_x, self.distance_y, self.distance_z))
        
        # Apply transformation to each selected object
        for obj in selected_objects:
            if self.use_local_space:
                # Transform in local space
                local_vector = obj.matrix_world.to_3x3() @ move_vector
                obj.location += local_vector
            else:
                # Transform in world space
                obj.location += move_vector
        
        # Update the view
        context.view_layer.update()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(self, "distance_x")
        col.prop(self, "distance_y")
        col.prop(self, "distance_z")
        
        layout.prop(self, "use_local_space")
        layout.prop(self, "use_snapping")

# Precise Rotate operator
class PRECISION_OT_precise_rotate(PrecisionOperator):
    """Rotate objects with precise control over angles"""
    bl_idname = "precision.precise_rotate"
    bl_label = "Precise Rotate"
    bl_description = "Rotate objects with precise angular control"
    
    # Rotation angles for each axis
    angle_x: FloatProperty(
        name="X",
        description="Angle to rotate around X axis",
        default=0.0,
        precision=3,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    angle_y: FloatProperty(
        name="Y",
        description="Angle to rotate around Y axis",
        default=0.0,
        precision=3,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    angle_z: FloatProperty(
        name="Z",
        description="Angle to rotate around Z axis",
        default=0.0,
        precision=3,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    use_local_space: BoolProperty(
        name="Local Space",
        description="Rotate in local space instead of world space",
        default=True
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        # Create rotation vector (in radians)
        rotation = (self.angle_x, self.angle_y, self.angle_z)
        
        # Apply transformation to each selected object
        for obj in selected_objects:
            if self.use_local_space:
                # Rotate in local space
                obj.rotation_euler.rotate_axis('X', self.angle_x)
                obj.rotation_euler.rotate_axis('Y', self.angle_y)
                obj.rotation_euler.rotate_axis('Z', self.angle_z)
            else:
                # Rotate in world space (would need more complex implementation)
                # This is simplified
                obj.rotation_euler = (
                    obj.rotation_euler.x + self.angle_x,
                    obj.rotation_euler.y + self.angle_y,
                    obj.rotation_euler.z + self.angle_z
                )
        
        # Update the view
        context.view_layer.update()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(self, "angle_x")
        col.prop(self, "angle_y")
        col.prop(self, "angle_z")
        
        layout.prop(self, "use_local_space")
        layout.prop(self, "use_snapping")

# Precise Scale operator
class PRECISION_OT_precise_scale(PrecisionOperator):
    """Scale objects with precise control over dimensions"""
    bl_idname = "precision.precise_scale"
    bl_label = "Precise Scale"
    bl_description = "Scale objects with precise numerical control"
    
    # Scale factors for each axis
    scale_x: FloatProperty(
        name="X",
        description="Scale factor for X axis",
        default=1.0,
        min=0.01,
        precision=3
    )
    
    scale_y: FloatProperty(
        name="Y",
        description="Scale factor for Y axis",
        default=1.0,
        min=0.01,
        precision=3
    )
    
    scale_z: FloatProperty(
        name="Z",
        description="Scale factor for Z axis",
        default=1.0,
        min=0.01,
        precision=3
    )
    
    uniform_scale: BoolProperty(
        name="Uniform Scale",
        description="Apply uniform scaling to all axes",
        default=False
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        # Create scale vector
        if self.uniform_scale:
            scale_vector = Vector((self.scale_x, self.scale_x, self.scale_x))
        else:
            scale_vector = Vector((self.scale_x, self.scale_y, self.scale_z))
        
        # Apply transformation to each selected object
        for obj in selected_objects:
            obj.scale = obj.scale.element_wise() * scale_vector
        
        # Update the view
        context.view_layer.update()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "uniform_scale")
        
        col = layout.column(align=True)
        col.prop(self, "scale_x")
        
        if not self.uniform_scale:
            col.prop(self, "scale_y")
            col.prop(self, "scale_z")
        
        layout.prop(self, "use_snapping")

# Create parametric cube
class PRECISION_OT_create_parametric_cube(PrecisionOperator):
    """Create a cube with precise dimensions"""
    bl_idname = "precision.create_parametric_cube"
    bl_label = "Parametric Cube"
    bl_description = "Create a cube with precise dimensions"
    
    width: FloatProperty(
        name="Width",
        description="Width of the cube (X axis)",
        default=1.0,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    depth: FloatProperty(
        name="Depth",
        description="Depth of the cube (Y axis)",
        default=1.0,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    height: FloatProperty(
        name="Height",
        description="Height of the cube (Z axis)",
        default=1.0,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    location: FloatVectorProperty(
        name="Location",
        description="Position of the cube center",
        default=(0.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    def execute(self, context):
        # Create a cube with specified dimensions
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=self.location)
        obj = context.active_object
        
        # Set dimensions
        obj.scale.x = self.width / 2.0
        obj.scale.y = self.depth / 2.0
        obj.scale.z = self.height / 2.0
        
        # Apply scale to make the dimensions real
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Store parameter data for later editing
        obj["parametric_type"] = "cube"
        obj["parametric_width"] = self.width
        obj["parametric_depth"] = self.depth
        obj["parametric_height"] = self.height
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(self, "width")
        col.prop(self, "depth")
        col.prop(self, "height")
        
        col = layout.column(align=True)
        col.prop(self, "location")

# Create parametric cylinder
class PRECISION_OT_create_parametric_cylinder(PrecisionOperator):
    """Create a cylinder with precise dimensions"""
    bl_idname = "precision.create_parametric_cylinder"
    bl_label = "Parametric Cylinder"
    bl_description = "Create a cylinder with precise dimensions"
    
    radius: FloatProperty(
        name="Radius",
        description="Radius of the cylinder",
        default=0.5,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    height: FloatProperty(
        name="Height",
        description="Height of the cylinder",
        default=1.0,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    location: FloatVectorProperty(
        name="Location",
        description="Position of the cylinder center",
        default=(0.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    vertices: IntProperty(
        name="Vertices",
        description="Number of vertices in the cylinder base",
        default=32,
        min=3,
        max=256
    )
    
    def execute(self, context):
        # Create a cylinder with specified dimensions
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=self.vertices,
            radius=self.radius,
            depth=self.height,
            location=self.location
        )
        obj = context.active_object
        
        # Store parameter data for later editing
        obj["parametric_type"] = "cylinder"
        obj["parametric_radius"] = self.radius
        obj["parametric_height"] = self.height
        obj["parametric_vertices"] = self.vertices
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(self, "radius")
        col.prop(self, "height")
        col.prop(self, "vertices")
        
        col = layout.column(align=True)
        col.prop(self, "location")

# Add dimension measurement
class PRECISION_OT_add_dimension(PrecisionOperator):
    """Add a dimension measurement between two points"""
    bl_idname = "precision.add_dimension"
    bl_label = "Add Dimension"
    bl_description = "Add a dimension measurement between two points"
    
    start_point: FloatVectorProperty(
        name="Start Point",
        description="Starting point of the dimension",
        default=(0.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    end_point: FloatVectorProperty(
        name="End Point",
        description="Ending point of the dimension",
        default=(1.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    dimension_type: EnumProperty(
        name="Type",
        description="Type of dimension measurement",
        items=[
            ('DISTANCE', "Distance", "Measure direct distance"),
            ('ALIGNED', "Aligned", "Measure aligned distance"),
            ('AXIS', "Axis", "Measure distance along an axis"),
        ],
        default='DISTANCE'
    )
    
    axis: EnumProperty(
        name="Axis",
        description="Axis for axis-aligned dimension",
        items=[
            ('X', "X", "X axis"),
            ('Y', "Y", "Y axis"),
            ('Z', "Z", "Z axis"),
        ],
        default='X'
    )
    
    def execute(self, context):
        from ..core.measurements import add_distance_measurement
        
        # Add the measurement
        measurement = add_distance_measurement(
            context.scene, 
            self.start_point, 
            self.end_point,
            f"{self.dimension_type} Dimension"
        )
        
        # Update viewport
        context.area.tag_redraw()
        
        self.report({'INFO'}, "Dimension added")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Try to use selected vertices or objects as points
        if context.mode == 'EDIT_MESH':
            mesh = context.edit_object.data
            bm = bmesh.from_edit_mesh(mesh)
            selected_verts = [v for v in bm.verts if v.select]
            
            if len(selected_verts) >= 2:
                # Get global coordinates
                world_matrix = context.edit_object.matrix_world
                self.start_point = world_matrix @ selected_verts[0].co
                self.end_point = world_matrix @ selected_verts[1].co
        elif len(context.selected_objects) >= 2:
            self.start_point = context.selected_objects[0].location
            self.end_point = context.selected_objects[1].location
        
        # Open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "dimension_type")
        
        if self.dimension_type == 'AXIS':
            layout.prop(self, "axis", expand=True)
        
        col = layout.column(align=True)
        col.prop(self, "start_point")
        col.prop(self, "end_point")
        
        layout.prop(self, "precision_level")

# List of all classes to register
classes = [
    PRECISION_OT_precise_move,
    PRECISION_OT_precise_rotate,
    PRECISION_OT_precise_scale,
    PRECISION_OT_create_parametric_cube,
    PRECISION_OT_create_parametric_cylinder,
    PRECISION_OT_add_dimension,
]

def register():
    """Register all precision operator classes"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all precision operator classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
