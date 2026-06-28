import sdl2
from sdl2 import sdlttf
from . import TEXT_COLOR, util, ttfhelper

ALIGN_LEFT = "left"
ALIGN_RIGHT = "right"
ALIGN_CENTER = "center"

FK_DISPLAY = "FK_DISPLAY"
FK_TEXT = "FK_TEXT"
FK_BOLD = "FK_BOLD"
FK_ITALIC = "FK_ITALIC"

TEXT_COLOR = sdl2.SDL_Color(240, 240, 50)
INFO_GREEN = sdl2.SDL_Color(50, 200, 0)
INFO_HILIGHT = sdl2.SDL_Color(100, 250, 0)

WHITE = sdl2.SDL_Color(255, 255, 255)
GREY = sdl2.SDL_Color(155, 155, 155)



ALL_FONTS = dict()


class FontStyle:
    def __init__(self, style_name, font_key, size, color):
        self.style_name = style_name
        self.font_key = font_key
        self.size = size
        self.color = color
        self.needs_initialization = True

    def render_text(self, text, width, line_h=None, align=ALIGN_LEFT, color=None):
        """
        Return an SDL_Surface object with the given text rendered in this style.
        If no line_h is provided, use the default. Same goes for color.
        """
        fontob: ttfhelper.PBGEFont = self._get_fontob()
        return fontob.render_text(text, self.style_name, width=width, line_h=line_h, align=align, color=color)

    def linesize(self, text):
        """Return the size of this text without line splitting."""
        fontob: ttfhelper.PBGEFont = self._get_fontob()
        return fontob.get_line_size(text, self.style_name)

    def wrapline(self, text, width):
        """Return a list of strings split to fit within width."""
        fontob: ttfhelper.PBGEFont = self._get_fontob()
        return fontob.split_lines(text, self.style_name, width=width)

    def textsize(self, text, width):
        """Return the w,h of this block of text."""
        fontob: ttfhelper.PBGEFont = self._get_fontob()
        lines = fontob.split_lines(text, self.style_name, width=width)
        return width, fontob.get_lines_height(lines, self.style_name)

    def textheight(self, text, width):
        """Return the w,h of this block of text."""
        fontob: ttfhelper.PBGEFont = self._get_fontob()
        lines = fontob.split_lines(text, self.style_name, width=width)
        return fontob.get_lines_height(lines, self.style_name)

    def get_font_spacing(self):
        fontob: ttfhelper.PBGEFont = self._get_fontob()
        return fontob.get_font_spacing(self.style_name)

    def _get_fontob(self) -> ttfhelper.PBGEFont:
        fontob: ttfhelper.PBGEFont = ALL_FONTS[self.font_key]
        if self.needs_initialization:
            self._initialize(fontob)
        return fontob

    def _initialize(self, fontob: ttfhelper.PBGEFont):
        fontob.add_style(self.style_name, self.size, self.color)
        self.needs_initialization = False


SMALLFONT = FontStyle("PBGE_SmallFont", FK_TEXT, 12, INFO_GREEN)
TINYFONT = FontStyle("PBGE_TinyFont", FK_TEXT, 10, INFO_GREEN)
ITALICFONT = FontStyle("PBGE_ItalicFont", FK_ITALIC, 12, INFO_GREEN)
MEDIUM_DISPLAY_FONT = FontStyle("PBGE_DisplayFont", FK_DISPLAY, 14, INFO_HILIGHT)
BIGFONT = FontStyle("PBGE_DisplayFont", FK_DISPLAY, 17, INFO_HILIGHT)
HUGEFONT = FontStyle("PBGE_DisplayFont", FK_DISPLAY, 24, WHITE)
ANIMFONT = FontStyle("PBGE_AnimFont", FK_BOLD, 16, WHITE)
MEDIUMFONT = FontStyle("PBGE_MediumFont", FK_TEXT, 14, TEXT_COLOR)
ALTTEXTFONT = FontStyle("PBGE_AltTextFont", FK_ITALIC, 14, TEXT_COLOR)  # Use this instead of MEDIUMFONT when you want to shake things up a bit.


def init_fonts(display_font, text_font, bold_font, italic_font):
    sdlttf.TTF_Init()
    ALL_FONTS[FK_DISPLAY] = ttfhelper.PBGEFont(util.image_dir(display_font), 14, TEXT_COLOR)
    ALL_FONTS[FK_TEXT] = ttfhelper.PBGEFont(util.image_dir(text_font), 14, TEXT_COLOR)
    ALL_FONTS[FK_BOLD] = ttfhelper.PBGEFont(util.image_dir(bold_font), 14, TEXT_COLOR, styleflags=sdlttf.TTF_STYLE_BOLD)
    ALL_FONTS[FK_ITALIC] = ttfhelper.PBGEFont(util.image_dir(italic_font), 14, TEXT_COLOR, styleflags=sdlttf.TTF_STYLE_ITALIC)


def quit():
    sdlttf.TTF_Quit()

