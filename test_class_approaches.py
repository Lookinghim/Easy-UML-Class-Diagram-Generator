#!/usr/bin/env python3
"""
Test different approaches for UML class representation
"""
import sys
sys.path.append('src')
from diagramDraw import *
from uml_classes import *

def test_dataclass_approach():
    print("=== Testing Dataclass Approach ===")
    
    # Create UML class using dataclass
    person_class = UMLClass("Person")
    person_class.add_attribute("- name: string")
    person_class.add_attribute("- age: int")
    person_class.add_attribute("+ email: string")
    
    person_class.add_operation("+ getName(): string")
    person_class.add_operation("+ setAge(int): void")
    person_class.add_operation("+ getEmail(): string")
    
    # Convert to drawing format
    name, attributes, operations = person_class.to_strings()
    
    # Draw the class
    base_font, _ = loadFonts()
    diagram = mergeBoxes(name, attributes, operations, base_font, 12)
    diagram.save("test_dataclass_person.png")
    print("✓ Dataclass approach - Person class saved")

def test_dictionary_approach():
    print("\n=== Testing Dictionary Approach ===")
    
    # Create UML class using dictionary
    car_class = create_uml_class("Car")
    add_attribute(car_class, "- make: string")
    add_attribute(car_class, "- model: string")
    add_attribute(car_class, "- year: int")
    
    add_operation(car_class, "+ start(): void")
    add_operation(car_class, "+ stop(): void")
    add_operation(car_class, "+ getInfo(): string")
    
    # Convert to drawing format
    name, attributes, operations = class_to_strings(car_class)
    
    # Draw the class
    base_font, _ = loadFonts()
    diagram = mergeBoxes(name, attributes, operations, base_font, 12)
    diagram.save("test_dictionary_car.png")
    print("✓ Dictionary approach - Car class saved")

def test_simple_function_approach():
    print("\n=== Testing Simple Function Approach ===")
    
    # Simple direct approach (what you probably need)
    def create_simple_class(name, attrs, ops):
        return {
            'name': name,
            'attributes': attrs,
            'operations': ops
        }
    
    # Create a class directly
    book_class = create_simple_class(
        "Book",
        ["- title: string", "- author: string", "- pages: int"],
        ["+ read(): void", "+ getTitle(): string", "+ getAuthor(): string"]
    )
    
    # Draw directly
    base_font, _ = loadFonts()
    diagram = mergeBoxes(
        book_class['name'],
        '\n'.join(book_class['attributes']),
        '\n'.join(book_class['operations']),
        base_font,
        12,
        outline_colour='blue',
        outline_width=2
    )
    diagram.save("test_simple_book.png")
    print("✓ Simple function approach - Book class saved")

if __name__ == "__main__":
    print("Testing different UML class representation approaches...")
    
    test_dataclass_approach()
    test_dictionary_approach() 
    test_simple_function_approach()
    
    print("\n=== Recommendation ===")
    print("For your UML generator, the SIMPLE FUNCTION approach is best because:")
    print("1. ✅ Less code complexity")
    print("2. ✅ Easier to understand and debug")
    print("3. ✅ More flexible for different input formats")
    print("4. ✅ Better performance")
    print("5. ✅ Easier integration with your existing drawing functions")
    
    print("\nUse classes only if you need:")
    print("- Complex validation logic")
    print("- Multiple methods per UML class")
    print("- State management across operations")
    print("- Object relationships and inheritance")