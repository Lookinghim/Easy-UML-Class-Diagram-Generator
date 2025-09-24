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
from diagramDraw import mergeBoxes, loadFonts, note, clear_notes, drawConnection
from connection import ConnectionManager, ConnectionType, UMLConnection
from classBox import createSingleUMLClass

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
        """Create a UML class box from class data using classBox module"""
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
            
            # Format parameters if they exist
            params = op.get('parameters', [])
            if params:
                param_str = ', '.join([f"{p.get('name', '')}: {p.get('type', '')}" for p in params])
                op_text = f"{visibility_symbol}{op.get('name', '')}({param_str}): {op.get('returnType', 'void')}"
            else:
                op_text = f"{visibility_symbol}{op.get('name', '')}(): {op.get('returnType', 'void')}"
            operations.append(op_text)
        
        attributes_text = '\n'.join(attributes) if attributes else ''
        operations_text = '\n'.join(operations) if operations else ''
        
        # Use the existing mergeBoxes function with custom styling
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
        
        # Calculate layout positions (single column layout)
        start_x = 80  # Starting x position
        start_y = 80  # Starting y position
        row_height = 350  # Height between rows
        
        for i, class_data in enumerate(classes_data):
            class_id = class_data.get('id', str(i))
            
            # Create class box
            class_box = self.create_class_box(
                class_data,
                styling_options.get('outline_color', 'blue'),
                styling_options.get('outline_width', 2)
            )
            
            # Calculate position - single column layout
            x = start_x
            y = start_y + (i * row_height)
            
            # Ensure positions are within bounds
            x = max(0, min(x, img_width - class_box.size[0]))
            y = max(0, min(y, img_height - class_box.size[1]))
            
            class_positions[class_id] = (x, y)
            class_boxes[class_id] = class_box
            
            # Paste class box onto diagram
            diagram_image.paste(class_box, (x, y))
            
            # Add notes if present and have actual content
            for note_data in class_data.get('notes', []):
                note_text = note_data.get('text', '').strip()
                if note_text and len(note_text) > 0:
                    note_color = self.get_note_color(note_data.get('type', 'Standard'))
                    note(
                        diagram_image,
                        note_text,
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
        """Draw connections between classes using proper edge connection points and generalization detection"""
        from diagramDraw import draw_proper_generalization
        
        # Create a mapping of class names to IDs for connection lookup
        class_name_to_id = {cls['name']: cls['id'] for cls in classes_data}
        
        # Create connection manager and register all class positions
        connection_manager = ConnectionManager()
        class_name_to_info = {}
        
        for class_data in classes_data:
            class_id = class_data['id']
            class_name = class_data['name']
            if class_id in class_positions and class_id in class_boxes:
                pos = class_positions[class_id]
                size = class_boxes[class_id].size
                connection_manager.add_class_position(class_name, pos[0], pos[1], size[0], size[1])
                class_name_to_info[class_name] = {
                    'position': pos,
                    'size': size,
                    'id': class_id
                }
        
        # First, collect all connections and group inheritance connections by target
        all_connections = []
        inheritance_groups = {}  # target_name -> [source_names]
        
        for class_data in classes_data:
            source_name = class_data['name']
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
            
            # Use ConnectionManager to calculate proper edge connection points
            source_class_pos = (source_pos[0], source_pos[1], source_size[0], source_size[1])
            target_class_pos = (target_pos[0], target_pos[1], target_size[0], target_size[1])
            
            # Calculate centers for direction determination
            target_center_x = target_pos[0] + target_size[0] // 2
            target_center_y = target_pos[1] + target_size[1] // 2
            source_center_x = source_pos[0] + source_size[0] // 2
            source_center_y = source_pos[1] + source_size[1] // 2
            
            # Get proper edge connection points using ConnectionManager logic
            start_point = connection_manager._get_best_connection_point(source_class_pos, target_center_x, target_center_y)
            end_point = connection_manager._get_best_connection_point(target_class_pos, source_center_x, source_center_y)
            
            # Use uniform black color for all connections
            line_color = 'black'
            
            # Use the proper drawConnection function with edge connection points
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
