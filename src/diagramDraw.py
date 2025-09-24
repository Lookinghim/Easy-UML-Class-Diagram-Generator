from PIL import Image, ImageDraw, ImageFont

""" Variables """
FONT_NAME = "arial.ttf"
FONT_SIZE = 12
FONT_SIZE_ITALIC = 12

PADDING_X = 10
PADDING_Y = 5
MAX_BOX_WIDTH = 250  # Maximum width for UML boxes in pixels

OUTLINE_COLOUR = 'black'
OUTLINE_WIDTH = 1

def loadFonts():
    """ Functions for drawing """
    try:
        base = ImageFont.truetype(FONT_NAME, FONT_SIZE)
        italic = ImageFont.truetype(FONT_NAME, FONT_SIZE_ITALIC)
    except Exception:
        base = ImageFont.load_default()
        italic = base
    return base, italic

def calculateBoxWidth(text, font):
    lines = text.split('\n')
    max_width = max(font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines)
    calculated_width = max_width + (PADDING_X * 2)  # Padding on both left and right
    return min(calculated_width, MAX_BOX_WIDTH)

def calculateBoxHeight(text, font):
    lines = text.split('\n')
    total_height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines)
    return total_height + (PADDING_Y * 2)  # Padding on both top and bottom



def drawBox(boxWidth, boxHeight, outline_colour=None, outline_width=None):
    """ Functions for drawing UML components """
    # Use default values if not provided
    if outline_colour is None:
        outline_colour = OUTLINE_COLOUR
    if outline_width is None:
        outline_width = OUTLINE_WIDTH
        
    # Create image with white background
    image = Image.new('RGB', (boxWidth, boxHeight), 'white')
    draw = ImageDraw.Draw(image)

    # Draw rectangle border with customizable outline
    draw.rectangle([0, 0, boxWidth-1, boxHeight-1], outline=outline_colour, width=outline_width)

    return image

def drawNameBox(boxWidth, boxHeight, text, font, fontSize, outline_colour=None, outline_width=None):
    # Start with a basic box
    image = drawBox(boxWidth, boxHeight, outline_colour, outline_width)
    draw = ImageDraw.Draw(image)
    
    # Draw text centered horizontally
    lines = text.split('\n')
    y_offset = PADDING_Y
    
    for line in lines:
        # Get text width for centering
        text_bbox = font.getbbox(line)
        text_width = text_bbox[2] - text_bbox[0]
        
        # Center horizontally
        x_position = (boxWidth - text_width) // 2
        
        # Draw text
        draw.text((x_position, y_offset), line, font=font, fill='black')
        
        # Move to next line
        text_height = text_bbox[3] - text_bbox[1]
        y_offset += text_height
    
    return image


def drawAttributeBox(boxWidth, boxHeight, text, font, fontSize, outline_colour=None, outline_width=None):
    # Start with a basic box
    image = drawBox(boxWidth, boxHeight, outline_colour, outline_width)
    draw = ImageDraw.Draw(image)
    
    # Draw attributes (left-aligned)
    lines = text.split('\n')
    y_offset = PADDING_Y
    
    for line in lines:
        if line.strip():  # Skip empty lines
            # Left-align attributes
            draw.text((PADDING_X, y_offset), line, font=font, fill='black')
            
            # Move to next line
            text_bbox = font.getbbox(line)
            text_height = text_bbox[3] - text_bbox[1]
            y_offset += text_height
    
    return image

def drawOperationBox(boxWidth, boxHeight, text, font, fontSize, outline_colour=None, outline_width=None):
    # Start with a basic box
    image = drawBox(boxWidth, boxHeight, outline_colour, outline_width)
    draw = ImageDraw.Draw(image)
    
    # Draw operations (left-aligned)
    lines = text.split('\n')
    y_offset = PADDING_Y
    
    for line in lines:
        if line.strip():  # Skip empty lines
            # Left-align operations
            draw.text((PADDING_X, y_offset), line, font=font, fill='black')
            
            # Move to next line
            text_bbox = font.getbbox(line)
            text_height = text_bbox[3] - text_bbox[1]
            y_offset += text_height
    
    return image

def mergeBoxes(name, attributes, operations, font, fontSize, outline_colour=None, outline_width=None):
    # Use default values if not provided
    if outline_colour is None:
        outline_colour = OUTLINE_COLOUR
    if outline_width is None:
        outline_width = OUTLINE_WIDTH
        
    # Calculate dimensions for each section
    name_width = calculateBoxWidth(name, font)
    name_height = calculateBoxHeight(name, font)
    
    attr_width = calculateBoxWidth(attributes, font) if attributes else name_width
    attr_height = calculateBoxHeight(attributes, font) if attributes else 20
    
    ops_width = calculateBoxWidth(operations, font) if operations else name_width
    ops_height = calculateBoxHeight(operations, font) if operations else 20
    
    # Use the maximum width for consistency
    max_width = max(name_width, attr_width, ops_width)
    total_height = name_height + attr_height + ops_height
    
    # Create the final merged image with white background
    merged_image = Image.new('RGB', (max_width, total_height), 'white')
    draw = ImageDraw.Draw(merged_image)
    
    # Draw the outer border with custom outline
    draw.rectangle([0, 0, max_width-1, total_height-1], outline=outline_colour, width=outline_width)
    
    # Draw name section
    y_offset = PADDING_Y
    lines = name.split('\n')
    for line in lines:
        text_bbox = font.getbbox(line)
        text_width = text_bbox[2] - text_bbox[0]
        x_position = (max_width - text_width) // 2  # Center name
        draw.text((x_position, y_offset), line, font=font, fill='black')
        text_height = text_bbox[3] - text_bbox[1]
        y_offset += text_height
    
    # Draw horizontal line after name section
    name_section_bottom = name_height
    draw.line([0, name_section_bottom, max_width, name_section_bottom], fill=outline_colour, width=outline_width)
    
    # Draw attributes section
    if attributes:
        y_offset = name_height + PADDING_Y
        lines = attributes.split('\n')
        for line in lines:
            if line.strip():
                draw.text((PADDING_X, y_offset), line, font=font, fill='black')
                text_bbox = font.getbbox(line)
                text_height = text_bbox[3] - text_bbox[1]
                y_offset += text_height
    
    # Draw horizontal line after attributes section
    attr_section_bottom = name_height + attr_height
    draw.line([0, attr_section_bottom, max_width, attr_section_bottom], fill=outline_colour, width=outline_width)
    
    # Draw operations section
    if operations:
        y_offset = name_height + attr_height + PADDING_Y
        lines = operations.split('\n')
        for line in lines:
            if line.strip():
                draw.text((PADDING_X, y_offset), line, font=font, fill='black')
                text_bbox = font.getbbox(line)
                text_height = text_bbox[3] - text_bbox[1]
                y_offset += text_height
    

    return merged_image

def draw_generalization_line_only(image, start_x, start_y, end_x, end_y, line_color='black', line_width=2):
    """Draw a plain line for generalization (no arrow head)"""
    draw = ImageDraw.Draw(image)
    draw.line([(start_x, start_y), (end_x, end_y)], fill=line_color, width=line_width)

def draw_proper_generalization(image, parent_pos, children_positions, line_color='blue', line_width=2):
    """
    Draw proper UML generalization with correct routing:
    1. Short vertical line down from parent
    2. Horizontal line across (if multiple children)
    3. Vertical lines to each child
    4. Triangle at parent connection point
    
    Args:
        image: PIL Image to draw on
        parent_pos: (x, y) position of parent class connection point
        children_positions: List of (x, y) positions of children connection points
        line_color: Color of lines and triangle
        line_width: Width of lines
    """
    if not children_positions:
        return
    
    parent_x, parent_y = parent_pos
    
    # Calculate the horizontal line position (midway between parent and children)
    children_y_positions = [pos[1] for pos in children_positions]
    min_child_y = min(children_y_positions)
    horizontal_y = parent_y + (min_child_y - parent_y) // 2
    
    # Find the leftmost and rightmost child positions
    children_x_positions = [pos[0] for pos in children_positions]
    leftmost_x = min(children_x_positions)
    rightmost_x = max(children_x_positions)
    
    draw = ImageDraw.Draw(image)
    
    # Triangle dimensions (must match the triangle function)
    triangle_size = 12
    triangle_bottom_y = parent_y + triangle_size
    
    # 1. Draw vertical line down from bottom of triangle to horizontal line
    draw.line([(parent_x, triangle_bottom_y), (parent_x, horizontal_y)], 
              fill=line_color, width=line_width)
    
    # 2. Draw horizontal line across (only if multiple children)
    if len(children_positions) > 1:
        draw.line([(leftmost_x, horizontal_y), (rightmost_x, horizontal_y)], 
                  fill=line_color, width=line_width)
    
    # 3. Draw vertical lines from horizontal line to each child
    for child_x, child_y in children_positions:
        if len(children_positions) == 1:
            # Single child: direct line from triangle bottom to child
            draw.line([(parent_x, triangle_bottom_y), (child_x, child_y)], 
                     fill=line_color, width=line_width)
        else:
            # Multiple children: from horizontal line to child
            draw.line([(child_x, horizontal_y), (child_x, child_y)], 
                     fill=line_color, width=line_width)
    
    # 4. Draw triangle at parent connection point (tip touches parent edge)
    draw_fixed_generalization_triangle(image, parent_x, parent_y, line_color, line_width)

def draw_fixed_generalization_triangle(image, x, y, line_color='blue', line_width=2):
    """Draw triangle positioned below parent class (not overlapping text)"""
    draw = ImageDraw.Draw(image)
    
    # Triangle dimensions
    triangle_size = 12
    
    # Triangle pointing upward, but positioned BELOW the parent class edge
    # The tip touches the parent class edge, base extends downward
    vertices = [
        (x, y),                           # Top point (tip) - at parent edge
        (x - triangle_size//2, y + triangle_size),   # Bottom left
        (x + triangle_size//2, y + triangle_size)    # Bottom right
    ]
    
    # Draw triangle with white fill and colored outline
    draw.polygon(vertices, outline=line_color, width=line_width, fill='white')

def draw_generalization_triangle(image, x, y, direction_x, direction_y, line_color='black', line_width=2):
    """Draw a single triangle for generalization at the parent class"""
    import math
    
    draw = ImageDraw.Draw(image)
    
    # Triangle dimensions
    triangle_length = 15
    triangle_width = 12
    
    # Normalize direction
    length = math.sqrt(direction_x**2 + direction_y**2)
    if length == 0:
        return
    
    dx_norm = direction_x / length
    dy_norm = direction_y / length
    
    # Triangle points
    tip_x = x
    tip_y = y
    
    # Base of triangle
    base_x = x - dx_norm * triangle_length
    base_y = y - dy_norm * triangle_length
    
    # Perpendicular for triangle width
    perp_x = -dy_norm * triangle_width / 2
    perp_y = dx_norm * triangle_width / 2
    
    # Triangle vertices
    vertices = [
        (tip_x, tip_y),  # Tip point
        (base_x + perp_x, base_y + perp_y),  # Base left
        (base_x - perp_x, base_y - perp_y)   # Base right
    ]
    
    # Draw triangle outline (not filled)
    draw.polygon(vertices, outline=line_color, width=line_width, fill='white')

def drawConnection(image, start_x, start_y, end_x, end_y, connection_type='association', line_color='black', line_width=1):
    """
    Draw UML relationship arrows on an image
    
    Args:
        image: PIL Image to draw on
        start_x, start_y: Starting point coordinates
        end_x, end_y: Ending point coordinates  
        connection_type: Type of UML relationship
        line_color: Color of the line and arrow
        line_width: Width of the line
    
    Connection types:
        - 'association': Simple line with arrow
        - 'aggregation': Line with empty diamond
        - 'composition': Line with filled diamond
        - 'inheritance': Line with empty triangle (old way)
        - 'inheritance_line': Plain line only (for proper generalization)
        - 'realization': Dashed line with empty triangle
        - 'dependency': Dashed line with arrow
    """
    draw = ImageDraw.Draw(image)
    
    # Draw the main line
    if connection_type in ['realization', 'dependency']:
        # Draw dashed line
        draw_dashed_line(draw, start_x, start_y, end_x, end_y, line_color, line_width)
    else:
        # Draw solid line
        draw.line([(start_x, start_y), (end_x, end_y)], fill=line_color, width=line_width)
    
    # Draw appropriate arrow/symbol at the end
    if connection_type == 'association':
        draw_arrow_head(draw, start_x, start_y, end_x, end_y, line_color, line_width)
    elif connection_type == 'aggregation':
        draw_diamond(draw, end_x, end_y, start_x, start_y, line_color, line_width, filled=False)
    elif connection_type == 'composition':
        draw_diamond(draw, end_x, end_y, start_x, start_y, line_color, line_width, filled=True)
    elif connection_type == 'inheritance':
        draw_triangle(draw, start_x, start_y, end_x, end_y, line_color, line_width, filled=False)
    elif connection_type == 'inheritance_line':
        # Plain line only - no arrow (for proper generalization)
        pass  # Line already drawn above, no additional symbol needed
    elif connection_type == 'realization':
        draw_triangle(draw, start_x, start_y, end_x, end_y, line_color, line_width, filled=False)
    elif connection_type == 'dependency':
        draw_arrow_head(draw, start_x, start_y, end_x, end_y, line_color, line_width)

def draw_dashed_line(draw, x1, y1, x2, y2, color, width):
    """Draw a dashed line between two points"""
    import math
    
    # Calculate line length and direction
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    
    if length == 0:
        return
    
    # Normalize direction
    dx_norm = dx / length
    dy_norm = dy / length
    
    # Draw dashes
    dash_length = 5
    gap_length = 3
    current_length = 0
    
    while current_length < length:
        # Start of dash
        start_x = x1 + dx_norm * current_length
        start_y = y1 + dy_norm * current_length
        
        # End of dash
        end_length = min(current_length + dash_length, length)
        end_x = x1 + dx_norm * end_length
        end_y = y1 + dy_norm * end_length
        
        draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=width)
        current_length += dash_length + gap_length

def draw_arrow_head(draw, start_x, start_y, end_x, end_y, color, width):
    """Draw an arrow head at the end point"""
    import math
    
    # Calculate arrow direction
    dx = end_x - start_x
    dy = end_y - start_y
    length = math.sqrt(dx*dx + dy*dy)
    
    if length == 0:
        return
    
    # Normalize direction
    dx_norm = dx / length
    dy_norm = dy / length
    
    # Arrow dimensions
    arrow_length = 10
    arrow_width = 6
    
    # Calculate arrow points
    back_x = end_x - dx_norm * arrow_length
    back_y = end_y - dy_norm * arrow_length
    
    # Perpendicular direction for arrow width
    perp_x = -dy_norm * arrow_width
    perp_y = dx_norm * arrow_width
    
    # Arrow head points
    point1 = (back_x + perp_x, back_y + perp_y)
    point2 = (end_x, end_y)
    point3 = (back_x - perp_x, back_y - perp_y)
    
    draw.polygon([point1, point2, point3], fill=color, outline=color)

def draw_diamond(draw, end_x, end_y, start_x, start_y, color, width, filled=False):
    """Draw a diamond shape at the end point"""
    import math
    
    # Calculate direction
    dx = end_x - start_x
    dy = end_y - start_y
    length = math.sqrt(dx*dx + dy*dy)
    
    if length == 0:
        return
    
    # Normalize direction
    dx_norm = dx / length
    dy_norm = dy / length
    
    # Diamond dimensions
    diamond_length = 12
    diamond_width = 8
    
    # Calculate diamond points
    tip_x = end_x
    tip_y = end_y
    
    back_x = end_x - dx_norm * diamond_length
    back_y = end_y - dy_norm * diamond_length
    
    # Perpendicular direction for diamond width
    perp_x = -dy_norm * diamond_width
    perp_y = dx_norm * diamond_width
    
    # Diamond points
    points = [
        (tip_x, tip_y),
        (back_x + perp_x/2, back_y + perp_y/2),
        (back_x - dx_norm * diamond_length/2, back_y - dy_norm * diamond_length/2),
        (back_x - perp_x/2, back_y - perp_y/2)
    ]
    
    if filled:
        draw.polygon(points, fill=color, outline=color)
    else:
        draw.polygon(points, fill='white', outline=color, width=width)

def draw_triangle(draw, start_x, start_y, end_x, end_y, color, width, filled=False):
    """Draw a triangle at the end point (for inheritance)"""
    import math
    
    # Calculate direction
    dx = end_x - start_x
    dy = end_y - start_y
    length = math.sqrt(dx*dx + dy*dy)
    
    if length == 0:
        return
    
    # Normalize direction
    dx_norm = dx / length  
    dy_norm = dy / length
    
    # Triangle dimensions
    triangle_length = 12
    triangle_width = 10
    
    # Calculate triangle points
    tip_x = end_x
    tip_y = end_y
    
    back_x = end_x - dx_norm * triangle_length
    back_y = end_y - dy_norm * triangle_length
    
    # Perpendicular direction for triangle width
    perp_x = -dy_norm * triangle_width
    perp_y = dx_norm * triangle_width
    
    # Triangle points
    points = [
        (tip_x, tip_y),
        (back_x + perp_x/2, back_y + perp_y/2),
        (back_x - perp_x/2, back_y - perp_y/2)
    ]
    
    if filled:
        draw.polygon(points, fill=color, outline=color)
    else:
        draw.polygon(points, fill='white', outline=color, width=width)

# Global list to track existing notes for collision detection
_existing_notes = []

def clear_notes():
    """Clear the list of existing notes (call at start of new diagram)"""
    global _existing_notes
    _existing_notes = []

def note(image, note_text, class_position, class_size, font, font_size=10, 
         note_position='right', offset=20, note_color='yellow', text_color='black', 
         border_color='black', border_width=1, avoid_collisions=True):
    """
    Add a note next to a class box with smart positioning to avoid text blocking and collisions
    
    Args:
        image: PIL Image to draw on
        note_text: Text content of the note
        class_position: (x, y) position of the class box
        class_size: (width, height) size of the class box
        font: Font to use for note text
        font_size: Size of the font
        note_position: Position relative to class ('right', 'left', 'top', 'bottom', 'auto')
        offset: Distance from class box in pixels
        note_color: Background color of the note
        text_color: Color of the note text
        border_color: Color of the note border
        border_width: Width of the note border
        avoid_collisions: Whether to avoid collisions with existing notes
    
    Returns:
        (note_x, note_y, note_width, note_height): Position and size of the created note
    """
    global _existing_notes
    draw = ImageDraw.Draw(image)
    
    class_x, class_y = class_position
    class_width, class_height = class_size
    
    # Calculate note dimensions
    note_lines = note_text.split('\n')
    max_line_width = 0
    total_height = 0
    line_heights = []
    
    for line in note_lines:
        if line.strip():  # Only measure non-empty lines
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
        else:
            line_width = 0
            line_height = font_size  # Use font size for empty lines
        
        max_line_width = max(max_line_width, line_width)
        line_heights.append(line_height)
        total_height += line_height
    
    # Add padding to note
    note_padding = 8
    note_width = max_line_width + (note_padding * 2)
    note_height = total_height + (note_padding * 2)
    
    def check_collision(x, y, width, height):
        """Check if a note at given position would collide with existing notes"""
        if not avoid_collisions:
            return False
        
        for existing in _existing_notes:
            ex_x, ex_y, ex_w, ex_h = existing
            # Check rectangle overlap
            if (x < ex_x + ex_w and x + width > ex_x and 
                y < ex_y + ex_h and y + height > ex_y):
                return True
        return False
    
    def find_best_position():
        """Find the best position that avoids collisions"""
        positions_to_try = []
        
        if note_position == 'auto':
            # Try all positions in order of preference
            positions_to_try = ['right', 'left', 'bottom', 'top']
        else:
            # Try the requested position first, then alternatives
            positions_to_try = [note_position, 'right', 'left', 'bottom', 'top']
            # Remove duplicates while preserving order
            seen = set()
            positions_to_try = [x for x in positions_to_try if not (x in seen or seen.add(x))]
        
        for pos in positions_to_try:
            # Calculate position for this orientation
            if pos == 'right':
                test_x = class_x + class_width + offset
                test_y = class_y + (class_height - note_height) // 2
            elif pos == 'left':
                test_x = class_x - offset - note_width
                test_y = class_y + (class_height - note_height) // 2
            elif pos == 'top':
                test_x = class_x + (class_width - note_width) // 2
                test_y = class_y - offset - note_height
            elif pos == 'bottom':
                test_x = class_x + (class_width - note_width) // 2
                test_y = class_y + class_height + offset
            else:
                continue
            
            # Check if position is within image bounds
            if (test_x >= 0 and test_y >= 0 and 
                test_x + note_width <= image.width and 
                test_y + note_height <= image.height):
                
                # Check for collisions
                if not check_collision(test_x, test_y, note_width, note_height):
                    return test_x, test_y, pos
                
                # Try with small offsets to avoid collision
                for y_offset in [0, 20, -20, 40, -40]:
                    adjusted_y = test_y + y_offset
                    if (adjusted_y >= 0 and adjusted_y + note_height <= image.height and
                        not check_collision(test_x, adjusted_y, note_width, note_height)):
                        return test_x, adjusted_y, pos
        
        # If no collision-free position found, use default right position
        note_x = class_x + class_width + offset
        note_y = class_y + (class_height - note_height) // 2
        return note_x, note_y, 'right'
    
    # Find best position
    note_x, note_y, final_position = find_best_position()
    
    # Record this note's position for future collision detection
    if avoid_collisions:
        _existing_notes.append((note_x, note_y, note_width, note_height))
    
    # Draw note background
    note_rect = [
        (note_x, note_y),
        (note_x + note_width, note_y + note_height)
    ]
    draw.rectangle(note_rect, fill=note_color, outline=border_color, width=border_width)
    
    # Draw note text
    text_y = note_y + note_padding
    for i, line in enumerate(note_lines):
        if line.strip():  # Only draw non-empty lines
            text_x = note_x + note_padding
            draw.text((text_x, text_y), line, fill=text_color, font=font)
        text_y += line_heights[i]
    
    # Draw connection line from note to class
    draw_note_connection(draw, class_position, class_size, (note_x, note_y), (note_width, note_height), final_position)
    
    return (note_x, note_y, note_width, note_height)

def draw_note_connection(draw, class_pos, class_size, note_pos, note_size, position):
    """Draw a dashed line connecting the note to the class"""
    class_x, class_y = class_pos
    class_width, class_height = class_size
    note_x, note_y = note_pos
    note_width, note_height = note_size
    
    # Calculate connection points
    if position == 'right':
        # From right edge of class to left edge of note
        start_x = class_x + class_width
        start_y = class_y + class_height // 2
        end_x = note_x
        end_y = note_y + note_height // 2
    elif position == 'left':
        # From left edge of class to right edge of note
        start_x = class_x
        start_y = class_y + class_height // 2
        end_x = note_x + note_width
        end_y = note_y + note_height // 2
    elif position == 'top':
        # From top edge of class to bottom edge of note
        start_x = class_x + class_width // 2
        start_y = class_y
        end_x = note_x + note_width // 2
        end_y = note_y + note_height
    elif position == 'bottom':
        # From bottom edge of class to top edge of note
        start_x = class_x + class_width // 2
        start_y = class_y + class_height
        end_x = note_x + note_width // 2
        end_y = note_y
    else:
        return  # No connection for unknown positions
    
    # Draw dashed line
    draw_dashed_line(draw, start_x, start_y, end_x, end_y, 'gray', 1)

def draw_diagram(data, filename='diagram.png'):
    pass

