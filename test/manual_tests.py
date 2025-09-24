#!/usr/bin/env python3
"""
Quick manual testing commands for your UML functions
Run this interactively in Python terminal
"""

# Import your modules
import sys
import os
sys.path.append('../src')
from diagramDraw import *

# Load fonts once
base_font, italic_font = loadFonts()

print("=== Quick Test Commands ===")
print("Copy and paste these commands to test individual functions:\n")

print("# Test width calculation:")
print("calculateBoxWidth('MyClass', base_font)")
print()

print("# Test height calculation:")
print("calculateBoxHeight('MyClass', base_font)")
print()

print("# Test box drawing:")
print("box = drawBox(200, 100)")
print("box.save('my_test_box.png')")
print("print('Box saved!')")
print()

print("# Test max width constraint:")
print("long_name = 'VeryLongClassNameThatShouldBeLimited'")
print("width = calculateBoxWidth(long_name, base_font)")
print("print(f'Width: {width}px (max: {MAX_BOX_WIDTH}px)')")
print()

print("# Test multi-line text:")
print("multiline = 'Class\\nwith\\nmultiple\\nlines'")
print("width = calculateBoxWidth(multiline, base_font)")
print("height = calculateBoxHeight(multiline, base_font)")
print("print(f'Size: {width}x{height}px')")