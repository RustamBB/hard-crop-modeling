# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
import math
import bmesh
from mathutils import Vector, Matrix

# Geometry helper functions

def get_object_dimensions(obj):
    """Get the actual dimensions of an object in world space"""
    corners = [Vector(corner) for corner in obj.bound_box]
    corners_world = [obj.matrix_world @ corner for corner in corners]
    
    # Calculate min and max coordinates
    min_x = min(corner.x for corner in corners_world)
    max_x = max(corner.x for corner in corners_world)
    min_y = min(corner.y for corner in corners_world)
    max_y = max(corner.y for corner in corners_world)
    min_z = min(corner.z for corner in corners_world)
    max_z = max(corner.z for corner in corners_world)
    
    # Calculate dimensions
    dimensions = Vector((
        max_x - min_x,
        max_y - min_y,
        max_z - min_z
    ))
    
    return dimensions

def get_face_center(obj, face_index):
    """Get the center of a face in world space"""
    # Create a BMesh from the object
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    
    # Ensure face indices are up to date
    bm.faces.ensure_lookup_table()
    
    # Get the face
    if face_index < len(bm.faces):
        face = bm.faces[face_index]
        center = face.calc_center_median()
        
        # Transform to world space
        center = obj.matrix_world @ center
        
        # Clean up if needed
        if obj.mode != 'EDIT':
            bm.free()
        
        return center
    else:
        # Clean up if needed
        if obj.mode != 'EDIT':
            bm.free()
        
        return None

def get_edge_length(obj, edge_index):
    """Get the length of an edge in world space"""
    # Create a BMesh from the object
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    
    # Ensure edge indices are up to date
    bm.edges.ensure_lookup_table()
    
    # Get the edge
    if edge_index < len(bm.edges):
        edge = bm.edges[edge_index]
        
        # Get the vertices in world space
        v1 = obj.matrix_world @ edge.verts[0].co
        v2 = obj.matrix_world @ edge.verts[1].co
        
        # Calculate length
        length = (v2 - v1).length
        
        # Clean up if needed
        if obj.mode != 'EDIT':
            bm.free()
        
        return length
    else:
        # Clean up if needed
        if obj.mode != 'EDIT':
            bm.free()
        
        return None

def get_vertex_coordinates(obj, vertex_index):
    """Get the coordinates of a vertex in world space"""
    # Create a BMesh from the object
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    
    # Ensure vertex indices are up to date
    bm.verts.ensure_lookup_table()
    
    # Get the vertex
    if vertex_index < len(bm.verts):
        vert = bm.verts[vertex_index]
        
        # Transform to world space
        coords = obj.matrix_world @ vert.co
        
        # Clean up if needed
        if obj.mode != 'EDIT':
            bm.free()
        
        return coords
    else:
        # Clean up if needed
        if obj.mode != 'EDIT':
            bm.free()
        
        return None

def get_selected_vertices(obj):
    """Get a list of selected vertices in world space"""
    # Create a BMesh from the object
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    
    # Get selected vertices
    selected_verts = [obj.matrix_world @ v.co for v in bm.verts if v.select]
    
    # Clean up if needed
    if obj.mode != 'EDIT':
        bm.free()
    
    return selected_verts

def get_selected_edges(obj):
    """Get a list of selected edges (as vertex pairs) in world space"""
    # Create a BMesh from the object
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    
    # Get selected edges
    selected_edges = []
    for e in bm.edges:
        if e.select:
            v1 = obj.matrix_world @ e.verts[0].co
            v2 = obj.matrix_world @ e.verts[1].co
            selected_edges.append((v1, v2))
    
    # Clean up if needed
    if obj.mode != 'EDIT':
        bm.free()
    
    return selected_edges

def get_selected_faces(obj):
    """Get a list of selected faces (as vertex lists) in world space"""
    # Create a BMesh from the object
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    
    # Get selected faces
    selected_faces = []
    for f in bm.faces:
        if f.select:
            face_verts = [obj.matrix_world @ v.co for v in f.verts]
            selected_faces.append(face_verts)
    
    # Clean up if needed
    if obj.mode != 'EDIT':
        bm.free()
    
    return selected_faces

def create_face_normals_visualization(obj, length=0.1):
    """Create a visualization of face normals as small lines"""
    # Create a BMesh from the object
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    
    # Create a new mesh for the normals
    normal_mesh = bpy.data.meshes.new(f"{obj.name}_Normals")
    normal_obj = bpy.data.objects.new(f"{obj.name}_Normals", normal_mesh)
    
    # Link to the same collection as the original object
    for collection in bpy.data.collections:
        if obj.name in collection.objects:
            collection.objects.link(normal_obj)
            break
    else:
        # If not found in any collection, link to the active collection
        bpy.context.collection.objects.link(normal_obj)
    
    # Create vertices and edges for each face normal
    verts = []
    edges = []
    
    for face in bm.faces:
        # Calculate face center in world space
        center = obj.matrix_world @ face.calc_center_median()
        
        # Calculate normal direction in world space
        normal = (obj.matrix_world.to_3x3() @ face.normal).normalized()
        
        # Calculate the end point of the normal line
        end_point = center + normal * length
        
        # Add vertices and edge
        verts.extend([center, end_point])
        edges.append((len(verts) - 2, len(verts) - 1))
    
    # Create the mesh
    normal_mesh.from_pydata(verts, edges, [])
    normal_mesh.update()
    
    # Clean up if needed
    if obj.mode != 'EDIT':
        bm.free()
    
    return normal_obj

def calculate_angle_between_faces(obj, face1_index, face2_index):
    """Calculate the angle between two faces in radians"""
    # Create a BMesh from the object
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    
    # Ensure face indices are up to date
    bm.faces.ensure_lookup_table()
    
    # Get the faces
    if face1_index < len(bm.faces) and face2_index < len(bm.faces):
        face1 = bm.faces[face1_index]
        face2 = bm.faces[face2_index]
        
        # Get normals in world space
        normal1 = (obj.matrix_world.to_3x3() @ face1.normal).normalized()
        normal2 = (obj.matrix_world.to_3x3() @ face2.normal).normalized()
        
        # Calculate the angle between normals
        angle = normal1.angle(normal2)
        
        # Clean up if needed
        if obj.mode != 'EDIT':
            bm.free()
        
        return angle
    else:
        # Clean up if needed
        if obj.mode != 'EDIT':
            bm.free()
        
        return None

def calculate_distance_between_objects(obj1, obj2):
    """Calculate the minimum distance between two objects"""
    # Get the matrices for transformations
    mat1 = obj1.matrix_world
    mat2 = obj2.matrix_world
    
    # Get all vertices of both objects
    verts1 = [mat1 @ Vector(v) for v in obj1.bound_box]
    verts2 = [mat2 @ Vector(v) for v in obj2.bound_box]
    
    # Find the minimum distance
    min_distance = float('inf')
    
    for v1 in verts1:
        for v2 in verts2:
            distance = (v2 - v1).length
            min_distance = min(min_distance, distance)
    
    return min_distance

def create_line_between_points(point1, point2, name="Line"):
    """Create a line mesh between two points"""
    # Create a new mesh
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    # Link to the active collection
    bpy.context.collection.objects.link(obj)
    
    # Create the mesh data
    mesh.from_pydata([point1, point2], [(0, 1)], [])
    mesh.update()
    
    return obj

def create_arrow_between_points(start, end, name="Arrow", head_size=0.1):
    """Create an arrow mesh pointing from start to end"""
    # Calculate direction and length
    direction = end - start
    length = direction.length
    
    if length < 0.0001:  # Avoid division by zero
        return None
    
    direction = direction / length  # Normalize
    
    # Create points for the arrow
    shaft_end = end - direction * head_size * 2  # Shaft ends before the head
    
    # Create a basis with Z aligned to the arrow direction
    up = Vector((0, 0, 1))
    if abs(direction.dot(up)) > 0.99:
        up = Vector((0, 1, 0))
    
    right = direction.cross(up).normalized()
    up = right.cross(direction).normalized()
    
    # Create arrow head points
    p1 = shaft_end + right * head_size - direction * head_size
    p2 = shaft_end - right * head_size - direction * head_size
    p3 = shaft_end + up * head_size - direction * head_size
    p4 = shaft_end - up * head_size - direction * head_size
    
    # Create vertices and edges
    verts = [start, shaft_end, end, p1, p2, p3, p4]
    edges = [(0, 1), (1, 2), (2, 3), (2, 4), (2, 5), (2, 6)]
    
    # Create a new mesh
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    # Link to the active collection
    bpy.context.collection.objects.link(obj)
    
    # Create the mesh data
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    
    return obj

def align_object_to_face(obj, target, face_index):
    """Align an object to a face of another object"""
    # Create a BMesh from the target object
    if target.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(target.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(target.data)
    
    # Ensure face indices are up to date
    bm.faces.ensure_lookup_table()
    
    # Get the face
    if face_index < len(bm.faces):
        face = bm.faces[face_index]
        
        # Get face normal and center in world space
        normal = (target.matrix_world.to_3x3() @ face.normal).normalized()
        center = target.matrix_world @ face.calc_center_median()
        
        # Create a rotation matrix to align the object's Z axis with the face normal
        obj_forward = Vector((0, 0, 1))
        rotation_axis = obj_forward.cross(normal)
        
        if rotation_axis.length > 0.001:  # Avoid zero-length rotation axis
            rotation_axis.normalize()
            angle = obj_forward.angle(normal)
            rotation = Matrix.Rotation(angle, 4, rotation_axis)
        else:
            # If axes are parallel or anti-parallel
            if obj_forward.dot(normal) < 0:
                # Anti-parallel: rotate 180° around X axis
                rotation = Matrix.Rotation(math.pi, 4, 'X')
            else:
                # Parallel: no rotation needed
                rotation = Matrix.Identity(4)
        
        # Set the object's position and rotation
        obj.location = center
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rotation.to_quaternion()
        
        # Clean up if needed
        if target.mode != 'EDIT':
            bm.free()
        
        return True
    else:
        # Clean up if needed
        if target.mode != 'EDIT':
            bm.free()
        
        return False
