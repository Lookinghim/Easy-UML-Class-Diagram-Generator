#!/usr/bin/env python3

"""
Flask Web Application for UML Class Diagram Generator
Provides web interface and API endpoints for creating UML diagrams
"""

from flask import Flask, render_template, request, jsonify, send_file, url_for
from flask_cors import CORS
import os
import json
import uuid
import tempfile
from datetime import datetime
from PIL import Image
import io
import base64

# Import our UML generation modules
from diagramDraw import mergeBoxes, loadFonts, note, clear_notes
from connection import ConnectionManager, ConnectionType, UMLConnection

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)  # Enable CORS for API calls

# Global storage for diagram data (in production, use a database)
diagrams_storage = {}

class UMLDiagramService:
    """Service class to handle UML diagram generation"""
    
    def __init__(self):
        self.base_font, self.font_size = loadFonts()
        self.connection_manager = ConnectionManager()
    
    def create_class_box(self, class_data, outline_color='blue', outline_width=2):
        """Create a UML class box from class data"""
        class_name = class_data.get('name', 'UnnamedClass')
        
        # Format attributes
        attributes = []
        for attr in class_data.get('attributes', []):
            visibility_symbol = self.get_visibility_symbol(attr.get('visibility', 'private'))
            attr_text = f"{visibility_symbol}{attr.get('name', '')}: {attr.get('type', '')}"
            attributes.append(attr_text)
        
        # Format operations
        operations = []
        for op in class_data.get('operations', []):
            visibility_symbol = self.get_visibility_symbol(op.get('visibility', 'public'))
            op_text = f"{visibility_symbol}{op.get('name', '')}"
            operations.append(op_text)
        
        attributes_text = '\n'.join(attributes) if attributes else ''
        operations_text = '\n'.join(operations) if operations else ''
        
        # Create the class box
        class_box = mergeBoxes(
            class_name,
            attributes_text,
            operations_text,
            self.base_font,
            self.font_size,
            outline_colour=outline_color,
            outline_width=outline_width
        )
        
        return class_box
    
    def get_visibility_symbol(self, visibility):
        """Convert visibility string to UML symbol"""
        symbols = {
            'public': '+',
            'private': '-',
            'protected': '#'
        }
        return symbols.get(visibility, '+')
    
    def create_diagram_preview(self, class_box, width=200, height=150):
        """Create a small preview image of a class box"""
        # Create a preview image
        preview_img = Image.new('RGB', (width, height), 'white')
        
        # Calculate position to center the class box
        box_width, box_height = class_box.size
        x = max(0, (width - box_width) // 2)
        y = max(0, (height - box_height) // 2)
        
        # Paste the class box onto the preview
        preview_img.paste(class_box, (x, y))
        
        return preview_img
    
    def generate_full_diagram(self, classes_data, styling_options=None):
        """Generate a complete UML diagram with multiple classes and connections"""
        if not classes_data:
            return None
        
        # Clear any existing notes
        clear_notes()
        
        # Default styling options
        if styling_options is None:
            styling_options = {
                'outline_color': 'blue',
                'outline_width': 2,
                'image_width': 1200,
                'image_height': 800
            }
        
        # Create the main diagram image
        img_width = styling_options.get('image_width', 1200)
        img_height = styling_options.get('image_height', 800)
        diagram_image = Image.new('RGB', (img_width, img_height), 'white')
        
        # Create class boxes and track their positions
        class_boxes = {}
        class_positions = {}
        
        # Calculate layout positions (simple grid layout)
        classes_per_row = max(1, int(len(classes_data) ** 0.5))
        box_spacing_x = img_width // (classes_per_row + 1)
        box_spacing_y = img_height // (len(classes_data) // classes_per_row + 2)
        
        for i, class_data in enumerate(classes_data):
            class_id = class_data.get('id', str(i))
            
            # Create class box
            class_box = self.create_class_box(
                class_data,
                styling_options.get('outline_color', 'blue'),
                styling_options.get('outline_width', 2)
            )
            
            # Calculate position
            row = i // classes_per_row
            col = i % classes_per_row
            x = box_spacing_x * (col + 1) - class_box.size[0] // 2
            y = box_spacing_y * (row + 1) - class_box.size[1] // 2
            
            # Ensure positions are within bounds
            x = max(0, min(x, img_width - class_box.size[0]))
            y = max(0, min(y, img_height - class_box.size[1]))
            
            class_positions[class_id] = (x, y)
            class_boxes[class_id] = class_box
            
            # Paste class box onto diagram
            diagram_image.paste(class_box, (x, y))
            
            # Add notes if present
            for note_data in class_data.get('notes', []):
                if note_data.get('text', '').strip():
                    note_color = self.get_note_color(note_data.get('type', 'Standard'))
                    note(
                        diagram_image,
                        note_data['text'],
                        (x, y),
                        class_box.size,
                        self.base_font,
                        note_color=note_color
                    )
        
        # Draw connections
        self._draw_connections(diagram_image, classes_data, class_positions, class_boxes)
        
        return diagram_image
    
    def get_note_color(self, note_type):
        """Get color for different note types"""
        colors = {
            'Standard': 'yellow',
            'Information': 'lightblue',
            'Warning': 'orange',
            'Success': 'lightgreen',
            'Confirmation': 'lightcyan',
            'Decorative': 'lavender'
        }
        return colors.get(note_type, 'yellow')
    
    def _draw_connections(self, image, classes_data, class_positions, class_boxes):
        """Draw connections between classes using basic drawing"""
        from PIL import ImageDraw
        
        draw = ImageDraw.Draw(image)
        
        # Create a mapping of class names to IDs for connection lookup
        class_name_to_id = {cls['name']: cls['id'] for cls in classes_data}
        
        for class_data in classes_data:
            source_id = class_data['id']
            source_pos = class_positions.get(source_id)
            source_box = class_boxes.get(source_id)
            
            if not source_pos or not source_box:
                continue
            
            for connection in class_data.get('connections', []):
                target_name = connection.get('targetClass')
                target_id = class_name_to_id.get(target_name)
                
                if not target_id:
                    continue
                
                target_pos = class_positions.get(target_id)
                target_box = class_boxes.get(target_id)
                
                if not target_pos or not target_box:
                    continue
                
                # Calculate connection points (center to center for simplicity)
                source_center_x = source_pos[0] + source_box.size[0] // 2
                source_center_y = source_pos[1] + source_box.size[1] // 2
                target_center_x = target_pos[0] + target_box.size[0] // 2
                target_center_y = target_pos[1] + target_box.size[1] // 2
                
                # Draw basic line
                relationship = connection.get('relationship', 'association')
                line_color = 'black'
                line_width = 2
                
                if relationship == 'inheritance':
                    line_color = 'blue'
                elif relationship == 'composition':
                    line_color = 'red'
                elif relationship == 'aggregation':
                    line_color = 'green'
                elif relationship == 'dependency':
                    line_color = 'gray'
                
                # Draw connection line
                draw.line([
                    (source_center_x, source_center_y),
                    (target_center_x, target_center_y)
                ], fill=line_color, width=line_width)
                
                # Add arrowhead for directed relationships
                if relationship in ['inheritance', 'dependency']:
                    self._draw_arrowhead(draw, source_center_x, source_center_y, 
                                       target_center_x, target_center_y, line_color)
    
    def _draw_arrowhead(self, draw, start_x, start_y, end_x, end_y, color):
        """Draw a simple arrowhead at the end of a line"""
        import math
        
        # Calculate angle of the line
        angle = math.atan2(end_y - start_y, end_x - start_x)
        
        # Arrowhead size
        arrow_length = 10
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Calculate arrowhead points
        x1 = end_x - arrow_length * math.cos(angle - arrow_angle)
        y1 = end_y - arrow_length * math.sin(angle - arrow_angle)
        x2 = end_x - arrow_length * math.cos(angle + arrow_angle)
        y2 = end_y - arrow_length * math.sin(angle + arrow_angle)
        
        # Draw arrowhead
        draw.polygon([(end_x, end_y), (x1, y1), (x2, y2)], fill=color)

# Initialize the UML service
uml_service = UMLDiagramService()

@app.route('/')
def index():
    """Main page route"""
    return render_template('mainPage.html')

@app.route('/api/preview-class', methods=['POST'])
def preview_class():
    """Generate a preview of a single class box"""
    try:
        data = request.get_json()
        class_data = data.get('classData', {})
        styling_options = data.get('styling', {})
        
        # Create class box
        class_box = uml_service.create_class_box(
            class_data,
            styling_options.get('outline_color', 'blue'),
            styling_options.get('outline_width', 2)
        )
        
        # Create preview
        preview = uml_service.create_diagram_preview(class_box)
        
        # Convert to base64 for JSON response
        buffer = io.BytesIO()
        preview.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'preview': f'data:image/png;base64,{img_str}',
            'width': preview.width,
            'height': preview.height
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-diagram', methods=['POST'])
def generate_diagram():
    """Generate complete UML diagram"""
    try:
        data = request.get_json()
        classes_data = data.get('classes', [])
        styling_options = data.get('styling', {})
        
        if not classes_data:
            return jsonify({'success': False, 'error': 'No classes provided'}), 400
        
        # Generate diagram
        diagram = uml_service.generate_full_diagram(classes_data, styling_options)
        
        if diagram is None:
            return jsonify({'success': False, 'error': 'Failed to generate diagram'}), 500
        
        # Save diagram temporarily
        diagram_id = str(uuid.uuid4())
        temp_path = os.path.join(tempfile.gettempdir(), f'uml_diagram_{diagram_id}.png')
        diagram.save(temp_path)
        
        # Store diagram info
        diagrams_storage[diagram_id] = {
            'path': temp_path,
            'created': datetime.now(),
            'classes_count': len(classes_data)
        }
        
        return jsonify({
            'success': True,
            'diagram_id': diagram_id,
            'download_url': url_for('download_diagram', diagram_id=diagram_id)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<diagram_id>')
def download_diagram(diagram_id):
    """Download generated diagram"""
    try:
        diagram_info = diagrams_storage.get(diagram_id)
        if not diagram_info:
            return jsonify({'error': 'Diagram not found'}), 404
        
        diagram_path = diagram_info['path']
        if not os.path.exists(diagram_path):
            return jsonify({'error': 'Diagram file not found'}), 404
        
        return send_file(
            diagram_path,
            as_attachment=True,
            download_name=f'uml_diagram_{diagram_id}.png',
            mimetype='image/png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        
        # Check for empty classes
        empty_classes = []
        for cls in classes_data:
            if (not cls.get('attributes') and 
                not cls.get('operations') and 
                not cls.get('notes')):
                empty_classes.append(cls.get('name', 'Unnamed'))
        
        if empty_classes:
            warnings.append(f"Empty classes found: {', '.join(empty_classes)}")
        
        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create static and templates directories if they don't exist
    os.makedirs('../static', exist_ok=True)
    os.makedirs('../templates', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
