import diagramDraw

def createUMLClass(class_name, attributes_list, operations_list):
    """
    Create UML class diagrams from lists of class names, attributes, and operations
    
    Args:
        class_name: List of class names or single class name
        attributes_list: List of attribute strings for each class
        operations_list: List of operation strings for each class
    """
    # Load fonts once
    base_font, italic_font = diagramDraw.loadFonts()
    
    # Handle single class vs multiple classes
    if isinstance(class_name, str):
        class_name = [class_name]
        attributes_list = [attributes_list]
        operations_list = [operations_list]
    
    # Create UML diagram for each class
    for i, (name, attrs, ops) in enumerate(zip(class_name, attributes_list, operations_list)):
        # Convert lists to strings if needed
        if isinstance(attrs, list):
            attrs_string = '\n'.join(attrs)
        else:
            attrs_string = attrs or ""
            
        if isinstance(ops, list):
            ops_string = '\n'.join(ops)
        else:
            ops_string = ops or ""
        
        # Create the merged UML diagram
        diagram = diagramDraw.mergeBoxes(
            name, 
            attrs_string, 
            ops_string, 
            base_font, 
            12
        )
        
        # Save with descriptive filename
        safe_name = name.replace(" ", "_").replace("/", "_")
        filename = f"uml_{safe_name}_{i}.png"
        diagram.save(filename)
        print(f"✓ UML class '{name}' saved as '{filename}'")

def createSingleUMLClass(name, attributes, operations, filename=None):
    """
    Create a single UML class diagram
    
    Args:
        name: Class name (string)
        attributes: List of attributes or string with newlines
        operations: List of operations or string with newlines
        filename: Optional custom filename
    """
    base_font, _ = diagramDraw.loadFonts()
    
    # Convert to strings if needed
    if isinstance(attributes, list):
        attrs_string = '\n'.join(attributes)
    else:
        attrs_string = attributes or ""
        
    if isinstance(operations, list):
        ops_string = '\n'.join(operations)
    else:
        ops_string = operations or ""
    
    # Create diagram
    diagram = diagramDraw.mergeBoxes(name, attrs_string, ops_string, base_font, 12)
    
    # Save with custom or default filename
    if filename is None:
        safe_name = name.replace(" ", "_").replace("/", "_")
        filename = f"uml_{safe_name}.png"
    
    diagram.save(filename)
    print(f"✓ UML class '{name}' saved as '{filename}'")
    return diagram
