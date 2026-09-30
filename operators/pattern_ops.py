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

# Base class for pattern operators
class PatternOperator(Operator):
    """Base class for all pattern generation operators"""
    bl_options = {'REGISTER', 'UNDO'}
    
    pattern_name: StringProperty(
        name="Name",
        description="Name for the generated pattern",
        default="Pattern"
    )
    
    def apply_modifiers(self, obj):
        """Apply all modifiers to an object"""
        # Store active object
        original_active = bpy.context.view_layer.objects.active
        
        # Set object as active
        bpy.context.view_layer.objects.active = obj
        
        # Apply all modifiers
        for modifier in obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        
        # Restore original active object
        bpy.context.view_layer.objects.active = original_active

# Linear Array operator
class PATTERN_OT_linear_array(PatternOperator):
    """Create a linear array of objects with precise spacing"""
    bl_idname = "pattern.linear_array"
    bl_label = "Linear Array"
    bl_description = "Create a linear array of objects with precise spacing"
    
    count: IntProperty(
        name="Count",
        description="Number of items in the array",
        default=3,
        min=2,
        max=100
    )
    
    distance: FloatProperty(
        name="Distance",
        description="Distance between array items",
        default=1.0,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    direction: EnumProperty(
        name="Direction",
        description="Direction of the array",
        items=[
            ('X', "X", "Along X axis"),
            ('Y', "Y", "Along Y axis"),
            ('Z', "Z", "Along Z axis"),
            ('CUSTOM', "Custom", "Custom direction vector"),
        ],
        default='X'
    )
    
    custom_direction: FloatVectorProperty(
        name="Custom Direction",
        description="Custom direction vector for the array",
        default=(1.0, 0.0, 0.0),
        precision=3,
        subtype='XYZ'
    )
    
    offset_even_items: BoolProperty(
        name="Offset Even Items",
        description="Apply offset to even-numbered items for alternating patterns",
        default=False
    )
    
    even_offset: FloatVectorProperty(
        name="Even Item Offset",
        description="Offset to apply to even-numbered items",
        default=(0.0, 0.0, 0.0),
        precision=3,
        subtype='XYZ'
    )
    
    use_relative_offset: BoolProperty(
        name="Relative Offset",
        description="Calculate offset relative to object size",
        default=True
    )
    
    merge_result: BoolProperty(
        name="Merge Result",
        description="Merge all objects into a single mesh when finished",
        default=False
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        original_obj = context.active_object
        
        if original_obj not in selected_objects:
            self.report({'ERROR'}, "Active object must be selected")
            return {'CANCELLED'}
        
        # Determine direction vector
        direction_vector = Vector((1.0, 0.0, 0.0))  # Default X direction
        
        if self.direction == 'X':
            direction_vector = Vector((1.0, 0.0, 0.0))
        elif self.direction == 'Y':
            direction_vector = Vector((0.0, 1.0, 0.0))
        elif self.direction == 'Z':
            direction_vector = Vector((0.0, 0.0, 1.0))
        else:  # CUSTOM
            custom_dir = Vector(self.custom_direction)
            if custom_dir.length > 0:
                direction_vector = custom_dir.normalized()
        
        # Calculate offset
        if self.use_relative_offset:
            # Use bounding box dimensions for relative offset
            dimensions = original_obj.dimensions
            direction_size = abs(dimensions.dot(direction_vector))
            offset_distance = direction_size * self.distance
        else:
            offset_distance = self.distance
        
        # Create array
        new_objects = []
        for i in range(self.count):
            if i == 0:
                # First item is the original
                new_obj = original_obj
            else:
                # Create duplicate
                new_obj = original_obj.copy()
                new_obj.data = original_obj.data.copy()
                context.collection.objects.link(new_obj)
            
            # Calculate position
            offset = direction_vector * offset_distance * i
            new_obj.location = original_obj.location + offset
            
            # Apply offset to even items if enabled
            if self.offset_even_items and i % 2 == 1:
                new_obj.location += Vector(self.even_offset)
            
            new_objects.append(new_obj)
        
        # Merge result if requested
        if self.merge_result and len(new_objects) > 1:
            # Select all objects in the array
            bpy.ops.object.select_all(action='DESELECT')
            for obj in new_objects:
                obj.select_set(True)
            
            # Set the last object as active
            context.view_layer.objects.active = new_objects[-1]
            
            # Join objects
            bpy.ops.object.join()
            
            # Rename the result
            context.active_object.name = self.pattern_name
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "pattern_name")
        
        col = layout.column(align=True)
        col.prop(self, "count")
        col.prop(self, "distance")
        
        layout.prop(self, "direction")
        if self.direction == 'CUSTOM':
            layout.prop(self, "custom_direction")
        
        layout.prop(self, "use_relative_offset")
        
        box = layout.box()
        box.prop(self, "offset_even_items")
        if self.offset_even_items:
            box.prop(self, "even_offset")
        
        layout.prop(self, "merge_result")

# Circular Array operator
class PATTERN_OT_circular_array(PatternOperator):
    """Create a circular array of objects"""
    bl_idname = "pattern.circular_array"
    bl_label = "Circular Array"
    bl_description = "Create a circular array of objects around a center point"
    
    count: IntProperty(
        name="Count",
        description="Number of items in the array",
        default=8,
        min=2,
        max=100
    )
    
    radius: FloatProperty(
        name="Radius",
        description="Radius of the circular array",
        default=1.0,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    center_point: FloatVectorProperty(
        name="Center",
        description="Center point of the circular array",
        default=(0.0, 0.0, 0.0),
        precision=4,
        subtype='XYZ'
    )
    
    axis: EnumProperty(
        name="Axis",
        description="Axis of rotation for the circular array",
        items=[
            ('X', "X", "Around X axis"),
            ('Y', "Y", "Around Y axis"),
            ('Z', "Z", "Around Z axis"),
            ('CUSTOM', "Custom", "Custom axis vector"),
        ],
        default='Z'
    )
    
    custom_axis: FloatVectorProperty(
        name="Custom Axis",
        description="Custom axis of rotation",
        default=(0.0, 0.0, 1.0),
        precision=3,
        subtype='XYZ'
    )
    
    rotation_offset: FloatProperty(
        name="Rotation Offset",
        description="Offset rotation for the entire array",
        default=0.0,
        precision=3,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    align_to_circle: BoolProperty(
        name="Align to Circle",
        description="Align objects to face away from the center",
        default=True
    )
    
    merge_result: BoolProperty(
        name="Merge Result",
        description="Merge all objects into a single mesh when finished",
        default=False
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        original_obj = context.active_object
        
        if original_obj not in selected_objects:
            self.report({'ERROR'}, "Active object must be selected")
            return {'CANCELLED'}
        
        # Determine axis vector
        axis_vector = Vector((0.0, 0.0, 1.0))  # Default Z axis
        
        if self.axis == 'X':
            axis_vector = Vector((1.0, 0.0, 0.0))
        elif self.axis == 'Y':
            axis_vector = Vector((0.0, 1.0, 0.0))
        elif self.axis == 'Z':
            axis_vector = Vector((0.0, 0.0, 1.0))
        else:  # CUSTOM
            custom_axis = Vector(self.custom_axis)
            if custom_axis.length > 0:
                axis_vector = custom_axis.normalized()
        
        # Calculate angle step
        angle_step = 2.0 * math.pi / self.count
        
        # Create array
        new_objects = []
        center_point = Vector(self.center_point)
        
        for i in range(self.count):
            if i == 0:
                # First item is the original
                new_obj = original_obj
            else:
                # Create duplicate
                new_obj = original_obj.copy()
                new_obj.data = original_obj.data.copy()
                context.collection.objects.link(new_obj)
            
            # Calculate rotation angle
            angle = angle_step * i + self.rotation_offset
            
            # Calculate position around circle
            # Create rotation matrix around the specified axis
            rot_mat = Matrix.Rotation(angle, 4, axis_vector)
            
            # Calculate vector from center to original object
            original_offset = original_obj.location - center_point
            
            # If radius is specified, use it to set the distance from center
            if self.radius > 0.001:
                # Project original offset onto the plane perpendicular to the axis
                axis_component = original_offset.project(axis_vector)
                plane_component = original_offset - axis_component
                
                # Normalize and scale to the specified radius
                if plane_component.length > 0.001:
                    plane_component = plane_component.normalized() * self.radius
                else:
                    # If original is on the axis, use a default direction
                    if axis_vector == Vector((0.0, 0.0, 1.0)):
                        plane_component = Vector((self.radius, 0.0, 0.0))
                    else:
                        # Create a vector perpendicular to the axis
                        temp = Vector((1.0, 0.0, 0.0))
                        if abs(temp.dot(axis_vector)) > 0.9:
                            temp = Vector((0.0, 1.0, 0.0))
                        plane_component = temp.cross(axis_vector).normalized() * self.radius
                
                # Combine the axis component with the plane component
                radial_vector = plane_component
            else:
                radial_vector = original_offset
            
            # Rotate the radial vector
            rotated_vector = rot_mat @ radial_vector
            
            # Set the new position
            new_obj.location = center_point + rotated_vector
            
            # Align object orientation if requested
            if self.align_to_circle:
                # Look from object toward center (or away from center)
                look_direction = (new_obj.location - center_point).normalized()
                
                # Create a rotation that aligns object's forward axis with look direction
                # This assumes that object's "forward" is along the Y axis
                # Convert look direction to rotation
                up_vector = axis_vector
                rotation = look_direction.to_track_quat('Y', 'Z')
                
                # Apply rotation
                new_obj.rotation_mode = 'QUATERNION'
                new_obj.rotation_quaternion = rotation
            
            new_objects.append(new_obj)
        
        # Merge result if requested
        if self.merge_result and len(new_objects) > 1:
            # Select all objects in the array
            bpy.ops.object.select_all(action='DESELECT')
            for obj in new_objects:
                obj.select_set(True)
            
            # Set the last object as active
            context.view_layer.objects.active = new_objects[-1]
            
            # Join objects
            bpy.ops.object.join()
            
            # Rename the result
            context.active_object.name = self.pattern_name
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Try to determine center from selection
        if len(context.selected_objects) > 1:
            # Calculate average position
            avg_pos = Vector((0.0, 0.0, 0.0))
            for obj in context.selected_objects:
                avg_pos += obj.location
            avg_pos /= len(context.selected_objects)
            
            self.center_point = avg_pos
        
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "pattern_name")
        
        col = layout.column(align=True)
        col.prop(self, "count")
        col.prop(self, "radius")
        
        col = layout.column(align=True)
        col.prop(self, "center_point")
        
        layout.prop(self, "axis")
        if self.axis == 'CUSTOM':
            layout.prop(self, "custom_axis")
        
        layout.prop(self, "rotation_offset")
        layout.prop(self, "align_to_circle")
        layout.prop(self, "merge_result")

# Honeycomb Pattern operator
class PATTERN_OT_honeycomb_pattern(PatternOperator):
    """Create a honeycomb pattern of hexagons"""
    bl_idname = "pattern.honeycomb_pattern"
    bl_label = "Honeycomb Pattern"
    bl_description = "Create a honeycomb pattern of hexagons"
    
    rows: IntProperty(
        name="Rows",
        description="Number of rows in the honeycomb pattern",
        default=5,
        min=1,
        max=50
    )
    
    columns: IntProperty(
        name="Columns",
        description="Number of columns in the honeycomb pattern",
        default=5,
        min=1,
        max=50
    )
    
    cell_size: FloatProperty(
        name="Cell Size",
        description="Size of each hexagonal cell (distance between opposite sides)",
        default=1.0,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    wall_thickness: FloatProperty(
        name="Wall Thickness",
        description="Thickness of cell walls",
        default=0.1,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    height: FloatProperty(
        name="Height",
        description="Height of the honeycomb pattern",
        default=0.2,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    orientation: EnumProperty(
        name="Orientation",
        description="Orientation of the honeycomb pattern",
        items=[
            ('XY', "XY Plane", "Create on XY plane (Z up)"),
            ('XZ', "XZ Plane", "Create on XZ plane (Y up)"),
            ('YZ', "YZ Plane", "Create on YZ plane (X up)"),
        ],
        default='XY'
    )
    
    def execute(self, context):
        # Calculate honeycomb metrics
        # Hexagon geometry: for a hexagon with distance 'size' between opposite sides,
        # the distance between vertices is 'size / cos(30°)' or 'size / 0.866'
        inner_radius = self.cell_size / 2.0  # Distance from center to middle of side
        outer_radius = inner_radius / 0.866  # Distance from center to vertex
        
        # Calculate spacing between centers
        horiz_spacing = inner_radius * 2  # Distance between adjacent column centers
        vert_spacing = outer_radius * 1.5  # Distance between adjacent row centers (75% overlap)
        
        # Create empty mesh and object
        mesh = bpy.data.meshes.new(self.pattern_name)
        obj = bpy.data.objects.new(self.pattern_name, mesh)
        
        # Link object to collection
        context.collection.objects.link(obj)
        
        # Make it active
        context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Create BMesh
        bm = bmesh.new()
        
        # Create vertices and faces for each cell
        for row in range(self.rows):
            for col in range(self.columns):
                # Calculate cell center
                # Offset every other row by half a column
                x_offset = (horiz_spacing / 2) if (row % 2) else 0
                x = col * horiz_spacing + x_offset
                y = row * vert_spacing
                z = 0
                
                # Adjust coordinates based on orientation
                if self.orientation == 'XY':
                    center = Vector((x, y, z))
                elif self.orientation == 'XZ':
                    center = Vector((x, z, y))
                else:  # YZ
                    center = Vector((z, x, y))
                
                # Create hexagon vertices
                verts = []
                for i in range(6):
                    angle = 2 * math.pi * i / 6 + math.pi / 6  # Start at 30°
                    vx = outer_radius * math.cos(angle)
                    vy = outer_radius * math.sin(angle)
                    vz = 0
                    
                    # Adjust vertex coordinates based on orientation
                    if self.orientation == 'XY':
                        vertex = center + Vector((vx, vy, vz))
                    elif self.orientation == 'XZ':
                        vertex = center + Vector((vx, vz, vy))
                    else:  # YZ
                        vertex = center + Vector((vz, vx, vy))
                    
                    verts.append(bm.verts.new(vertex))
                
                # Create face
                bm.faces.new(verts)
        
        # Apply extruded height
        faces = bm.faces[:]  # Get all faces
        
        # Set extrusion direction based on orientation
        if self.orientation == 'XY':
            extrude_vec = Vector((0, 0, self.height))
        elif self.orientation == 'XZ':
            extrude_vec = Vector((0, self.height, 0))
        else:  # YZ
            extrude_vec = Vector((self.height, 0, 0))
        
        # Extrude faces
        result = bmesh.ops.extrude_face_region(bm, geom=faces)
        extruded_verts = [v for v in result["geom"] if isinstance(v, bmesh.types.BMVert)]
        
        # Translate extruded verts
        bmesh.ops.translate(bm, vec=extrude_vec, verts=extruded_verts)
        
        # Finalize BMesh and update mesh
        bm.to_mesh(mesh)
        bm.free()
        
        # Apply wall thickness using solidify modifier
        solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify.thickness = self.wall_thickness
        solidify.offset = 0.0  # Center the thickness
        
        # Set smooth shading
        bpy.ops.object.shade_smooth()
        
        # Update mesh
        mesh.update()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "pattern_name")
        
        col = layout.column(align=True)
        col.prop(self, "rows")
        col.prop(self, "columns")
        
        col = layout.column(align=True)
        col.prop(self, "cell_size")
        col.prop(self, "wall_thickness")
        col.prop(self, "height")
        
        layout.prop(self, "orientation", expand=True)

# List of all classes to register
classes = [
    PATTERN_OT_linear_array,
    PATTERN_OT_circular_array,
    PATTERN_OT_honeycomb_pattern,
]

def register():
    """Register all pattern operator classes"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all pattern operator classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
