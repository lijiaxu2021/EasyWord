from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT

# Modern Light Blue Theme
COLOR_PRIMARY = '#2196F3'      # Material Blue 500
COLOR_PRIMARY_DARK = '#1976D2' # Material Blue 700
COLOR_ACCENT = '#64B5F6'       # Material Blue 300
COLOR_BACKGROUND = '#F5F9FC'   # Very light blue-ish grey
COLOR_SURFACE = '#FFFFFF'      # White
COLOR_TEXT_PRIMARY = '#102027' # Dark Blue Grey
COLOR_TEXT_SECONDARY = '#546E7A' # Blue Grey
COLOR_SUCCESS = '#4CAF50'
COLOR_ERROR = '#F44336'

# Layout Constants
# Flex=1 is crucial for Android layout stability
STYLE_ROOT = Pack(direction=COLUMN, flex=1, background_color=COLOR_BACKGROUND)

# Card Style - Flat with border for "modern" look (Shadows not supported well)
STYLE_CARD = Pack(
    direction=COLUMN, 
    margin=8, 
    padding=12, 
    background_color=COLOR_SURFACE, 
    flex=1
)

# Typography
STYLE_HEADING = Pack(font_size=20, font_weight='bold', color=COLOR_TEXT_PRIMARY, margin_bottom=12)
STYLE_SUBTITLE = Pack(font_size=14, color=COLOR_TEXT_SECONDARY, margin_bottom=4)

# Modern Button Styles
# Note: Toga buttons have native styling, we can only control basic colors.
# We use flex in parent containers to control size usually.
STYLE_BTN_PRIMARY = Pack(
    background_color=COLOR_PRIMARY, 
    color='white', 
    font_weight='bold',
    height=45,
    flex=1
)

STYLE_BTN_SECONDARY = Pack(
    background_color=COLOR_SURFACE, 
    color=COLOR_PRIMARY, 
    height=45,
    flex=1
)

STYLE_INPUT = Pack(
    background_color=COLOR_SURFACE,
    height=45,
    margin_bottom=10,
    flex=1
)
