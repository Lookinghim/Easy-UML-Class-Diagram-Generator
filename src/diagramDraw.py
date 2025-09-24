from PIL import Image, ImageDraw, ImageFont

"""
Variables
"""
FONT_NAME = "arial.ttf"
FONT_SIZE = 12
FONT_SIZE_ITALIC = 12

PADDING_X = 10
PADDING_Y = 5
MAX_BOX_WIDTH = 250  # Maximum width for UML boxes in pixels

OUTLINE_COLOUR = 'black'
OUTLINE_WIDTH = 1
"""
Functions for drawing
"""
def loadFonts():
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


"""
Functions for drawing UML components
"""
def drawBox(boxWidth, boxHeight, outline_colour=None, outline_width=None):
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

def drawConnection(image, xCoord, yCoord, lineXCoord, lineYCoord, lineType='solid'):
    pass

def draw_diagram(data, filename='diagram.png'):
    pass

