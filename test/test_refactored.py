#!/usr/bin/env python3
"""
Test the refactored UML functions
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from diagramDraw import *
if __name__ == "__main__":
    # Load fonts
    base_font, italic_font = loadFonts()
    
    # Test individual boxes
    name_box = drawNameBox(200, 40, "MyClass", base_font, 12)
    name_box.save("test_name_box.png")
    print("✓ Name box saved")
    
    attr_box = drawAttributeBox(200, 60, "- name: string\n+ age: int", base_font, 12)
    attr_box.save("test_attr_box.png")
    print("✓ Attribute box saved")
    
    ops_box = drawOperationBox(200, 60, "+ getName(): string\n+ setAge(int): void", base_font, 12)
    ops_box.save("test_ops_box.png")
    print("✓ Operations box saved")
    
    # Test complete UML class
    complete_class = mergeBoxes(
        "Person",
        "- name: string\n- age: int\n- email: string",
        "+ getName(): string\n+ setAge(int): void\n+ getEmail(): string",
        base_font,
        12
    )
    complete_class.save("test_complete_class.png")
    print("✓ Complete UML class saved")
    
    print("All tests completed! Check the generated PNG files.")