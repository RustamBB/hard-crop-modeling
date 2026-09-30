# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
import os
import json
import csv
import math
from mathutils import Vector

# Export utilities

def export_object_data(obj, filepath, include_modifiers=True):
    """Export object data to a JSON file"""
    # Create data dictionary
    data = {
        "name": obj.name,
        "type": obj.type,
        "location": [obj.location.x, obj.location.y, obj.location.z],
        "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
        "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
        "dimensions": [obj.dimensions.x, obj.dimensions.y, obj.dimensions.z]
    }
    
    # Include additional data for mesh objects
    if obj.type == 'MESH':
        # Get mesh data
        if include_modifiers:
            # Get evaluated mesh (with modifiers applied)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            eval_obj = obj.evaluated_get(depsgraph)
            mesh = eval_obj.data
        else:
            mesh = obj.data
        
        # Add mesh data
        data["mesh"] = {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "materials": [mat.name for mat in mesh.materials] if mesh.materials else []
        }
    
    # Write data to file
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error exporting object data: {str(e)}")
        return False

def export_measurements(scene, filepath):
    """Export measurements to a CSV file"""
    try:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Name', 'Type', 'Value', 'Unit'])
            
            # Write measurement data
            if hasattr(scene, "precision_measurements"):
                for measurement in scene.precision_measurements.measurements:
                    if measurement.measurement_type == 'DISTANCE':
                        # Calculate distance
                        start = Vector(measurement.start_point)
                        end = Vector(measurement.end_point)
                        distance = (end - start).length
                        
                        # Format value based on precision
                        value = round(distance, measurement.precision)
                        
                        # Get unit string
                        unit = "m"  # Default unit
                        
                        # Write row
                        writer.writerow([measurement.name, 'DISTANCE', value, unit])
                    
                    elif measurement.measurement_type == 'ANGLE':
                        # Calculate angle
                        center = Vector(measurement.center_point)
                        point1 = Vector(measurement.point1)
                        point2 = Vector(measurement.point2)
                        
                        vec1 = point1 - center
                        vec2 = point2 - center
                        
                        # Normalize vectors
                        if vec1.length > 0:
                            vec1 = vec1.normalized()
                        if vec2.length > 0:
                            vec2 = vec2.normalized()
                        
                        # Calculate angle
                        dot_product = min(max(vec1.dot(vec2), -1.0), 1.0)  # Clamp to avoid precision errors
                        angle = math.acos(dot_product)
                        
                        # Convert to degrees
                        angle_degrees = math.degrees(angle)
                        
                        # Format value based on precision
                        value = round(angle_degrees, measurement.precision)
                        
                        # Write row
                        writer.writerow([measurement.name, 'ANGLE', value, 'degrees'])
        
        return True
    except Exception as e:
        print(f"Error exporting measurements: {str(e)}")
        return False

def export_bill_of_materials(objects, filepath):
    """Export a bill of materials for the selected objects"""
    try:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Item', 'Name', 'Type', 'Quantity', 'Dimensions'])
            
            # Group objects by name and type
            materials = {}
            
            for obj in objects:
                key = (obj.name, obj.type)
                
                # Calculate dimensions for mesh objects
                dimensions = ""
                if obj.type == 'MESH':
                    dim = obj.dimensions
                    dimensions = f"{dim.x:.2f} x {dim.y:.2f} x {dim.z:.2f}"
                
                if key in materials:
                    materials[key]['quantity'] += 1
                else:
                    materials[key] = {
                        'name': obj.name,
                        'type': obj.type,
                        'quantity': 1,
                        'dimensions': dimensions
                    }
            
            # Write materials
            for i, (_, material) in enumerate(materials.items(), 1):
                writer.writerow([
                    i,
                    material['name'],
                    material['type'],
                    material['quantity'],
                    material['dimensions']
                ])
        
        return True
    except Exception as e:
        print(f"Error exporting bill of materials: {str(e)}")
        return False

def export_technical_drawing(obj, filepath, views=None):
    """Export a technical drawing of the object"""
    # This is a placeholder - a real implementation would generate
    # proper orthographic views and dimensioning for technical drawings
    
    # Define which views to export if not specified
    if views is None:
        views = ['TOP', 'FRONT', 'RIGHT']
    
    try:
        # Create a text report as a simple stand-in
        with open(filepath, 'w') as f:
            f.write(f"Technical Drawing: {obj.name}\n")
            f.write("=" * 40 + "\n\n")
            
            f.write("Object Information:\n")
            f.write(f"- Type: {obj.type}\n")
            f.write(f"- Dimensions: {obj.dimensions.x:.2f} x {obj.dimensions.y:.2f} x {obj.dimensions.z:.2f}\n")
            
            f.write("\nViews Included:\n")
            for view in views:
                f.write(f"- {view} view\n")
            
            f.write("\nNote: This is a placeholder for a technical drawing.\n")
            f.write("In a full implementation, this would generate proper 2D drawings with dimensions.\n")
        
        return True
    except Exception as e:
        print(f"Error exporting technical drawing: {str(e)}")
        return False

def export_manufacturing_notes(obj, filepath, manufacturing_method):
    """Export manufacturing notes for the object"""
    try:
        with open(filepath, 'w') as f:
            f.write(f"Manufacturing Notes: {obj.name}\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Manufacturing Method: {manufacturing_method}\n\n")
            
            if manufacturing_method == '3D_PRINTING':
                f.write("3D Printing Recommendations:\n")
                f.write("- Minimum wall thickness: 1.0 mm\n")
                f.write("- Suggested print orientation: Bottom flat on build plate\n")
                f.write("- Support material: Required for overhangs > 45 degrees\n")
                f.write("- Infill percentage: 20% recommended\n")
            
            elif manufacturing_method == 'CNC_MACHINING':
                f.write("CNC Machining Recommendations:\n")
                f.write("- Minimum internal radius: 1.5 mm (based on tool diameter)\n")
                f.write("- Minimum feature size: 1.0 mm\n")
                f.write("- Maximum depth-to-width ratio for pockets: 4:1\n")
                f.write("- Surface finish: Specify if critical\n")
            
            elif manufacturing_method == 'INJECTION_MOLDING':
                f.write("Injection Molding Recommendations:\n")
                f.write("- Minimum wall thickness: 0.8 mm\n")
                f.write("- Draft angle: 1-3 degrees required on all surfaces\n")
                f.write("- Avoid undercuts or plan for side actions\n")
                f.write("- Uniform wall thickness recommended\n")
            
            f.write("\nMaterial Recommendations:\n")
            if manufacturing_method == '3D_PRINTING':
                f.write("- PLA: Good for general purpose, dimensional accuracy\n")
                f.write("- PETG: Better temperature resistance, more durable\n")
                f.write("- ABS: Good for mechanical parts, heat resistant\n")
            elif manufacturing_method == 'CNC_MACHINING':
                f.write("- Aluminum: Good for general purpose, lightweight\n")
                f.write("- Stainless Steel: For greater strength and corrosion resistance\n")
                f.write("- Delrin/Acetal: For plastic parts with good machinability\n")
            elif manufacturing_method == 'INJECTION_MOLDING':
                f.write("- ABS: Good for structural parts\n")
                f.write("- Polypropylene: Good chemical resistance\n")
                f.write("- Nylon: Strong and durable\n")
        
        return True
    except Exception as e:
        print(f"Error exporting manufacturing notes: {str(e)}")
        return False
