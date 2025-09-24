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
        """Generate a simple diagram representation for Vercel"""
        if not classes_data:
            return None
        
        # Create a simple image with PIL
        try:
            img_width = styling_options.get('image_width', 800) if styling_options else 800
            img_height = styling_options.get('image_height', 600) if styling_options else 600
            
            # Create basic image
            diagram_image = Image.new('RGB', (img_width, img_height), 'white')
            
            # For Vercel deployment, return a simple placeholder
            return diagram_image
        except Exception as e:
            print(f"Error generating diagram: {e}")
            return None

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

@app.route('/api/export-plantuml', methods=['POST'])
def export_plantuml():
    """Export diagram as PlantUML code"""
    try:
        data = request.get_json()
        classes_data = data.get('classes', [])
        
        if not classes_data:
            return jsonify({'success': False, 'error': 'No classes provided'}), 400
        
        # Generate PlantUML code
        plantuml_code = generate_plantuml_code(classes_data)
        
        return jsonify({
            'success': True,
            'plantuml_code': plantuml_code
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-diagram', methods=['POST'])
def generate_diagram():
    """Generate UML diagram - simplified for Vercel"""
    try:
        data = request.get_json()
        classes_data = data.get('classes', [])
        styling_options = data.get('styling', {})
        
        if not classes_data:
            return jsonify({'success': False, 'error': 'No classes provided'}), 400
        
        # For Vercel deployment, return a success message with PlantUML code instead
        plantuml_code = generate_plantuml_code(classes_data)
        
        return jsonify({
            'success': True,
            'message': 'Diagram generated successfully! PlantUML code provided.',
            'plantuml_code': plantuml_code,
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

def generate_plantuml_code(classes_data):
    """Generate PlantUML code from classes data"""
    uml_text = "@startuml\n\n"
    
    # Add classes
    for cls in classes_data:
        class_name = cls.get('name', 'UnnamedClass')
        uml_text += f"class {class_name} {{\n"
        
        # Add notes
        for note in cls.get('notes', []):
            if note.get('text', '').strip():
                uml_text += f"  note [{note.get('type', 'Standard')}]: {note['text']}\n"
        
        # Add separator if notes exist and other elements exist
        if cls.get('notes') and (cls.get('attributes') or cls.get('operations')):
            uml_text += "  --\n"
        
        # Add attributes
        for attr in cls.get('attributes', []):
            visibility = uml_service.get_visibility_symbol(attr.get('visibility', 'private'))
            uml_text += f"  {visibility}{attr.get('name', '')}: {attr.get('type', '')}\n"
        
        # Add separator between attributes and operations
        if cls.get('attributes') and cls.get('operations'):
            uml_text += "  --\n"
        
        # Add operations
        for op in cls.get('operations', []):
            visibility = uml_service.get_visibility_symbol(op.get('visibility', 'public'))
            uml_text += f"  {visibility}{op.get('name', '')}\n"
        
        uml_text += "}\n\n"
    
    # Add connections
    for cls in classes_data:
        for connection in cls.get('connections', []):
            if connection.get('targetClass'):
                relationship_symbol = {
                    'inheritance': '<|--',
                    'association': '--',
                    'aggregation': 'o--',
                    'composition': '*--',
                    'dependency': '..>'
                }.get(connection.get('relationship', 'association'), '--')
                
                uml_text += f"{cls['name']} {relationship_symbol} {connection['targetClass']}\n"
    
    uml_text += "\n@enduml"
    return uml_text

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