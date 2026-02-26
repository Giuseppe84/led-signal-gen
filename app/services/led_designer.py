import trimesh
import numpy as np
from PIL import Image
from typing import List, Tuple
import math

class LEDDesigner:
    def __init__(self):
        pass
    
    def calculate_led_positions(
        self, 
        width: float, 
        height: float, 
        spacing: float,
        margin: float = 2.0
    ) -> List[Tuple[float, float]]:
        """
        Calculate positions for LEDs in a grid pattern
        """
        # Calculate how many LEDs fit in the area considering margins
        effective_width = width - 2 * margin
        effective_height = height - 2 * margin
        
        # Number of LEDs that fit in each direction
        num_x = max(1, int(effective_width / spacing))
        num_y = max(1, int(effective_height / spacing))
        
        # Calculate actual spacing to evenly distribute LEDs
        actual_spacing_x = effective_width / (num_x + 1) if num_x > 0 else spacing
        actual_spacing_y = effective_height / (num_y + 1) if num_y > 0 else spacing
        
        positions = []
        for y in range(num_y):
            for x in range(num_x):
                pos_x = margin + (x + 1) * actual_spacing_x
                pos_y = margin + (y + 1) * actual_spacing_y
                positions.append((pos_x, pos_y))
        
        return positions
    
    def create_3d_model(
        self,
        width: float,
        height: float,
        image: Image.Image,
        led_positions: List[Tuple[float, float]],
        led_diameter: float = 3.0,
        base_thickness: float = 2.0,
        led_hole_depth: float = 1.5
    ) -> trimesh.Trimesh:
        """
        Create a 3D model with front panel (for printing) and back panel (for LEDs)
        """
        # Create base plate
        base_plate = self._create_base_plate(width, height, base_thickness)
        
        # Add mounting holes for LEDs
        led_mounts = self._create_led_mounts(led_positions, led_diameter, base_thickness, led_hole_depth)
        
        # Subtract the LED mounts from the base to create holes
        if len(led_mounts.vertices) > 0:
            final_model = self._subtract_meshes(base_plate, led_mounts)
        else:
            final_model = base_plate
        
        return final_model
    
    def _create_base_plate(
        self, 
        width: float, 
        height: float, 
        thickness: float
    ) -> trimesh.Trimesh:
        """
        Create the base plate for the LED sign
        """
        # Create a rectangular prism for the base
        box = trimesh.primitives.Box(extents=[width, height, thickness])
        
        # Center the box at origin
        box.apply_translation([-width/2, -height/2, thickness/2])
        
        return box
    
    def _create_led_mounts(
        self,
        led_positions: List[Tuple[float, float]],
        led_diameter: float,
        base_thickness: float,
        hole_depth: float
    ) -> trimesh.Trimesh:
        """
        Create mounts/hole for LEDs
        """
        mounts = []
        
        for pos_x, pos_y in led_positions:
            # Create a cylinder for the LED hole
            hole_cylinder = trimesh.primitives.Cylinder(
                radius=led_diameter/2,
                height=hole_depth,
                sections=32  # Smooth circle
            )
            
            # Position the cylinder
            translation_matrix = trimesh.transformations.translation_matrix([
                pos_x, 
                pos_y, 
                hole_depth/2
            ])
            hole_cylinder.apply_transform(translation_matrix)
            
            # We need to subtract this from the base, so we'll handle this later
            mounts.append(hole_cylinder)
        
        if mounts:
            # Combine all mount meshes
            combined_mounts = self._combine_meshes(mounts)
            return combined_mounts
        else:
            # Return empty mesh if no mounts
            return trimesh.Trimesh(vertices=[], faces=[])
    
    def _subtract_meshes(self, base: trimesh.Trimesh, holes: trimesh.Trimesh) -> trimesh.Trimesh:
        """
        Subtract hole mesh from base mesh using boolean operations
        """
        try:
            # Use trimesh's difference operation to subtract holes from base
            result = base.difference(holes)
            return result
        except Exception:
            # If boolean operations fail, return base without holes
            # This might happen due to complex geometry or library limitations
            print("Boolean operation failed, returning base without holes")
            return base
    
    def _combine_meshes(self, meshes: List[trimesh.Trimesh]) -> trimesh.Trimesh:
        """
        Combine multiple meshes into a single mesh
        """
        if not meshes:
            return trimesh.Trimesh(vertices=[], faces=[])
        
        # Filter out empty meshes
        valid_meshes = [mesh for mesh in meshes if len(mesh.vertices) > 0 and len(mesh.faces) > 0]
        
        if not valid_meshes:
            return trimesh.Trimesh(vertices=[], faces=[])
        
        # Concatenate all valid meshes
        combined = trimesh.util.concatenate(valid_meshes)
        return combined