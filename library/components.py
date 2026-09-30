# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
import os
import math
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
)
from bpy.types import PropertyGroup, Operator, Panel

# Component categories
COMPONENT_CATEGORIES = [
    ('FASTENERS', "Fasteners", "Screws, bolts, nuts and other fasteners"),
    ('PANELS', "Panels", "Panels, plates and surfaces"),
    ('STRUCTURAL', "Structural", "Structural elements like beams and brackets"),
    ('VENTS', "Vents", "Vents, grills and air flow components"),
    ('ELECTRONIC', "Electronic", "Electronic components like connectors"),
    ('CUSTOM', "Custom", "Custom user components"),
]

# Component property group
class ComponentPropertyGroup(PropertyGroup):
    """Properties for a component in the library"""
    
    name: StringProperty(
        name="Name",
        description="Component name",
        default="Component"
    )
    
    description: StringProperty(
        name="Description",
        description="Component description",
        default=""
    )
    
    category: EnumProperty(
        name="Category",
        description="Component category",
        items=COMPONENT_CATEGORIES,
        default='FASTENERS'
    )
    
    thumbnail: StringProperty(
        name="Thumbnail",
        description="Path to component thumbnail image",
        default=""
    )
    
    blend_file: StringProperty(
        name="Blend File",
        description="Path to blend file containing the component",
        default=""
    )
    
    object_name: StringProperty(
        name="Object Name",
        description="Name of the object in the blend file",
        default=""
    )
    
    # Component parameters (simplified for example)
    has_parameters: BoolProperty(
        name="Has Parameters",
        description="Component has adjustable parameters",
        default=False
    )
    
    parameters: StringProperty(
        name="Parameters",
        description="JSON string of component parameters",
        default="{}"
    )

# Component library
class ComponentLibrary(PropertyGroup):
    """Collection of all components in the library"""
    
    components: CollectionProperty(
        name="Components",
        description="All components in the library",
        type=ComponentPropertyGroup
    )
    
    active_component_index: IntProperty(
        name="Active Component",
        description="Index of the active component",
        default=0
    )
    
    filter_category: EnumProperty(
        name="Filter Category",
        description="Filter components by category",
        items=COMPONENT_CATEGORIES + [('ALL', "All Categories", "Show all component categories")],
        default='ALL'
    )
    
    search_term: StringProperty(
        name="Search",
        description="Search components by name",
        default=""
    )

# Add Component operator
class LIBRARY_OT_add_component(Operator):
    """Add a component from the library to the scene"""
    bl_idname = "library.add_component"
    bl_label = "Add Component"
    bl_description = "Add the selected component to the scene"
    
    component_index: IntProperty(
        name="Component Index",
        description="Index of the component to add",
        default=0
    )
    
    def execute(self, context):
        # Get the component library
        library = context.scene.component_library
        
        # Check if the index is valid
        if self.component_index < 0 or self.component_index >= len(library.components):
            self.report({'ERROR'}, "Invalid component index")
            return {'CANCELLED'}
        
        # Get the component
        component = library.components[self.component_index]
        
        # Check if the component file exists
        if not component.blend_file or not os.path.exists(component.blend_file):
            self.report({'ERROR'}, f"Component file not found: {component.blend_file}")
            return {'CANCELLED'}
        
        # Load the component
        try:
            # Append the object from the blend file
            filepath = component.blend_file
            directory = os.path.join(filepath, "Object")
            filename = component.object_name
            
            bpy.ops.wm.append(
                filepath=os.path.join(directory, filename),
                directory=directory,
                filename=filename
            )
            
            # Get the newly added object
            if component.object_name in bpy.data.objects:
                obj = bpy.data.objects[component.object_name]
                
                # Place it at the 3D cursor
                obj.location = context.scene.cursor.location
                
                # Select it and make it active
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                # Mark it as a library component
                obj["is_library_component"] = True
                obj["component_name"] = component.name
                obj["component_category"] = component.category
                
                self.report({'INFO'}, f"Added component: {component.name}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to add component: {component.name}")
                return {'CANCELLED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error adding component: {str(e)}")
            return {'CANCELLED'}

# Create Component operator
class LIBRARY_OT_create_component(Operator):
    """Create a new component in the library from selected object"""
    bl_idname = "library.create_component"
    bl_label = "Create Component"
    bl_description = "Create a new component from the selected object"
    
    component_name: StringProperty(
        name="Name",
        description="Name for the new component",
        default="New Component"
    )
    
    component_description: StringProperty(
        name="Description",
        description="Description of the new component",
        default=""
    )
    
    component_category: EnumProperty(
        name="Category",
        description="Category for the new component",
        items=COMPONENT_CATEGORIES,
        default='CUSTOM'
    )
    
    def execute(self, context):
        # Check if an object is selected
        if not context.active_object:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
        
        # Get the object
        obj = context.active_object
        
        # Create a new component
        library = context.scene.component_library
        new_component = library.components.add()
        
        # Set component properties
        new_component.name = self.component_name
        new_component.description = self.component_description
        new_component.category = self.component_category
        new_component.object_name = obj.name
        
        # Set the index to the new component
        library.active_component_index = len(library.components) - 1
        
        # In a real addon, you would save the object to a library blend file here
        # and set the blend_file property to point to it
        
        self.report({'INFO'}, f"Created component: {self.component_name}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # When invoked, open a properties panel
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "component_name")
        layout.prop(self, "component_description")
        layout.prop(self, "component_category")

# Component Library panel
class LIBRARY_PT_component_library(Panel):
    """Panel for the component library"""
    bl_label = "Component Library"
    bl_idname = "LIBRARY_PT_component_library"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PrecisionSurface'
    bl_parent_id = "PRECISION_SURFACE_PT_Main"
    
    def draw(self, context):
        layout = self.layout
        library = context.scene.component_library
        
        # Search and filter
        row = layout.row(align=True)
        row.prop(library, "search_term", text="", icon='VIEWZOOM')
        row.prop(library, "filter_category", text="")
        
        # Component list
        box = layout.box()
        
        # Get filtered components
        filtered_components = []
        for i, component in enumerate(library.components):
            # Filter by category
            if library.filter_category != 'ALL' and component.category != library.filter_category:
                continue
            
            # Filter by search term
            if library.search_term and library.search_term.lower() not in component.name.lower():
                continue
            
            filtered_components.append((i, component))
        
        # Show components
        if filtered_components:
            for i, component in filtered_components:
                row = box.row()
                
                # Thumbnail (in a real addon, you'd show an actual thumbnail)
                row.label(text="", icon='MESH_CUBE')
                
                # Component info
                col = row.column()
                col.label(text=component.name)
                col.label(text=component.description)
                
                # Add button
                op = row.operator("library.add_component", text="", icon='ADD')
                op.component_index = i
        else:
            box.label(text="No components found")
        
        # Actions
        row = layout.row()
        row.operator("library.create_component", text="Create", icon='PLUS')
        row.operator("library.import_components", text="Import", icon='IMPORT')

# Import Components operator (stub)
class LIBRARY_OT_import_components(Operator):
    """Import components from another blend file"""
    bl_idname = "library.import_components"
    bl_label = "Import Components"
    bl_description = "Import components from another blend file"
    
    def execute(self, context):
        self.report({'INFO'}, "Import components functionality not yet implemented")
        return {'FINISHED'}

# List of all classes to register
classes = [
    ComponentPropertyGroup,
    ComponentLibrary,
    LIBRARY_OT_add_component,
    LIBRARY_OT_create_component,
    LIBRARY_OT_import_components,
    LIBRARY_PT_component_library,
]

def register():
    """Register all component library classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add component library to scene
    bpy.types.Scene.component_library = PointerProperty(type=ComponentLibrary)
    
    # Add some example components (in a real addon, these would be loaded from files)
    add_example_components()

def unregister():
    """Unregister all component library classes"""
    # Remove component library from scene
    del bpy.types.Scene.component_library
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

def add_example_components():
    """Add example components to the library"""
    # Skip if running in headless mode or the property doesn't exist yet
    if not hasattr(bpy.context.scene, "component_library"):
        return
    
    library = bpy.context.scene.component_library
    
    # Clear existing components
    library.components.clear()
    
    # Add example fasteners
    for size in ["M3", "M4", "M5", "M6"]:
        component = library.components.add()
        component.name = f"{size} Hex Bolt"
        component.description = f"Standard {size} hex head bolt"
        component.category = 'FASTENERS'
    
    for size in ["M3", "M4", "M5", "M6"]:
        component = library.components.add()
        component.name = f"{size} Hex Nut"
        component.description = f"Standard {size} hex nut"
        component.category = 'FASTENERS'
    
    # Add example panels
    panel_types = ["Flat", "Curved", "Perforated", "Ribbed"]
    for panel_type in panel_types:
        component = library.components.add()
        component.name = f"{panel_type} Panel"
        component.description = f"{panel_type.lower()} panel for enclosures"
        component.category = 'PANELS'
    
    # Add example vents
    vent_types = ["Hexagonal", "Linear", "Circular", "Rectangular"]
    for vent_type in vent_types:
        component = library.components.add()
        component.name = f"{vent_type} Vent"
        component.description = f"{vent_type.lower()} ventilation grill"
        component.category = 'VENTS'
