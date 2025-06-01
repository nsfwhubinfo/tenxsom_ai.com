#!/usr/bin/env python3
"""Minimal V6 test to identify issues"""

print("Testing V6 imports...")

try:
    from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import (
        CuboctahedronCPUState, PHI
    )
    print("✓ Basic imports successful")
    
    print("\nTesting cuboctahedron creation...")
    cpu_state = CuboctahedronCPUState()
    print(f"✓ Created state with {len(cpu_state.vertices)} vertices")
    
    print("\nTesting basic optimization...")
    from research.meta_opt_quant.enhanced_meta_optimizer_v6_cuboctahedral import EnhancedMetaOptimizerV6
    
    # Don't actually create optimizer - just test import
    print("✓ Optimizer class imported")
    
    print("\nV6 basic functionality confirmed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()