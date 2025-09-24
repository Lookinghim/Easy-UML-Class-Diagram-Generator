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

try:
    from diagramDraw import mergeBoxes, loadFonts, note, clear_notes
    from connection import ConnectionManager, ConnectionType, UMLConnection
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback for missing modules
    def mergeBoxes(*args, **kwargs):
        return None
    def loadFonts():
        return None, 12
    def note(*args, **kwargs):
        return (0, 0, 100, 50)
    def clear_notes():
        pass
    class ConnectionManager:
        def __init__(self): pass
        def add_connection(self, conn): return True
    class ConnectionType:
        INHERITANCE = "inheritance"
        ASSOCIATION = "association"
        AGGREGATION = "aggregation"
        COMPOSITION = "composition"
        DEPENDENCY = "dependency"
    class UMLConnection:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

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
        """Generate a complete UML diagram with attributes, operations, and connections"""
        if not classes_data:
            return None
        
        try:
            from PIL import ImageDraw, ImageFont
            
            img_width = styling_options.get('image_width', 1200) if styling_options else 1200
            img_height = styling_options.get('image_height', 800) if styling_options else 800
            
            # Create basic image
            diagram_image = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(diagram_image)
            
            # Try to get a font
            try:
                font = ImageFont.truetype("arial.ttf", 12)
                small_font = ImageFont.truetype("arial.ttf", 10)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            class_boxes = {}  # Store box positions for connection drawing
            
            # Calculate layout - arrange classes in a grid
            classes_per_row = min(3, len(classes_data))
            row_height = 250
            col_width = img_width // classes_per_row
            
            # Draw classes
            for i, class_data in enumerate(classes_data):
                row = i // classes_per_row
                col = i % classes_per_row
                
                box_x = col * col_width + 50
                box_y = row * row_height + 50
                box_width = col_width - 100
                
                # Calculate box height based on content
                class_name = class_data.get('name', f'Class{i+1}')
                attributes = class_data.get('attributes', [])
                operations = class_data.get('operations', [])
                
                # Basic dimensions
                line_height = 15
                header_height = 25
                section_padding = 10
                
                # Calculate required height
                attr_height = len(attributes) * line_height + (section_padding if attributes else 0)
                op_height = len(operations) * line_height + (section_padding if operations else 0)
                box_height = header_height + attr_height + op_height + 30
                
                # Store box info for connections
                class_boxes[class_data.get('id', f'class_{i}')] = {
                    'x': box_x, 'y': box_y, 'width': box_width, 'height': box_height,
                    'center_x': box_x + box_width // 2, 'center_y': box_y + box_height // 2,
                    'name': class_name
                }
                
                # Draw main box
                outline_color = styling_options.get('outline_color', 'black') if styling_options else 'black'
                outline_width = styling_options.get('outline_width', 2) if styling_options else 2
                
                draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], 
                             outline=outline_color, width=outline_width)
                
                # Draw class name (header)
                draw.text((box_x + 10, box_y + 5), class_name, fill='black', font=font)
                
                # Draw separator line after class name
                current_y = box_y + header_height
                draw.line([box_x, current_y, box_x + box_width, current_y], fill='black', width=1)
                
                # Draw attributes
                if attributes:
                    current_y += 5
                    for attr in attributes:
                        visibility = self.get_visibility_symbol(attr.get('visibility', 'private'))
                        attr_name = attr.get('name', '')
                        attr_type = attr.get('type', '')
                        attr_text = f"{visibility}{attr_name}: {attr_type}"
                        draw.text((box_x + 10, current_y), attr_text, fill='black', font=small_font)
                        current_y += line_height
                    
                    # Draw separator line after attributes
                    draw.line([box_x, current_y + 5, box_x + box_width, current_y + 5], fill='black', width=1)
                    current_y += 10
                
                # Draw operations
                if operations:
                    for op in operations:
                        visibility = self.get_visibility_symbol(op.get('visibility', 'public'))
                        op_name = op.get('name', '')
                        return_type = op.get('returnType', 'void')
                        
                        # Format parameters
                        params = op.get('parameters', [])
                        param_str = ', '.join([f"{p.get('name', '')}: {p.get('type', '')}" for p in params])
                        
                        op_text = f"{visibility}{op_name}({param_str}): {return_type}"
                        draw.text((box_x + 10, current_y), op_text, fill='black', font=small_font)
                        current_y += line_height
            
            # Draw connections
            self._draw_connections_simple(draw, classes_data, class_boxes)
            
            return diagram_image
            
        except Exception as e:
            print(f"Error generating diagram: {e}")
            # Return a minimal valid image with error info
            try:
                minimal_image = Image.new('RGB', (400, 300), 'white')
                draw = ImageDraw.Draw(minimal_image)
                draw.text((10, 10), "UML Diagram", fill='black')
                draw.text((10, 30), f"Error: {str(e)}", fill='red')
                return minimal_image
            except:
                return None
    
    def _draw_connections_simple(self, draw, classes_data, class_boxes):
        """Draw connections between classes"""
        # Create a mapping of class names to box info
        name_to_box = {box_info['name']: box_info for box_info in class_boxes.values()}
        
        for class_data in classes_data:
            source_box = class_boxes.get(class_data.get('id'))
            if not source_box:
                continue
                
            for connection in class_data.get('connections', []):
                target_name = connection.get('targetClass')
                if not target_name:
                    continue
                    
                target_box = name_to_box.get(target_name)
                if not target_box:
                    continue
                
                # Draw connection line
                relationship = connection.get('relationship', 'association')
                
                # Calculate connection points (center to center for simplicity)
                start_x, start_y = source_box['center_x'], source_box['center_y']
                end_x, end_y = target_box['center_x'], target_box['center_y']
                
                # Draw the connection line
                draw.line([start_x, start_y, end_x, end_y], fill='blue', width=2)
                
                # Draw relationship indicator
                mid_x = (start_x + end_x) // 2
                mid_y = (start_y + end_y) // 2
                
                # Draw relationship symbol/text
                rel_text = self._get_relationship_symbol(relationship)
                if rel_text:
                    draw.text((mid_x - 10, mid_y - 10), rel_text, fill='blue')
    
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