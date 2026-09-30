# This file is part of the PrecisionSurface Addon for Blender 3D
# PrecisionSurface: Bridge the gap between art and engineering

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty

# Base tutorial operator
class TutorialOperator(Operator):
    """Base class for tutorial operators"""
    bl_options = {'REGISTER', 'INTERNAL'}
    
    # Store tutorial state
    current_step: IntProperty(
        name="Current Step",
        description="Current tutorial step",
        default=0
    )
    
    def cancel(self, context):
        """Clean up when tutorial is cancelled"""
        # Remove any tutorial-specific UI or highlighting
        context.area.tag_redraw()
        return {'CANCELLED'}

# Precision Basics tutorial
class TUTORIAL_OT_precision_basics(TutorialOperator):
    """Interactive tutorial for precision modeling basics"""
    bl_idname = "tutorial.precision_basics"
    bl_label = "Precision Basics Tutorial"
    bl_description = "Learn the basics of precision modeling tools"
    
    # Tutorial steps content
    tutorial_steps = [
        {
            "title": "Welcome to Precision Basics",
            "text": "This tutorial will guide you through the basic precision modeling tools.\n"
                    "Click 'Next' to continue or 'Cancel' to exit the tutorial at any time.",
            "action": None
        },
        {
            "title": "Setting Up the Workspace",
            "text": "First, let's set up our workspace for precision modeling.\n"
                    "1. Make sure the PrecisionSurface tab is visible in the sidebar.\n"
                    "2. Set the display mode to 'BASIC' for this tutorial.",
            "action": "setup_workspace"
        },
        {
            "title": "Creating a Precise Cube",
            "text": "Let's create a cube with precise dimensions:\n"
                    "1. Click on the 'Parametric Cube' button in the Parametric Shapes panel.\n"
                    "2. Set Width = 2, Depth = 3, Height = 1.\n"
                    "3. Click OK to create the cube.",
            "action": "create_cube"
        },
        {
            "title": "Precise Movement",
            "text": "Now let's move the cube with precision:\n"
                    "1. Select the cube if not already selected.\n"
                    "2. Click on the 'Move' button in the Precision Tools panel.\n"
                    "3. Set X = 1, Y = 0, Z = 0.\n"
                    "4. Click OK to move the cube.",
            "action": "move_cube"
        },
        {
            "title": "Adding Dimensions",
            "text": "Let's add a dimension to measure our model:\n"
                    "1. Click on the 'Distance' button in the Measurements panel.\n"
                    "2. Set the start and end points or use selected vertices.\n"
                    "3. Click OK to add the dimension.",
            "action": "add_dimension"
        },
        {
            "title": "Precision Basics Complete",
            "text": "Congratulations! You've completed the Precision Basics tutorial.\n"
                    "You've learned how to:\n"
                    "- Create parametric objects with precise dimensions\n"
                    "- Move objects with precision\n"
                    "- Add dimension measurements\n\n"
                    "Click 'Finish' to exit the tutorial.",
            "action": None
        }
    ]
    
    def execute(self, context):
        # Execute current step action if defined
        current_step_data = self.tutorial_steps[self.current_step]
        action = current_step_data.get("action")
        
        if action:
            method = getattr(self, action, None)
            if method:
                method(context)
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Reset tutorial state
        self.current_step = 0
        
        # Open the tutorial dialog
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        
        # Get current step data
        current_step_data = self.tutorial_steps[self.current_step]
        
        # Draw title
        layout.label(text=current_step_data["title"], icon='HELP')
        
        # Draw content
        for line in current_step_data["text"].split("\n"):
            layout.label(text=line)
        
        # Draw navigation buttons
        row = layout.row()
        
        # Previous button (except on first step)
        if self.current_step > 0:
            row.operator("tutorial.previous_step", text="Previous")
        else:
            row.label(text="")
        
        # Next/Finish button
        if self.current_step < len(self.tutorial_steps) - 1:
            row.operator("tutorial.next_step", text="Next")
        else:
            row.operator("tutorial.finish", text="Finish")
    
    # Step action methods
    def setup_workspace(self, context):
        """Set up the workspace for the tutorial"""
        # Set display mode to basic
        context.scene.precision_surface.display_mode = 'BASIC'
        
        # Ensure help is shown
        context.scene.precision_surface.show_help = True
        
        # Switch to object mode if in edit mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
    
    def create_cube(self, context):
        """Guide the user to create a parametric cube"""
        # Highlight the Parametric Shapes panel
        # This would typically involve some UI hinting mechanism
        pass
    
    def move_cube(self, context):
        """Guide the user to move the cube with precision"""
        # Highlight the Precision Move button
        # This would typically involve some UI hinting mechanism
        pass
    
    def add_dimension(self, context):
        """Guide the user to add a dimension measurement"""
        # Highlight the Add Dimension button
        # This would typically involve some UI hinting mechanism
        pass

# Parametric Modeling tutorial
class TUTORIAL_OT_parametric_modeling(TutorialOperator):
    """Interactive tutorial for parametric modeling"""
    bl_idname = "tutorial.parametric_modeling"
    bl_label = "Parametric Modeling Tutorial"
    bl_description = "Learn how to use parametric modeling tools"
    
    # Tutorial steps content (simplified for example)
    tutorial_steps = [
        {
            "title": "Welcome to Parametric Modeling",
            "text": "This tutorial will guide you through parametric modeling techniques.\n"
                    "Click 'Next' to continue or 'Cancel' to exit the tutorial at any time.",
            "action": None
        },
        {
            "title": "What is Parametric Modeling?",
            "text": "Parametric modeling lets you create objects with editable parameters.\n"
                    "This means you can change dimensions and properties even after creation.\n"
                    "It's perfect for precision engineering and design iteration.",
            "action": None
        },
        {
            "title": "Parametric Modeling Complete",
            "text": "Congratulations! You've completed the introduction to Parametric Modeling.\n"
                    "In a full tutorial, you would learn much more about:\n"
                    "- Creating complex parametric objects\n"
                    "- Linking parameters between objects\n"
                    "- Using constraints to control geometry\n\n"
                    "Click 'Finish' to exit the tutorial.",
            "action": None
        }
    ]
    
    def execute(self, context):
        # Execute current step action if defined
        current_step_data = self.tutorial_steps[self.current_step]
        action = current_step_data.get("action")
        
        if action:
            method = getattr(self, action, None)
            if method:
                method(context)
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Reset tutorial state
        self.current_step = 0
        
        # Open the tutorial dialog
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        
        # Get current step data
        current_step_data = self.tutorial_steps[self.current_step]
        
        # Draw title
        layout.label(text=current_step_data["title"], icon='HELP')
        
        # Draw content
        for line in current_step_data["text"].split("\n"):
            layout.label(text=line)
        
        # Draw navigation buttons
        row = layout.row()
        
        # Previous button (except on first step)
        if self.current_step > 0:
            row.operator("tutorial.previous_step", text="Previous")
        else:
            row.label(text="")
        
        # Next/Finish button
        if self.current_step < len(self.tutorial_steps) - 1:
            row.operator("tutorial.next_step", text="Next")
        else:
            row.operator("tutorial.finish", text="Finish")

# Pattern Creation tutorial (stub)
class TUTORIAL_OT_pattern_creation(TutorialOperator):
    """Interactive tutorial for pattern creation"""
    bl_idname = "tutorial.pattern_creation"
    bl_label = "Pattern Creation Tutorial"
    bl_description = "Learn how to create precise patterns"
    
    def execute(self, context):
        self.report({'INFO'}, "Pattern Creation tutorial not yet implemented")
        return {'FINISHED'}

# Manufacturing Prep tutorial (stub)
class TUTORIAL_OT_manufacturing_prep(TutorialOperator):
    """Interactive tutorial for manufacturing preparation"""
    bl_idname = "tutorial.manufacturing_prep"
    bl_label = "Manufacturing Prep Tutorial"
    bl_description = "Learn how to prepare models for manufacturing"
    
    def execute(self, context):
        self.report({'INFO'}, "Manufacturing Prep tutorial not yet implemented")
        return {'FINISHED'}

# Tutorial navigation operators
class TUTORIAL_OT_next_step(Operator):
    """Go to the next tutorial step"""
    bl_idname = "tutorial.next_step"
    bl_label = "Next Step"
    bl_description = "Go to the next tutorial step"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        # Find the active tutorial operator
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'PROPERTIES':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            # Access the active operator
                            tutorial_op = context.window_manager.operators[-1]
                            if hasattr(tutorial_op, "current_step"):
                                tutorial_op.current_step += 1
                                area.tag_redraw()
        
        return {'FINISHED'}

class TUTORIAL_OT_previous_step(Operator):
    """Go to the previous tutorial step"""
    bl_idname = "tutorial.previous_step"
    bl_label = "Previous Step"
    bl_description = "Go to the previous tutorial step"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        # Find the active tutorial operator
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'PROPERTIES':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            # Access the active operator
                            tutorial_op = context.window_manager.operators[-1]
                            if hasattr(tutorial_op, "current_step") and tutorial_op.current_step > 0:
                                tutorial_op.current_step -= 1
                                area.tag_redraw()
        
        return {'FINISHED'}

class TUTORIAL_OT_finish(Operator):
    """Finish the tutorial"""
    bl_idname = "tutorial.finish"
    bl_label = "Finish Tutorial"
    bl_description = "Finish and exit the tutorial"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        self.report({'INFO'}, "Tutorial completed")
        return {'FINISHED'}

# List of all classes to register
classes = [
    TUTORIAL_OT_precision_basics,
    TUTORIAL_OT_parametric_modeling,
    TUTORIAL_OT_pattern_creation,
    TUTORIAL_OT_manufacturing_prep,
    TUTORIAL_OT_next_step,
    TUTORIAL_OT_previous_step,
    TUTORIAL_OT_finish,
]

def register():
    """Register all tutorial classes"""
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister all tutorial classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
