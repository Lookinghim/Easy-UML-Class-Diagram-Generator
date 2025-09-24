#!/usr/bin/env python3
"""
Test script for UML diagram drawing functions
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from diagramDraw import *

def test_basic_functions():
    print("Testing UML drawing functions...")
    
    # Load fonts
    base_font, italic_font = loadFonts()
    print(f"✓ Fonts loaded successfully")
    
    # Test text width calculation
    test_text = "MyClass"
    width = calculateBoxWidth(test_text, base_font)
    print(f"✓ Width calculation: '{test_text}' -> {width}px")
    
    # Test text height calculation
    height = calculateBoxHeight(test_text, base_font)
    print(f"✓ Height calculation: '{test_text}' -> {height}px")
    
    # Test multi-line text
    multiline_text = "MyClass\nwith\nmultiple\nlines"
    width_multi = calculateBoxWidth(multiline_text, base_font)
    height_multi = calculateBoxHeight(multiline_text, base_font)
    print(f"✓ Multi-line calculation: {width_multi}x{height_multi}px")
    
    # Test very long text (should be limited by MAX_BOX_WIDTH)
    long_text = "ThisIsAVeryLongClassNameThatShouldBeLimitedByMaxWidth"
    width_long = calculateBoxWidth(long_text, base_font)
    print(f"✓ Long text width (should be ≤ {MAX_BOX_WIDTH}): {width_long}px")
    
    return base_font, italic_font

def test_box_drawing():
    print("\nTesting box drawing...")
    
    base_font, italic_font = loadFonts()
    
    # Test basic box
    box = drawBox(200, 100)
    box.save("test_basic_box.png")
    print("✓ Basic box saved as 'test_basic_box.png'")
    
    # Test with different sizes
    small_box = drawBox(100, 50)
    small_box.save("test_small_box.png")
    print("✓ Small box saved as 'test_small_box.png'")
    
    large_box = drawBox(300, 150)
    large_box.save("test_large_box.png")
    print("✓ Large box saved as 'test_large_box.png'")

def test_max_width_constraint():
    print("\nTesting max width constraint...")
    
    base_font, _ = loadFonts()
    
    test_cases = [
        "Short",
        "MediumLengthClassName",
        "ThisIsAVeryLongClassNameThatShouldDefinitelyExceedTheMaximumWidthLimit",
        "AnotherExtremelyLongClassNameWithManyCharactersThatWillTestTheConstraint"
    ]
    
    for i, text in enumerate(test_cases):
        width = calculateBoxWidth(text, base_font)
        height = calculateBoxHeight(text, base_font)
        
        print(f"  Case {i+1}: '{text[:30]}...' -> {width}x{height}px")
        
        if width > MAX_BOX_WIDTH:
            print(f"    ⚠️  WARNING: Width {width} exceeds MAX_BOX_WIDTH {MAX_BOX_WIDTH}")
        else:
            print(f"    ✓ Width within limit")

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("UML Diagram Drawing Test Suite")
        print("=" * 50)
        
        test_basic_functions()
        test_box_drawing()
        test_max_width_constraint()
        
        print("\n" + "=" * 50)
        print("All tests completed! Check the generated PNG files.")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()