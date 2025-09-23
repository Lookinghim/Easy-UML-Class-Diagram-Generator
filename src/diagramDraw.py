from PIL import Image, ImageDraw, ImageFont

"""
Variables
"""
FONT_NAME = "arial.ttf"
FONT_SIZE = 12
FONT_SIZE_ITALIC = 12

"""
Functions for drawing
"""
def load_fonts():
    try:
        base = ImageFont.truetype(FONT_NAME, FONT_SIZE)
        italic = ImageFont.truetype(FONT_NAME, FONT_SIZE_ITALIC)
    except Exception:
        base = ImageFont.load_default()
        italic = base
    return base, italic


def drawNameBox():
    pass

def drawAttributeBox():
    pass

def drawOperationBox():
    pass

def mergeBoxes():
    pass

def drawConnection():
    pass

def draw_diagram(data, filename='diagram.png'):
    pass
