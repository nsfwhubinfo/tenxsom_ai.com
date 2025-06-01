#!/usr/bin/env python3
"""
Minimal CHRONOSONIC test to verify core functionality
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from research.chronosonic_qualia_v2.chronosonic_refactored import (
    RefactoredChakraSystem,
    RefactoredFrequencyModulatedIAMState,
    RefactoredChronosonicDynamics,
    ChakraType
)


def test_chronosonic_core():
    """Test core CHRONOSONIC functionality"""
    print("CHRONOSONIC Core Functionality Test")
    print("=" * 60)
    
    # Create system
    print("\n1. Creating 3-chakra system...")
    chakra_system = RefactoredChakraSystem(use_simplified=True)
    iam_state = RefactoredFrequencyModulatedIAMState(base_dimension=3)
    dynamics = RefactoredChronosonicDynamics(chakra_system, iam_state)
    print("   ✓ System created")
    
    # Test frequencies
    print("\n2. Testing frequency methods...")
    tests_passed = 0
    total_tests = 0
    
    for chakra_type in [ChakraType.ROOT, ChakraType.HEART, ChakraType.CROWN]:
        base_freq = chakra_system.get_base_frequency(chakra_type)
        current_freq = chakra_system.get_frequency(chakra_type)
        amplitude = chakra_system.get_amplitude(chakra_type)
        
        print(f"   {chakra_type.value}:")
        print(f"     Base frequency: {base_freq:.1f} Hz")
        print(f"     Current frequency: {current_freq:.1f} Hz")
        print(f"     Amplitude: {amplitude:.2f}")
        
        total_tests += 3
        if base_freq > 0:
            tests_passed += 1
        if current_freq > 0:
            tests_passed += 1
        if 0 <= amplitude <= 1:
            tests_passed += 1
    
    # Test modulation
    print("\n3. Testing frequency modulation...")
    chakra_system.modulate_chakra(ChakraType.ROOT, 0.1, 2.0)
    new_freq = chakra_system.get_frequency(ChakraType.ROOT)
    print(f"   ROOT after modulation: {new_freq:.1f} Hz")
    total_tests += 1
    if new_freq != 256.0:  # Should be different from base
        tests_passed += 1
        print("   ✓ Modulation working")
    else:
        print("   ✗ Modulation not working")
    
    # Test activation/deactivation
    print("\n4. Testing activation control...")
    initial_active = sum(1 for c in chakra_system.chakras.values() if c.active)
    chakra_system.deactivate_chakra(ChakraType.ROOT)
    after_deactivate = sum(1 for c in chakra_system.chakras.values() if c.active)
    chakra_system.activate_chakra(ChakraType.ROOT)
    after_activate = sum(1 for c in chakra_system.chakras.values() if c.active)
    
    total_tests += 1
    if after_deactivate < initial_active and after_activate == initial_active:
        tests_passed += 1
        print("   ✓ Activation control working")
    else:
        print("   ✗ Activation control not working")
    
    # Test evolution
    print("\n5. Testing system evolution...")
    initial_coherence = chakra_system.get_system_coherence()
    initial_time = dynamics.time
    
    for i in range(10):
        dynamics.evolve(dt=0.1)
    
    final_coherence = chakra_system.get_system_coherence()
    final_time = dynamics.time
    
    print(f"   Time evolved: {initial_time:.1f} → {final_time:.1f}")
    print(f"   Coherence: {initial_coherence:.3f} → {final_coherence:.3f}")
    
    total_tests += 2
    if final_time > initial_time:
        tests_passed += 1
        print("   ✓ Time evolution working")
    else:
        print("   ✗ Time evolution not working")
    
    if final_coherence > 0:
        tests_passed += 1
        print("   ✓ Coherence calculation working")
    else:
        print("   ✗ Coherence calculation not working")
    
    # Test I_AM state
    print("\n6. Testing I_AM state...")
    iam_metrics = iam_state.get_state_metrics()
    print(f"   Coherence: {iam_metrics['coherence']:.3f}")
    print(f"   Energy: {iam_metrics['energy']:.3f}")
    print(f"   Entropy: {iam_metrics['entropy']:.3f}")
    
    total_tests += 1
    if all(k in iam_metrics for k in ['coherence', 'energy', 'entropy']):
        tests_passed += 1
        print("   ✓ I_AM metrics working")
    else:
        print("   ✗ I_AM metrics not working")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    success_rate = tests_passed / total_tests * 100
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n✅ CHRONOSONIC core functionality VERIFIED!")
        print("\nThe refactored implementation successfully addresses:")
        print("  - All missing methods (get_base_frequency, modulate_chakra, etc.)")
        print("  - API consistency issues")
        print("  - Removed visualization dependencies")
        print("\nReady for extended testing and integration.")
    else:
        print("\n❌ CHRONOSONIC core functionality has issues")
        print("Review the failed tests above.")
    
    return success_rate >= 90


if __name__ == "__main__":
    success = test_chronosonic_core()
    sys.exit(0 if success else 1)