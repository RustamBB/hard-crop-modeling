# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Validation utilities

def check_mesh_is_manifold(obj):
    """Check if a mesh is manifold (watertight)"""
    # Get mesh data (apply modifiers temporarily for analysis)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Check for non-manifold elements
    non_manifold_edges = [e for e in bm.edges if not e.is_manifold]
    boundary_edges = [e for e in bm.edges if e.is_boundary]
    
    # Calculate total edge count for percentage
    total_edges = len(bm.edges)
    non_manifold_percent = (len(non_manifold_edges) / total_edges * 100) if total_edges > 0 else 0
    boundary_percent = (len(boundary_edges) / total_edges * 100) if total_edges > 0 else 0
    
    # Clean up
    bm.free()
    
    # Return results
    return {
        "is_manifold": len(non_manifold_edges) == 0 and len(boundary_edges) == 0,
        "non_manifold_edges": len(non_manifold_edges),
        "boundary_edges": len(boundary_edges),
        "total_edges": total_edges,
        "non_manifold_percent": non_manifold_percent,
        "boundary_percent": boundary_percent
    }

def check_minimum_wall_thickness(obj, min_thickness=1.0):
    """Check if mesh has any walls thinner than the minimum thickness"""
    # Get mesh data (apply modifiers temporarily for analysis)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Ensure mesh has proper topology data
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    # Find thin areas (simplified approach)
    thin_walls = []
    
    # Check each edge with exactly two connected faces
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            f1, f2 = edge.link_faces
            
            # Find vertices not part of the shared edge
            v1_list = [v for v in f1.verts if v not in edge.verts]
            v2_list = [v for v in f2.verts if v not in edge.verts]
            
            if v1_list and v2_list:
                # For each vertex in the first face, find closest vertex in second face
                for v1 in v1_list:
                    min_distance = float('inf')
                    for v2 in v2_list:
                        distance = (v1.co - v2.co).length
                        min_distance = min(min_distance, distance)
                    
                    # If distance is less than minimum thickness, add to thin walls
                    if min_distance < min_thickness:
                        # Convert to world space for accuracy
                        thickness = min_distance * obj.scale.x  # Simplified scaling
                        thin_walls.append({
                            "edge_index": edge.index,
                            "thickness": thickness,
                            "percent_below": (min_thickness - thickness) / min_thickness * 100
                        })
    
    # Clean up
    bm.free()
    
    # Return results
    return {
        "all_walls_thick_enough": len(thin_walls) == 0,
        "thin_walls": thin_walls,
        "min_thickness_required": min_thickness,
        "total_thin_areas": len(thin_walls)
    }

def check_overhangs(obj, max_angle=45.0, build_direction=Vector((0.0, 0.0, 1.0))):
    """Check for overhanging faces that exceed the maximum angle from the build direction"""
    # Get mesh data (apply modifiers temporarily for analysis)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Convert max angle to radians
    max_angle_rad = math.radians(max_angle)
    
    # Transform build direction to object space
    world_to_obj = obj.matrix_world.inverted()
    build_direction_obj = world_to_obj.to_3x3() @ build_direction
    build_direction_obj.normalize()
    
    # Find overhanging faces
    overhangs = []
    
    for face in bm.faces:
        # Calculate angle between face normal and build direction
        angle = math.acos(min(max(face.normal.dot(build_direction_obj), -1.0), 1.0))
        
        # If normal points downward, angle will be > 90°
        # We're interested in the angle from horizontal, so:
        if angle > math.pi / 2:
            angle = math.pi - angle
        
        # Check if angle exceeds our overhang threshold
        if angle > (math.pi / 2 - max_angle_rad):
            angle_degrees = math.degrees(angle)
            overhangs.append({
                "face_index": face.index,
                "angle": angle_degrees,
                "area": face.calc_area()
            })
    
    # Calculate total mesh area and overhang percentage
    total_area = sum(f.calc_area() for f in bm.faces)
    overhang_area = sum(o["area"] for o in overhangs)
    overhang_percent = (overhang_area / total_area * 100) if total_area > 0 else 0
    
    # Clean up
    bm.free()
    
    # Return results
    return {
        "no_overhangs": len(overhangs) == 0,
        "overhangs": overhangs,
        "max_angle_allowed": max_angle,
        "total_overhang_faces": len(overhangs),
        "overhang_area_percent": overhang_percent
    }

def check_mesh_intersections(obj):
    """Check for self-intersections in the mesh"""
    # Get mesh data (apply modifiers temporarily for analysis)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # This is a simplified approach - proper intersection detection would use
    # more sophisticated algorithms like a BVH tree
    
    # Find potentially intersecting faces
    intersecting_pairs = []
    
    # For a simple check, we'll look for faces that might have intersecting bounding boxes
    for i, face1 in enumerate(bm.faces):
        # Calculate face1 bounding box
        verts1 = [v.co for v in face1.verts]
        min1 = Vector((
            min(v.x for v in verts1),
            min(v.y for v in verts1),
            min(v.z for v in verts1)
        ))
        max1 = Vector((
            max(v.x for v in verts1),
            max(v.y for v in verts1),
            max(v.z for v in verts1)
        ))
        
        for j in range(i + 1, len(bm.faces)):
            face2 = bm.faces[j]
            
            # Skip adjacent faces
            if any(v in face1.verts for v in face2.verts):
                continue
            
            # Calculate face2 bounding box
            verts2 = [v.co for v in face2.verts]
            min2 = Vector((
                min(v.x for v in verts2),
                min(v.y for v in verts2),
                min(v.z for v in verts2)
            ))
            max2 = Vector((
                max(v.x for v in verts2),
                max(v.y for v in verts2),
                max(v.z for v in verts2)
            ))
            
            # Check if bounding boxes overlap
            if (min1.x <= max2.x and max1.x >= min2.x and
                min1.y <= max2.y and max1.y >= min2.y and
                min1.z <= max2.z and max1.z >= min2.z):
                
                # This is a potential intersection - a real check would do a triangle-triangle
                # intersection test here, but we'll simplify for this example
                intersecting_pairs.append({
                    "face1_index": face1.index,
                    "face2_index": face2.index,
                    "severity": "potential"  # A real check would categorize severity
                })
    
    # Clean up
    bm.free()
    
    # Return results
    return {
        "no_intersections": len(intersecting_pairs) == 0,
        "intersecting_pairs": intersecting_pairs,
        "total_intersections": len(intersecting_pairs)
    }

def check_draft_angles(obj, min_draft_angle=1.0, draw_direction=Vector((0.0, 1.0, 0.0))):
    """Check if mesh has sufficient draft angles for molding/casting"""
    # Get mesh data (apply modifiers temporarily for analysis)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Convert min draft angle to radians
    min_draft_angle_rad = math.radians(min_draft_angle)
    
    # Transform draw direction to object space
    world_to_obj = obj.matrix_world.inverted()
    draw_direction_obj = world_to_obj.to_3x3() @ draw_direction
    draw_direction_obj.normalize()
    
    # Find faces with insufficient draft
    insufficient_draft = []
    
    for face in bm.faces:
        # Calculate angle between face normal and draw direction
        angle = math.acos(min(max(abs(face.normal.dot(draw_direction_obj)), -1.0), 1.0))
        
        # Draft angle is 90° - this angle
        draft_angle = math.pi/2 - angle
        
        # Check if draft angle is less than minimum
        if draft_angle < min_draft_angle_rad:
            draft_angle_degrees = math.degrees(draft_angle)
            insufficient_draft.append({
                "face_index": face.index,
                "draft_angle": draft_angle_degrees,
                "required_angle": min_draft_angle,
                "area": face.calc_area()
            })
    
    # Calculate total mesh area and insufficient draft percentage
    total_area = sum(f.calc_area() for f in bm.faces)
    insufficient_area = sum(i["area"] for i in insufficient_draft)
    insufficient_percent = (insufficient_area / total_area * 100) if total_area > 0 else 0
    
    # Clean up
    bm.free()
    
    # Return results
    return {
        "all_drafts_sufficient": len(insufficient_draft) == 0,
        "insufficient_draft": insufficient_draft,
        "min_draft_required": min_draft_angle,
        "total_insufficient_faces": len(insufficient_draft),
        "insufficient_area_percent": insufficient_percent
    }

def check_undercuts(obj, draw_direction=Vector((0.0, 1.0, 0.0))):
    """Check if mesh has undercuts that would prevent molding/casting"""
    # Get mesh data (apply modifiers temporarily for analysis)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Transform draw direction to object space
    world_to_obj = obj.matrix_world.inverted()
    draw_direction_obj = world_to_obj.to_3x3() @ draw_direction
    draw_direction_obj.normalize()
    
    # Find undercut faces
    undercuts = []
    
    for face in bm.faces:
        # Calculate dot product with draw direction
        dot = face.normal.dot(draw_direction_obj)
        
        # If dot product is positive, face points in similar direction as draw direction
        # If dot product is negative, face points in opposite direction
        if dot < 0:
            undercuts.append({
                "face_index": face.index,
                "severity": abs(dot),  # How opposed to draw direction
                "area": face.calc_area()
            })
    
    # Calculate total mesh area and undercut percentage
    total_area = sum(f.calc_area() for f in bm.faces)
    undercut_area = sum(u["area"] for u in undercuts)
    undercut_percent = (undercut_area / total_area * 100) if total_area > 0 else 0
    
    # Clean up
    bm.free()
    
    # Return results
    return {
        "no_undercuts": len(undercuts) == 0,
        "undercuts": undercuts,
        "total_undercut_faces": len(undercuts),
        "undercut_area_percent": undercut_percent
    }

def check_structural_stability(obj, min_support_area=0.25):
    """Check if object has sufficient base for structural stability"""
    # Get mesh data (apply modifiers temporarily for analysis)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.data
    
    # Create BMesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # We'll assume Z is up and check for faces pointing downward
    down_direction = Vector((0.0, 0.0, -1.0))
    
    # Transform to object space
    world_to_obj = obj.matrix_world.inverted()
    down_direction_obj = world_to_obj.to_3x3() @ down_direction
    down_direction_obj.normalize()
    
    # Find faces that could be part of the base
    base_faces = []
    
    for face in bm.faces:
        # Calculate dot product with down direction
        dot = face.normal.dot(down_direction_obj)
        
        # If dot product is positive, face points somewhat downward
        if dot > 0.7:  # Roughly 45° from downward
            base_faces.append({
                "face_index": face.index,
                "area": face.calc_area()
            })
    
    # Calculate total base area
    base_area = sum(f["area"] for f in base_faces)
    
    # Calculate total mesh surface area
    total_area = sum(f.calc_area() for f in bm.faces)
    
    # Calculate bounding box volume for comparison
    bbox_corners = [Vector(v) for v in obj.bound_box]
    bbox_dims = (
        max(v.x for v in bbox_corners) - min(v.x for v in bbox_corners),
        max(v.y for v in bbox_corners) - min(v.y for v in bbox_corners),
        max(v.z for v in bbox_corners) - min(v.z for v in bbox_corners)
    )
    bbox_base_area = bbox_dims[0] * bbox_dims[1]
    
    # Calculate ratio of base area to bounding box base area
    base_ratio = base_area / bbox_base_area if bbox_base_area > 0 else 0
    
    # Clean up
    bm.free()
    
    # Return results
    return {
        "is_stable": base_ratio >= min_support_area,
        "base_area": base_area,
        "total_area": total_area,
        "base_to_bbox_ratio": base_ratio,
        "min_support_required": min_support_area,
        "base_faces": len(base_faces)
    }
