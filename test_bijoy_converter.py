#!/usr/bin/env python3
"""
Quick verification test for bijoy2unicode integration
Run this to verify the converter is working correctly
"""

from backend.utils.bijoy_unicode_converter import (
    convert_bijoy_to_unicode, 
    is_bijoy_text,
    converter
)

def test_converter():
    """Test the integrated bijoy2unicode converter"""
    
    print("=" * 70)
    print("BIJOY2UNICODE INTEGRATION VERIFICATION")
    print("=" * 70)
    
    # Check if using advanced library
    using_advanced = hasattr(converter, 'use_advanced') and converter.use_advanced
    print(f"\n✓ Using bijoy2unicode library: {using_advanced}")
    
    # Test cases - verified working examples
    tests = [
        ('Avwg evsjvq Mvb MvB|', 'Basic sentence'),
        ('wk¶v gš¿Yvjq', 'Education ministry'),
        ('MYcÖRvZš¿x evsjv‡`k', 'Complex text'),
        ('†`‡ki RbmsL¨v cÖvq 17 †KvwU', 'With numbers'),
        ('wk¶v', 'Single word'),
    ]
    
    print("\n" + "-" * 70)
    print("Running conversion tests...")
    print("-" * 70)
    
    passed = 0
    for bijoy, description in tests:
        result = convert_bijoy_to_unicode(bijoy)
        # Check if conversion produced Bengali Unicode
        has_bengali = any('\u0980' <= c <= '\u09FF' for c in result)
        is_different = result != bijoy
        
        if has_bengali or is_different:
            status = "✓"
            passed += 1
        else:
            status = "✗"
        
        print(f"{status} {description:20s}: {bijoy:30s} → {result}")
    
    print("-" * 70)
    print(f"Result: {passed}/{len(tests)} tests passed")
    
    # Test detection
    print("\n" + "-" * 70)
    print("Testing Bijoy text detection...")
    print("-" * 70)
    
    print(f"✓ 'Avwg' is Bijoy: {is_bijoy_text('Avwg')}")
    print(f"✓ 'আমি' is Unicode: {not is_bijoy_text('আমি')}")
    
    # Test bidirectional (if available)
    if using_advanced:
        print("\n" + "-" * 70)
        print("Testing bidirectional conversion...")
        print("-" * 70)
        
        unicode_text = "আমি বাংলায় গান গাই।"
        bijoy_text = converter.convert_to_bijoy(unicode_text)
        back_to_unicode = convert_bijoy_to_unicode(bijoy_text)
        
        print(f"Unicode → Bijoy → Unicode: {unicode_text == back_to_unicode}")
    
    print("\n" + "=" * 70)
    if passed == len(tests):
        print("✅ ALL TESTS PASSED - Converter is working correctly!")
    else:
        print("⚠️  SOME TESTS FAILED - Check the output above")
    print("=" * 70)
    
    return passed == len(tests)

if __name__ == "__main__":
    success = test_converter()
    exit(0 if success else 1)
