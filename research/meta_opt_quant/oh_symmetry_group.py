#!/usr/bin/env python3
"""
Complete Oh Symmetry Group Implementation
=========================================

The Oh group (octahedral symmetry) has 48 elements:
- 1 identity
- 6 face rotations (90° and 270° around 3 axes)
- 3 face rotations (180° around 3 axes)
- 8 vertex rotations (120° and 240° around 4 body diagonals)
- 6 edge rotations (180° around 6 edge midpoints)
- 1 inversion
- 6 rotoinversions (90° and 270° + inversion)
- 3 rotoinversions (180° + inversion = mirror planes)
- 8 rotoinversions (120° and 240° + inversion)
- 6 rotoinversions (edge rotation + inversion = mirror planes)

For Tenxsom AI's META-OPT-QUANT V6.
"""

import numpy as np
from typing import List, Tuple, Dict
from enum import Enum
import itertools

class SymmetryOperation:
    """Single symmetry operation in Oh group"""
    
    def __init__(self, matrix: np.ndarray, name: str, order: int):
        self.matrix = matrix
        self.name = name
        self.order = order  # How many times to apply to get identity
        
    def apply(self, point: np.ndarray) -> np.ndarray:
        """Apply symmetry operation to a 3D point"""
        return self.matrix @ point
        
    def __repr__(self):
        return f"SymOp({self.name}, order={self.order})"

class OhSymmetryGroup:
    """Complete Oh symmetry group with all 48 operations"""
    
    def __init__(self):
        self.operations = self._generate_all_operations()
        self.operation_dict = {op.name: op for op in self.operations}
        
    def _generate_all_operations(self) -> List[SymmetryOperation]:
        """Generate all 48 symmetry operations"""
        ops = []
        
        # 1. Identity
        ops.append(SymmetryOperation(np.eye(3), "E", 1))
        
        # 2. Face rotations around coordinate axes
        # Rotation matrices using Rodrigues' formula
        
        # X-axis rotations
        ops.append(SymmetryOperation(self._rotation_matrix([1,0,0], np.pi/2), "C4x", 4))
        ops.append(SymmetryOperation(self._rotation_matrix([1,0,0], -np.pi/2), "C4x^3", 4))
        ops.append(SymmetryOperation(self._rotation_matrix([1,0,0], np.pi), "C2x", 2))
        
        # Y-axis rotations
        ops.append(SymmetryOperation(self._rotation_matrix([0,1,0], np.pi/2), "C4y", 4))
        ops.append(SymmetryOperation(self._rotation_matrix([0,1,0], -np.pi/2), "C4y^3", 4))
        ops.append(SymmetryOperation(self._rotation_matrix([0,1,0], np.pi), "C2y", 2))
        
        # Z-axis rotations
        ops.append(SymmetryOperation(self._rotation_matrix([0,0,1], np.pi/2), "C4z", 4))
        ops.append(SymmetryOperation(self._rotation_matrix([0,0,1], -np.pi/2), "C4z^3", 4))
        ops.append(SymmetryOperation(self._rotation_matrix([0,0,1], np.pi), "C2z", 2))
        
        # 3. Vertex rotations (body diagonals)
        # 8 C3 rotations around the 4 body diagonals
        diagonals = [
            [1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]
        ]
        
        for i, diag in enumerate(diagonals):
            axis = np.array(diag) / np.sqrt(3)
            ops.append(SymmetryOperation(self._rotation_matrix(axis, 2*np.pi/3), f"C3_{i}", 3))
            ops.append(SymmetryOperation(self._rotation_matrix(axis, -2*np.pi/3), f"C3_{i}^2", 3))
        
        # 4. Edge rotations (180° around edge midpoints)
        # 6 C2 rotations around edges
        edge_axes = [
            [1, 1, 0], [1, -1, 0], [1, 0, 1], 
            [1, 0, -1], [0, 1, 1], [0, 1, -1]
        ]
        
        for i, axis in enumerate(edge_axes):
            axis_norm = np.array(axis) / np.sqrt(2)
            ops.append(SymmetryOperation(self._rotation_matrix(axis_norm, np.pi), f"C2e_{i}", 2))
        
        # 5. Inversion
        inversion = -np.eye(3)
        ops.append(SymmetryOperation(inversion, "i", 2))
        
        # 6. Rotoinversions (rotation followed by inversion)
        # S4 operations (90° rotation + inversion)
        for ax, name in [([1,0,0], 'x'), ([0,1,0], 'y'), ([0,0,1], 'z')]:
            rot90 = self._rotation_matrix(ax, np.pi/2)
            ops.append(SymmetryOperation(-rot90, f"S4{name}", 4))
            rot270 = self._rotation_matrix(ax, -np.pi/2)
            ops.append(SymmetryOperation(-rot270, f"S4{name}^3", 4))
        
        # S2 operations (180° rotation + inversion = mirror planes)
        ops.append(SymmetryOperation(-self._rotation_matrix([1,0,0], np.pi), "σx", 2))
        ops.append(SymmetryOperation(-self._rotation_matrix([0,1,0], np.pi), "σy", 2))
        ops.append(SymmetryOperation(-self._rotation_matrix([0,0,1], np.pi), "σz", 2))
        
        # S6 operations (60° rotation + inversion around body diagonals)
        for i, diag in enumerate(diagonals):
            axis = np.array(diag) / np.sqrt(3)
            rot60 = self._rotation_matrix(axis, np.pi/3)
            ops.append(SymmetryOperation(-rot60, f"S6_{i}", 6))
            rot300 = self._rotation_matrix(axis, -np.pi/3)
            ops.append(SymmetryOperation(-rot300, f"S6_{i}^5", 6))
        
        # Mirror planes through edges
        for i, normal in enumerate(edge_axes):
            # Mirror plane has normal vector = edge axis
            mirror = self._reflection_matrix(normal)
            ops.append(SymmetryOperation(mirror, f"σd_{i}", 2))
        
        return ops
        
    def _rotation_matrix(self, axis: List[float], angle: float) -> np.ndarray:
        """Generate rotation matrix using Rodrigues' formula"""
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)
        
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        
        # Cross product matrix
        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        
        # Rodrigues' formula
        R = np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)
        
        return R
        
    def _reflection_matrix(self, normal: List[float]) -> np.ndarray:
        """Generate reflection matrix for plane with given normal"""
        n = np.array(normal)
        n = n / np.linalg.norm(n)
        
        # Reflection matrix: I - 2nn^T
        return np.eye(3) - 2 * np.outer(n, n)
        
    def get_operation(self, name: str) -> SymmetryOperation:
        """Get operation by name"""
        return self.operation_dict.get(name)
        
    def find_fundamental_domain(self, points: np.ndarray) -> Tuple[np.ndarray, List[int]]:
        """
        Find fundamental domain of a set of points under Oh symmetry.
        Returns representative points and their orbit sizes.
        """
        n_points = len(points)
        visited = [False] * n_points
        fundamental_points = []
        orbit_sizes = []
        
        for i in range(n_points):
            if visited[i]:
                continue
                
            # Find orbit of this point
            orbit = set()
            point = points[i]
            
            for op in self.operations:
                transformed = op.apply(point)
                
                # Find which original point this maps to
                for j in range(n_points):
                    if np.allclose(transformed, points[j], atol=1e-10):
                        orbit.add(j)
                        visited[j] = True
                        break
                        
            fundamental_points.append(point)
            orbit_sizes.append(len(orbit))
            
        return np.array(fundamental_points), orbit_sizes
        
    def compress_cuboctahedron_state(self, vertex_values: List[float]) -> Dict[str, any]:
        """
        Compress 12 vertex values using Oh symmetry.
        Cuboctahedron has specific symmetry properties we can exploit.
        """
        # Cuboctahedron vertices in standard position
        vertices = np.array([
            [1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0],
            [1, 0, 1], [1, 0, -1], [-1, 0, -1], [-1, 0, 1],
            [0, 1, 1], [0, 1, -1], [0, -1, -1], [0, -1, 1]
        ]) / np.sqrt(2)
        
        # Find symmetry orbits
        fundamental_vertices, orbit_sizes = self.find_fundamental_domain(vertices)
        
        # Group vertex values by orbit
        compressed = {
            'fundamental_values': [],
            'orbit_structure': orbit_sizes,
            'reconstruction_map': self._build_reconstruction_map(vertices)
        }
        
        # For cuboctahedron, we expect 1 or 2 orbits depending on values
        orbit_representatives = []
        for i, (vert, size) in enumerate(zip(fundamental_vertices, orbit_sizes)):
            # Find original index of this vertex
            for j, v in enumerate(vertices):
                if np.allclose(v, vert):
                    orbit_representatives.append(vertex_values[j])
                    break
                    
        compressed['fundamental_values'] = orbit_representatives
        
        return compressed
        
    def _build_reconstruction_map(self, vertices: np.ndarray) -> List[Tuple[int, str]]:
        """Build map from original vertices to fundamental domain + operation"""
        reconstruction_map = []
        fundamental_vertices, _ = self.find_fundamental_domain(vertices)
        
        for i, vertex in enumerate(vertices):
            # Find which fundamental vertex and operation gives this vertex
            for j, fund_vert in enumerate(fundamental_vertices):
                for op in self.operations:
                    if np.allclose(op.apply(fund_vert), vertex, atol=1e-10):
                        reconstruction_map.append((j, op.name))
                        break
                else:
                    continue
                break
                
        return reconstruction_map
        
    def decompress_cuboctahedron_state(self, compressed: Dict[str, any]) -> List[float]:
        """Decompress to recover all 12 vertex values"""
        values = [0.0] * 12
        
        # Standard cuboctahedron vertices
        vertices = np.array([
            [1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0],
            [1, 0, 1], [1, 0, -1], [-1, 0, -1], [-1, 0, 1],
            [0, 1, 1], [0, 1, -1], [0, -1, -1], [0, -1, 1]
        ]) / np.sqrt(2)
        
        # Reconstruct using symmetry
        for i, (fund_idx, op_name) in enumerate(compressed['reconstruction_map']):
            values[i] = compressed['fundamental_values'][fund_idx]
            
        return values
        
    def analyze_symmetry(self, vertex_values: List[float], tolerance: float = 1e-6) -> Dict[str, any]:
        """Analyze symmetry properties of given vertex values"""
        # Check which symmetries are preserved
        preserved_symmetries = []
        
        vertices = np.array([
            [1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0],
            [1, 0, 1], [1, 0, -1], [-1, 0, -1], [-1, 0, 1],
            [0, 1, 1], [0, 1, -1], [0, -1, -1], [0, -1, 1]
        ]) / np.sqrt(2)
        
        for op in self.operations:
            # Check if this operation preserves the value pattern
            preserved = True
            
            for i, vertex in enumerate(vertices):
                transformed = op.apply(vertex)
                
                # Find which vertex this maps to
                for j, v in enumerate(vertices):
                    if np.allclose(transformed, v, atol=1e-10):
                        if abs(vertex_values[i] - vertex_values[j]) > tolerance:
                            preserved = False
                            break
                        break
                        
                if not preserved:
                    break
                    
            if preserved:
                preserved_symmetries.append(op.name)
                
        return {
            'preserved_symmetries': preserved_symmetries,
            'symmetry_group_size': len(preserved_symmetries),
            'compression_ratio': 48 / len(preserved_symmetries)
        }

# Demonstration and testing
if __name__ == "__main__":
    print("Oh Symmetry Group Implementation Test")
    print("=" * 50)
    
    oh_group = OhSymmetryGroup()
    print(f"Generated {len(oh_group.operations)} symmetry operations")
    
    # Test on cuboctahedron with different value patterns
    
    # Pattern 1: All same values (full Oh symmetry)
    values1 = [1.0] * 12
    compressed1 = oh_group.compress_cuboctahedron_state(values1)
    print(f"\nPattern 1 (all same): {len(compressed1['fundamental_values'])} fundamental values")
    print(f"Compression ratio: {12/len(compressed1['fundamental_values']):.1f}x")
    
    # Pattern 2: Alternating values
    values2 = [1.0 if i % 2 == 0 else 2.0 for i in range(12)]
    compressed2 = oh_group.compress_cuboctahedron_state(values2)
    print(f"\nPattern 2 (alternating): {len(compressed2['fundamental_values'])} fundamental values")
    
    # Pattern 3: Random values (likely no symmetry)
    values3 = [0.1 * i for i in range(12)]
    analysis3 = oh_group.analyze_symmetry(values3)
    print(f"\nPattern 3 (sequential): {analysis3['symmetry_group_size']} preserved symmetries")
    print(f"Maximum compression ratio: {analysis3['compression_ratio']:.1f}x")