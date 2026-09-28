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

# Base class for manufacturing operators
class ManufacturingOperator(Operator):
    """Base class for all manufacturing-related operators"""
    bl_options = {'REGISTER', 'UNDO'}

# Check Printability operator
class MANUFACTURING_OT_check_printability(ManufacturingOperator):
    """Check if a model is suitable for 3D printing"""
    bl_idname = "manufacturing.check_printability"
    bl_label = "Check Printability"
    bl_description = "Analyze model for 3D printing issues"
    
    min_wall_thickness: FloatProperty(
        name="Minimum Wall Thickness",
        description="Minimum acceptable wall thickness (mm)",
        default=1.0,
        min=0.1,
        max=10.0,
        precision=2,
        unit='LENGTH'
    )
    
    max_overhang_angle: FloatProperty(
        name="Maximum Overhang Angle",
        description="Maximum overhang angle before supports are needed (degrees)",
        default=45.0,
        min=0.0,
        max=90.0,
        precision=1,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    check_manifold: BoolProperty(
        name="Check Manifold",
        description="Check if the mesh is watertight (manifold)",
        default=True
    )
    
    check_overlapping: BoolProperty(
        name="Check Overlapping Geometry",
        description="Check for overlapping faces",
        default=True
    )
    
    check_overhangs: BoolProperty(
        name="Check Overhangs",
        description="Check for overhanging faces that might need support",
        default=True
    )
    
    check_wall_thickness: BoolProperty(
        name="Check Wall Thickness",
        description="Check for walls thinner than minimum thickness",
        default=True
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
        
        if not mesh_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        # Store results for report
        issues_found = False
        report_lines = []
        
        # Check each selected mesh object
        for obj in mesh_objects:
            report_lines.append(f"Analyzing {obj.name}:")
            
            # Get mesh data (apply modifiers temporarily for analysis)
            depsgraph = context.evaluated_depsgraph_get()
            temp_mesh = obj.evaluated_get(depsgraph).data
            
            # Create BMesh for analysis
            bm = bmesh.new()
            bm.from_mesh(temp_mesh)
            bm.faces.ensure_lookup_table()
            
            # 1. Check if mesh is manifold (watertight)
            if self.check_manifold:
                non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
                if non_manifold_edges:
                    issues_found = True
                    report_lines.append(f"  - Non-manifold edges found: {len(non_manifold_edges)}")
                else:
                    report_lines.append("  - Mesh is manifold (watertight): OK")
            
            # 2. Check for overlapping geometry
            if self.check_overlapping:
                # This is a simplified check - in a real addon, you'd use more sophisticated algorithms
                overlapping = False
                for face in bm.faces:
                    center = face.calc_center_median()
                    normal = face.normal
                    
                    # Cast ray in both directions of the normal
                    for direction in [normal, -normal]:
                        hits = []
                        # Simple ray cast to find potential overlaps
                        for other_face in bm.faces:
                            if other_face == face:
                                continue
                            # This is a simplified check - in a real addon, you'd use proper ray-triangle intersection
                            if other_face.normal.dot(direction) < 0:  # Only check faces pointing opposite to ray
                                other_center = other_face.calc_center_median()
                                if (other_center - center).normalized().dot(direction) > 0.9:
                                    hits.append(other_face)
                        
                        if len(hits) > 0:
                            overlapping = True
                            break
                    
                    if overlapping:
                        break
                
                if overlapping:
                    issues_found = True
                    report_lines.append("  - Overlapping geometry detected")
                else:
                    report_lines.append("  - No overlapping geometry: OK")
            
            # 3. Check for overhangs
            if self.check_overhangs:
                # Convert degrees to radians for comparison
                max_angle_rad = math.radians(self.max_overhang_angle)
                
                # Define build direction (typically Z-up)
                build_direction = Vector((0.0, 0.0, 1.0))
                
                # Transform to object space
                world_to_obj = obj.matrix_world.inverted()
                build_direction_obj = world_to_obj.to_3x3() @ build_direction
                build_direction_obj.normalize()
                
                # Check each face
                overhang_faces = []
                for face in bm.faces:
                    # Calculate angle between face normal and build direction
                    angle = math.acos(min(max(face.normal.dot(build_direction_obj), -1.0), 1.0))
                    
                    # If normal points downward, angle will be > 90°
                    # We're interested in the angle from horizontal, so:
                    if angle > math.pi / 2:
                        angle = math.pi - angle
                    
                    # Check if angle exceeds our overhang threshold
                    if angle > (math.pi / 2 - max_angle_rad):
                        overhang_faces.append(face)
                
                if overhang_faces:
                    issues_found = True
                    report_lines.append(f"  - Overhang issues found: {len(overhang_faces)} faces exceed {self.max_overhang_angle}°")
                else:
                    report_lines.append("  - No problematic overhangs: OK")
            
            # 4. Check wall thickness
            if self.check_wall_thickness:
                # This is a very simplified check - real wall thickness checking requires more complex algorithms
                # A proper implementation would use ray casting from face to opposite face
                thin_edges = []
                
                for edge in bm.edges:
                    if len(edge.link_faces) == 2:  # Only check edges with 2 connected faces
                        f1, f2 = edge.link_faces
                        
                        # Calculate distance between opposite vertices
                        v1 = None
                        v2 = None
                        
                        # Find vertices that are not part of the shared edge
                        for v in f1.verts:
                            if v not in edge.verts:
                                v1 = v
                                break
                        
                        for v in f2.verts:
                            if v not in edge.verts:
                                v2 = v
                                break
                        
                        if v1 and v2:
                            # Calculate distance
                            distance = (v1.co - v2.co).length
                            
                            if distance < self.min_wall_thickness:
                                thin_edges.append(edge)
                
                if thin_edges:
                    issues_found = True
                    report_lines.append(f"  - Thin walls found: {len(thin_edges)} areas below {self.min_wall_thickness}mm")
                else:
                    report_lines.append(f"  - Wall thickness above {self.min_wall_thickness}mm: OK")
            
            # Clean up
            bm.free()
        
        # Show report
        self.report({'INFO' if not issues_found else 'WARNING'}, "Printability check complete")
        
        # Create a text report
        report_text = bpy.data.texts.new("PrintabilityReport.txt")
        report_text.write("\n".join(report_lines))
        
        # Open text editor and show report
        context.window_manager.printability_report = report_text.name
        
        if issues_found:
            # In a real addon, you would mark problematic areas in the 3D view
            return {'FINISHED'}
        else:
            return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Checks:")
        box.prop(self, "check_manifold")
        box.prop(self, "check_overlapping")
        box.prop(self, "check_overhangs")
        box.prop(self, "check_wall_thickness")
        
        box = layout.box()
        box.label(text="Parameters:")
        box.prop(self, "min_wall_thickness")
        box.prop(self, "max_overhang_angle")

# Add Fillet operator
class MANUFACTURING_OT_add_fillet(ManufacturingOperator):
    """Add fillets to edges for manufacturing"""
    bl_idname = "manufacturing.add_fillet"
    bl_label = "Add Fillet"
    bl_description = "Add rounded fillets to edges for manufacturing"
    
    radius: FloatProperty(
        name="Radius",
        description="Fillet radius",
        default=0.1,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    segments: IntProperty(
        name="Segments",
        description="Number of segments in the fillet",
        default=4,
        min=1,
        max=32
    )
    
    limit_angle: FloatProperty(
        name="Limit Angle",
        description="Minimum angle between faces for an edge to be filleted",
        default=math.radians(30.0),
        min=0.0,
        max=math.radians(180.0),
        precision=1,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    apply_modifier: BoolProperty(
        name="Apply Modifier",
        description="Apply the bevel modifier after creation",
        default=False
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
        
        if not mesh_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        # Apply fillet to each selected mesh object
        for obj in mesh_objects:
            # Add bevel modifier
            bevel = obj.modifiers.new(name="ManufacturingFillet", type='BEVEL')
            bevel.limit_method = 'ANGLE'
            bevel.angle_limit = self.limit_angle
            bevel.width = self.radius
            bevel.segments = self.segments
            bevel.profile = 0.5  # Circular profile
            
            # Apply modifier if requested
            if self.apply_modifier:
                # Set as active object
                context.view_layer.objects.active = obj
                
                # Apply modifier
                bpy.ops.object.modifier_apply(modifier=bevel.name)
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(self, "radius")
        col.prop(self, "segments")
        col.prop(self, "limit_angle")
        
        layout.prop(self, "apply_modifier")

# Add Chamfer operator
class MANUFACTURING_OT_add_chamfer(ManufacturingOperator):
    """Add chamfers to edges for manufacturing"""
    bl_idname = "manufacturing.add_chamfer"
    bl_label = "Add Chamfer"
    bl_description = "Add angled chamfers to edges for manufacturing"
    
    width: FloatProperty(
        name="Width",
        description="Chamfer width",
        default=0.1,
        min=0.001,
        precision=4,
        unit='LENGTH'
    )
    
    segments: IntProperty(
        name="Segments",
        description="Number of segments in the chamfer",
        default=1,
        min=1,
        max=8
    )
    
    limit_angle: FloatProperty(
        name="Limit Angle",
        description="Minimum angle between faces for an edge to be chamfered",
        default=math.radians(30.0),
        min=0.0,
        max=math.radians(180.0),
        precision=1,
        subtype='ANGLE',
        unit='ROTATION'
    )
    
    apply_modifier: BoolProperty(
        name="Apply Modifier",
        description="Apply the bevel modifier after creation",
        default=False
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
        
        if not mesh_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        # Apply chamfer to each selected mesh object
        for obj in mesh_objects:
            # Add bevel modifier
            bevel = obj.modifiers.new(name="ManufacturingChamfer", type='BEVEL')
            bevel.limit_method = 'ANGLE'
            bevel.angle_limit = self.limit_angle
            bevel.width = self.width
            bevel.segments = self.segments
            bevel.profile = 1.0  # Straight profile for chamfer
            
            # Apply modifier if requested
            if self.apply_modifier:
                # Set as active object
                context.view_layer.objects.active = obj
                
                # Apply modifier
                bpy.ops.object.modifier_apply(modifier=bevel.name)
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(self, "width")
        col.prop(self, "segments")
        col.prop(self, "limit_angle")
        
        layout.prop(self, "apply_modifier")

# Export for Manufacturing operator
class MANUFACTURING_OT_export_for_manufacturing(ManufacturingOperator):
    """Export model in formats suitable for manufacturing"""
    bl_idname = "manufacturing.export_for_manufacturing"
    bl_label = "Export for Manufacturing"
    bl_description = "Export model in formats suitable for manufacturing"
    
    export_format: EnumProperty(
        name="Format",
        description="File format to export",
        items=[
            ('STL', "STL", "Standard format for 3D printing"),
            ('OBJ', "OBJ", "Wavefront OBJ format"),
            ('3DS', "3DS", "3D Studio format"),
            ('FBX', "FBX", "Autodesk FBX format"),
            ('GLTF', "glTF", "GL Transmission Format"),
        ],
        default='STL'
    )
    
    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply all modifiers before export",
        default=True
    )
    
    export_materials: BoolProperty(
        name="Export Materials",
        description="Include material data in export (if format supports it)",
        default=False
    )
    
    scale_factor: FloatProperty(
        name="Scale Factor",
        description="Scale factor to apply during export (1.0 = no scaling)",
        default=1.0,
        min=0.001,
        max=1000.0,
        precision=3
    )
    
    def execute(self, context):
        # Get selected objects
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
        
        if not mesh_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}
        
        # Determine file extension
        if self.export_format == 'STL':
            extension = ".stl"
            export_func = bpy.ops.export_mesh.stl
        elif self.export_format == 'OBJ':
            extension = ".obj"
            export_func = bpy.ops.export_scene.obj
        elif self.export_format == '3DS':
            extension = ".3ds"
            export_func = bpy.ops.export_scene.autodesk_3ds
        elif self.export_format == 'FBX':
            extension = ".fbx"
            export_func = bpy.ops.export_scene.fbx
        elif self.export_format == 'GLTF':
            extension = ".gltf"
            export_func = bpy.ops.export_scene.gltf
        
        # Get export path from Blender's file browser
        filepath = bpy.path.ensure_ext(bpy.data.filepath, extension)
        
        if not filepath:
            filepath = "//untitled" + extension
        
        # Export settings dictionary (common settings)
        export_settings = {
            'filepath': filepath,
            'use_selection': True,
            'global_scale': self.scale_factor
        }
        
        # Format-specific settings
        if self.export_format == 'STL':
            export_settings.update({
                'use_mesh_modifiers': self.apply_modifiers,
                'use_selection': True,
                'global_scale': self.scale_factor,
                'ascii': False,  # Binary format is more compact
            })
        elif self.export_format == 'OBJ':
            export_settings.update({
                'use_mesh_modifiers': self.apply_modifiers,
                'use_selection': True,
                'use_materials': self.export_materials,
                'global_scale': self.scale_factor,
            })
        elif self.export_format == 'FBX':
            export_settings.update({
                'use_mesh_modifiers': self.apply_modifiers,
                'use_selection': True,
                'embed_textures': self.export_materials,
                'global_scale': self.scale_factor,
            })
        
        # Execute export with settings
        export_func(**export_settings)
        
        self.report({'INFO'}, f"Exported {len(mesh_objects)} objects to {filepath}")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "export_format")
        layout.prop(self, "apply_modifiers")
        
        if self.export_format in ['OBJ', 'FBX', '3DS', 'GLTF']:
            layout.prop(self, "export_materials")
        
        layout.prop(self, "scale_factor")

# Register printability report property
def get_printability_report(self):
    return getattr(self, "_printability_report", "")

def set_printability_report(self, value):
    self._printability_report = value

# List of all classes to register
classes = [
    MANUFACTURING_OT_check_printability,
    MANUFACTURING_OT_add_fillet,
    MANUFACTURING_OT_add_chamfer,
    MANUFACTURING_OT_export_for_manufacturing,
]

def register():
    """Register all manufacturing operator classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register printability report property
    bpy.types.WindowManager.printability_report = bpy.props.StringProperty(
        name="Printability Report",
        description="Name of the text data-block containing the printability report",
        get=get_printability_report,
        set=set_printability_report
    )

def unregister():
    """Unregister all manufacturing operator classes"""
    # Unregister printability report property
    del bpy.types.WindowManager.printability_report
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
