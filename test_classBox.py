#!/usr/bin/env python3
"""
Test script for classBox.py UML class creation functions
"""
import sys
sys.path.append('src')
from classBox import *

def test_single_class():
    print("=== Testing Single UML Class Creation ===")
    
    # Test 1: Simple class with lists
    print("\n1. Testing with lists:")
    createSingleUMLClass(
        "Person",
        ["- name: string", "- age: int", "- email: string"],
        ["+ getName(): string", "+ setAge(int): void", "+ getEmail(): string"],
        "test_person_lists.png"
    )
    
    # Test 2: Class with string attributes/operations
    print("\n2. Testing with strings:")
    attributes_str = "- make: string\n- model: string\n- year: int"
    operations_str = "+ start(): void\n+ stop(): void\n+ getInfo(): string"
    
    createSingleUMLClass(
        "Car",
        attributes_str,
        operations_str,
        "test_car_strings.png"
    )
    
    # Test 3: Class with minimal data
    print("\n3. Testing minimal class:")
    createSingleUMLClass(
        "SimpleClass",
        ["- data: int"],
        ["+ getData(): int"],
        "test_simple.png"
    )
    
    # Test 4: Class with no attributes/operations
    print("\n4. Testing empty class:")
    createSingleUMLClass(
        "EmptyClass",
        [],
        [],
        "test_empty.png"
    )

def test_multiple_classes():
    print("\n=== Testing Multiple UML Classes Creation ===")
    
    # Test multiple classes at once
    class_names = ["Student", "Teacher", "Course"]
    
    attributes_lists = [
        ["- studentId: int", "- name: string", "- grade: float"],
        ["- teacherId: int", "- name: string", "- department: string"],
        ["- courseId: int", "- title: string", "- credits: int"]
    ]
    
    operations_lists = [
        ["+ getId(): int", "+ getName(): string", "+ setGrade(float): void"],
        ["+ getId(): int", "+ getName(): string", "+ getDepartment(): string"],
        ["+ getId(): int", "+ getTitle(): string", "+ getCredits(): int"]
    ]
    
    createUMLClass(class_names, attributes_lists, operations_lists)

def test_edge_cases():
    print("\n=== Testing Edge Cases ===")
    
    # Test 1: Very long class name
    print("\n1. Testing long class name:")
    createSingleUMLClass(
        "VeryLongClassNameThatMightCauseIssues",
        ["- attribute: string"],
        ["+ method(): void"],
        "test_long_name.png"
    )
    
    # Test 2: Class with many attributes
    print("\n2. Testing many attributes:")
    many_attrs = [
        "- attr1: string",
        "- attr2: int", 
        "- attr3: float",
        "- attr4: boolean",
        "- attr5: list",
        "- attr6: dict"
    ]
    many_ops = [
        "+ getAttr1(): string",
        "+ setAttr1(string): void",
        "+ getAttr2(): int",
        "+ setAttr2(int): void",
        "+ processData(): void",
        "+ validateData(): boolean"
    ]
    
    createSingleUMLClass(
        "ComplexClass",
        many_attrs,
        many_ops,
        "test_complex.png"
    )
    
    # Test 3: Special characters in names
    print("\n3. Testing special characters:")
    createSingleUMLClass(
        "Class<T>",
        ["- data: T", "- size: int"],
        ["+ getData(): T", "+ getSize(): int"],
        "test_generic.png"
    )

def test_custom_styling():
    print("\n=== Testing Custom Styling ===")
    
    # We need to modify the function to accept styling parameters
    # For now, let's test the basic functionality
    
    print("Note: Custom styling would require modifying the classBox functions")
    print("to accept outline_colour and outline_width parameters")

def run_all_tests():
    print("🚀 Starting UML Class Box Tests")
    print("=" * 50)
    
    try:
        test_single_class()
        test_multiple_classes()
        test_edge_cases()
        test_custom_styling()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("Check the generated PNG files to see the results.")
        print("Generated files:")
        print("- test_person_lists.png")
        print("- test_car_strings.png") 
        print("- test_simple.png")
        print("- test_empty.png")
        print("- uml_Student_0.png")
        print("- uml_Teacher_1.png")
        print("- uml_Course_2.png")
        print("- test_long_name.png")
        print("- test_complex.png")
        print("- test_generic.png")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()