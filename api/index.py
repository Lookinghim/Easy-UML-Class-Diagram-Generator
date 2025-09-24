#!/usr/bin/env python3

"""
Vercel-compatible Flask API for UML Class Diagram Generator
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import uuid
import tempfile
from datetime import datetime
from PIL import Image
import io
import base64

# Add the src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import robust UML modules - no fallbacks
from diagramDraw import mergeBoxes, loadFonts, note, clear_notes, drawConnection, draw_proper_generalization
from connection import ConnectionManager, ConnectionType, UMLConnection
from classBox import createSingleUMLClass

app = Flask(__name__)
CORS(app)

# Global storage for diagram data
diagrams_storage = {}

class UMLDiagramService:
    """Service class to handle UML diagram generation"""
    
    def __init__(self):
        try:
            self.base_font, self.font_size = loadFonts()
        except:
            self.base_font, self.font_size = None, 12
        self.connection_manager = ConnectionManager()
    
    def get_visibility_symbol(self, visibility):
        """Convert visibility string to UML symbol"""
        symbols = {
            'public': '+',
            'private': '-',
            'protected': '#'
        }
        return symbols.get(visibility, '+')
    
    def create_class_box(self, class_data, outline_color='blue', outline_width=2):
        """Create a UML class box from class data - simplified for Vercel"""
        class_name = class_data.get('name', 'UnnamedClass')
        
        # Create a simple text representation for Vercel deployment
        # In a full deployment, this would use the actual mergeBoxes function
        text_repr = f"Class: {class_name}\n"
        
        # Format attributes
        for attr in class_data.get('attributes', []):
            visibility_symbol = self.get_visibility_symbol(attr.get('visibility', 'private'))
            text_repr += f"{visibility_symbol}{attr.get('name', '')}: {attr.get('type', '')}\n"
        
        # Format operations
        for op in class_data.get('operations', []):
            visibility_symbol = self.get_visibility_symbol(op.get('visibility', 'public'))
            text_repr += f"{visibility_symbol}{op.get('name', '')}\n"
        
        return text_repr
    
    def generate_simple_diagram(self, classes_data, styling_options=None):
        """Generate a complete UML diagram using robust UML modules"""
        if not classes_data:
            return None
        
        try:
            # Create larger canvas for proper UML diagram
            img_width = styling_options.get('image_width', 1400) if styling_options else 1400
            img_height = styling_options.get('image_height', 1000) if styling_options else 1000
            
            # Create main diagram image
            diagram_image = Image.new('RGB', (img_width, img_height), 'white')
            
            # Load fonts using robust module
            font, font_size = loadFonts()
            
            # Clear notes for collision detection
            clear_notes()
            
            # Initialize connection manager
            connection_manager = ConnectionManager()
            
            # Process each class and create UML boxes
            class_boxes = {}
            class_positions = {}
            
            # First pass: create all class boxes to know their sizes
            temp_class_boxes = {}
            for i, class_data in enumerate(classes_data):
                class_id = class_data.get('id', f'class_{i}')
                class_name = class_data.get('name', f'Class{i+1}')
                attributes = class_data.get('attributes', [])
                operations = class_data.get('operations', [])
                
                # Format attributes using proper visibility symbols
                attr_list = []
                for attr in attributes:
                    visibility = self.get_visibility_symbol(attr.get('visibility', 'private'))
                    attr_name = attr.get('name', '')
                    attr_type = attr.get('type', '')
                    if attr_name:  # Only add non-empty attributes
                        attr_list.append(f"{visibility}{attr_name}: {attr_type}")
                
                # Format operations using proper visibility symbols
                op_list = []
                for op in operations:
                    visibility = self.get_visibility_symbol(op.get('visibility', 'public'))
                    op_name = op.get('name', '')
                    return_type = op.get('returnType', 'void')
                    
                    # Format parameters
                    params = op.get('parameters', [])
                    if params:
                        param_str = ', '.join([f"{p.get('name', '')}: {p.get('type', '')}" for p in params])
                        op_text = f"{visibility}{op_name}({param_str}): {return_type}"
                    else:
                        op_text = f"{visibility}{op_name}(): {return_type}"
                    
                    if op_name:  # Only add non-empty operations
                        op_list.append(op_text)
                
                # Get styling options
                outline_color = styling_options.get('outline_color', 'black') if styling_options else 'black'
                outline_width = styling_options.get('outline_width', 2) if styling_options else 2
                
                # Create UML class box using robust mergeBoxes function
                class_box = mergeBoxes(
                    name=class_name,
                    attributes='\n'.join(attr_list) if attr_list else '',
                    operations='\n'.join(op_list) if op_list else '',
                    font=font,
                    fontSize=12,
                    outline_colour=outline_color,
                    outline_width=outline_width
                )
                temp_class_boxes[class_id] = class_box
            
            # Calculate layout positions with better centering
            if classes_data:
                # Calculate total height needed for all boxes
                total_height = sum(temp_class_boxes[class_data.get('id', f'class_{i}')].size[1] for i, class_data in enumerate(classes_data))
                vertical_spacing = 60  # Space between boxes
                total_layout_height = total_height + (vertical_spacing * (len(classes_data) - 1))
                
                # Center the entire layout vertically
                start_y = max(40, (img_height - total_layout_height) // 2)
                
                # Center horizontally (all boxes in single column)
                max_width = max(temp_class_boxes[class_data.get('id', f'class_{i}')].size[0] for i, class_data in enumerate(classes_data))
                start_x = (img_width - max_width) // 2
                
                current_y = start_y
                
            for i, class_data in enumerate(classes_data):
                class_id = class_data.get('id', f'class_{i}')
                class_name = class_data.get('name', f'Class{i+1}')
                class_box = temp_class_boxes[class_id]
                
                # Calculate position - centered single column layout
                box_width, box_height = class_box.size
                pos_x = (img_width - box_width) // 2  # Center each box horizontally
                pos_y = current_y
                
                # Ensure positions are within bounds
                pos_x = max(20, min(pos_x, img_width - box_width - 20))
                pos_y = max(20, min(pos_y, img_height - box_height - 20))
                
                # Store class box and position
                class_boxes[class_id] = class_box
                class_positions[class_id] = (pos_x, pos_y)
                current_y += box_height + vertical_spacing
                
                # Register class position with connection manager
                connection_manager.add_class_position(
                    class_name, pos_x, pos_y, class_box.size[0], class_box.size[1]
                )
                
                # Paste the class box onto the main diagram
                diagram_image.paste(class_box, (pos_x, pos_y))
            
            # Draw connections using robust connection drawing with generalization detection
            self._draw_connections_with_robust_modules(
                diagram_image, classes_data, class_positions, class_boxes, connection_manager
            )
            
            return diagram_image
            
        except Exception as e:
            print(f"Error generating diagram: {e}")
            import traceback
            traceback.print_exc()
            # Return a minimal valid image with error info
            try:
                minimal_image = Image.new('RGB', (400, 300), 'white')
                from PIL import ImageDraw
                draw = ImageDraw.Draw(minimal_image)
                draw.text((10, 10), "UML Diagram", fill='black')
                draw.text((10, 30), f"Error: {str(e)}", fill='red')
                return minimal_image
            except:
                return None
    
    def _draw_connections_with_robust_modules(self, image, classes_data, class_positions, class_boxes, connection_manager):
        """Draw connections using robust modules with generalization detection"""
        print(f"🔗 Drawing connections for {len(classes_data)} classes")
        
        # Create a mapping of class names to IDs and positions
        class_name_to_info = {}
        for class_data in classes_data:
            class_id = class_data.get('id')
            class_name = class_data.get('name')
            if class_id in class_positions and class_id in class_boxes:
                pos = class_positions[class_id]
                box = class_boxes[class_id]
                class_name_to_info[class_name] = {
                    'position': pos,
                    'size': box.size,
                    'id': class_id
                }
        
        # First, collect all connections and group inheritance connections by target
        all_connections = []
        inheritance_groups = {}  # target_name -> [source_names]
        
        for class_data in classes_data:
            source_name = class_data.get('name')
            if source_name not in class_name_to_info:
                continue
                
            for connection in class_data.get('connections', []):
                target_name = connection.get('targetClass')
                relationship = connection.get('relationship', 'association')
                
                if not target_name or target_name not in class_name_to_info:
                    continue
                
                if relationship == 'inheritance':
                    # Group inheritance connections
                    if target_name not in inheritance_groups:
                        inheritance_groups[target_name] = []
                    inheritance_groups[target_name].append(source_name)
                else:
                    # Regular connection
                    all_connections.append((source_name, target_name, relationship))
        
        # Draw generalization connections (grouped inheritance)
        connections_drawn = 0
        processed_inheritance = set()
        
        for target_name, source_names in inheritance_groups.items():
            if len(source_names) > 1:
                # Multiple inheritance - use proper generalization
                print(f"🔗 Drawing generalization: {source_names} -> {target_name}")
                
                target_info = class_name_to_info[target_name]
                target_pos = target_info['position']
                target_size = target_info['size']
                
                # Calculate parent connection point (top edge center)
                parent_x = target_pos[0] + target_size[0] // 2
                parent_y = target_pos[1]  # Top edge
                parent_pos = (parent_x, parent_y)
                
                # Calculate children connection points (bottom edge centers)
                children_positions = []
                for source_name in source_names:
                    source_info = class_name_to_info[source_name]
                    source_pos = source_info['position']
                    source_size = source_info['size']
                    child_x = source_pos[0] + source_size[0] // 2
                    child_y = source_pos[1] + source_size[1]  # Bottom edge
                    children_positions.append((child_x, child_y))
                
                # Draw proper generalization
                draw_proper_generalization(
                    image, parent_pos, children_positions, 
                    line_color='black', line_width=2
                )
                
                connections_drawn += len(source_names)
                processed_inheritance.update(source_names)
            else:
                # Single inheritance - add to regular connections
                all_connections.append((source_names[0], target_name, 'inheritance'))
        
        # Draw regular connections (non-grouped)
        for source_name, target_name, relationship in all_connections:
            if relationship == 'inheritance' and source_name in processed_inheritance:
                continue  # Already drawn as part of generalization
            
            source_info = class_name_to_info[source_name]
            target_info = class_name_to_info[target_name]
            
            source_pos = source_info['position']
            source_size = source_info['size']
            target_pos = target_info['position']
            target_size = target_info['size']
            
            # Create class position tuples for edge calculation
            source_class_pos = (source_pos[0], source_pos[1], source_size[0], source_size[1])
            target_class_pos = (target_pos[0], target_pos[1], target_size[0], target_size[1])
            
            # Calculate centers for direction determination
            source_center_x = source_pos[0] + source_size[0] // 2
            source_center_y = source_pos[1] + source_size[1] // 2
            target_center_x = target_pos[0] + target_size[0] // 2
            target_center_y = target_pos[1] + target_size[1] // 2
            
            # Use ConnectionManager to get proper edge connection points
            start_point = connection_manager._get_best_connection_point(source_class_pos, target_center_x, target_center_y)
            end_point = connection_manager._get_best_connection_point(target_class_pos, source_center_x, source_center_y)
            
            # Use uniform black color for all connections
            line_color = 'black'
            
            print(f"🔗 Drawing {relationship} connection: {source_name} -> {target_name}")
            print(f"   Edge points: ({start_point.x}, {start_point.y}) -> ({end_point.x}, {end_point.y})")
            
            # Draw the connection using proper edge connection points
            drawConnection(
                image=image,
                start_x=start_point.x,
                start_y=start_point.y,
                end_x=end_point.x,
                end_y=end_point.y,
                connection_type=relationship,
                line_color=line_color,
                line_width=2
            )
            connections_drawn += 1
                
        print(f"✅ Successfully drew {connections_drawn} connections with proper generalization")
    
    def _get_relationship_symbol(self, relationship):
        """Get symbol for relationship type"""
        symbols = {
            'inheritance': '▲',
            'association': '→',
            'aggregation': '◇',
            'composition': '◆',
            'dependency': '- ->'
        }
        return symbols.get(relationship, '→')

# Initialize the UML service
uml_service = UMLDiagramService()

@app.route('/')
def index():
    """Main page route"""
    try:
        # For Vercel, we need to serve the HTML directly
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'mainPage.html')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return """
            <!DOCTYPE html>
            <html>
            <head><title>UML Diagram Builder</title></head>
            <body>
                <h1>UML Diagram Builder</h1>
                <p>Welcome to the UML Diagram Builder API!</p>
                <p>The application is running on Vercel.</p>
            </body>
            </html>
            """
    except Exception as e:
        return f"Error loading template: {str(e)}"

@app.route('/api/validate-classes', methods=['POST'])
def validate_classes():
    """Validate class data structure"""
    try:
        data = request.get_json()
        classes_data = data.get('classes', [])
        
        errors = []
        warnings = []
        
        # Check for duplicate class names
        class_names = [cls.get('name', '') for cls in classes_data]
        duplicates = [name for name in set(class_names) if class_names.count(name) > 1]
        if duplicates:
            errors.append(f"Duplicate class names found: {', '.join(duplicates)}")
        
        # Check for invalid connections
        for cls in classes_data:
            for connection in cls.get('connections', []):
                target = connection.get('targetClass')
                if target and target not in class_names:
                    warnings.append(f"Class '{cls.get('name')}' has connection to non-existent class '{target}'")
        
        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/generate-diagram', methods=['POST'])
def generate_diagram():
    """Generate UML diagram as PNG"""
    try:
        data = request.get_json()
        classes_data = data.get('classes', [])
        styling_options = data.get('styling', {})
        
        # Debug: Log the received data
        print(f"Received {len(classes_data)} classes")
        for i, cls in enumerate(classes_data):
            print(f"Class {i}: {cls.get('name', 'Unnamed')}")
            print(f"  - Attributes: {len(cls.get('attributes', []))}")
            print(f"  - Operations: {len(cls.get('operations', []))}")
            print(f"  - Connections: {len(cls.get('connections', []))}")
            for conn in cls.get('connections', []):
                print(f"    -> {conn.get('targetClass', 'Unknown')} ({conn.get('relationship', 'unknown')})")
        
        if not classes_data:
            return jsonify({'success': False, 'error': 'No classes provided'}), 400
        
        # Generate a simple diagram image
        diagram = uml_service.generate_simple_diagram(classes_data, styling_options)
        
        if diagram:
            # Convert PIL image to base64 for JSON response
            try:
                buffer = io.BytesIO()
                diagram.save(buffer, format='PNG')
                buffer.seek(0)  # Reset buffer position
                img_bytes = buffer.getvalue()
                
                if len(img_bytes) == 0:
                    raise ValueError("Generated image is empty")
                
                img_str = base64.b64encode(img_bytes).decode('utf-8')
                
                # Validate base64 string
                if not img_str or len(img_str) < 10:
                    raise ValueError("Generated base64 string is invalid")
                
                return jsonify({
                    'success': True,
                    'message': 'PNG diagram generated successfully!',
                    'image_data': f'data:image/png;base64,{img_str}',
                    'classes_count': len(classes_data)
                })
            except Exception as base64_error:
                print(f"Base64 conversion error: {base64_error}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to convert image to base64: {str(base64_error)}'
                }), 500
        else:
            return jsonify({
                'success': True,
                'message': 'Diagram processed successfully!',
                'classes_count': len(classes_data)
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preview-class', methods=['POST'])
def preview_class():
    """Generate a preview of a single class"""
    try:
        data = request.get_json()
        class_data = data.get('classData', {})
        
        # Create text representation
        class_repr = uml_service.create_class_box(class_data)
        
        return jsonify({
            'success': True,
            'preview_text': class_repr,
            'message': 'Class preview generated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Vercel requires the app to be callable
if __name__ == '__main__':
    app.run(debug=True)
else:
    # This is how Vercel will call the app
    pass