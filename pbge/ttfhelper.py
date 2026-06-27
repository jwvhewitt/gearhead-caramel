import os
import re
from ctypes import c_int, byref
from sdl2 import surface, pixels, rwops, rect, ext
from sdl2.ext.compat import byteify, stringify, utf8, _is_text
from sdl2.ext.err import raise_sdl_err
from sdl2.ext.color import Color, convert_to_color
from sdl2.ext.draw import prepare_color
from sdl2.ext.resources import _validate_path
from sdl2.ext.surface import _create_surface
import sdl2

# The PySDL2 ext.ttf unit, released as public domain software, now
# being modified by me since there are some things I want to change.

# If we don't have sdlttf, just crash.
from sdl2 import sdlttf

__all__ = ["PBGEFont"]


# This module variable keeps track of the number of separate times SDL_ttf has
# been initialized. This is important to keep track of, since de-initializing
# the library frees all associated font data, so we want to make sure this
# hasn't changed during the lifetime of an object to avoid segfaults.
_ttf_init_count = 0




def _is_whitespace(s):
    ws_chars = [" ", "\n", "\t", "\r"]
    return len(s) == 0 or all([c in ws_chars for c in s])


def _split_on_whitespace(line):
    # Splits a string on whitespace starts without removing the whitespace
    words = []
    current_word = ""
    for s in re.split(r'(\s+)', line):
        current_word += s
        if not _is_whitespace(s):
            words.append(current_word)
            current_word = ""
    return words


class PBGEFont(object):
    """A class for rendering text with a given TrueType font.

    Modified from the PySDL2 version for Polar Bear Game Engine.

    This class loads a TrueType or OpenType font using the **SDL_ttf** library
    and allows the user to render text with it in various sizes and colors.

    To simplify rendering text with different font sizes and colors, this class
    allows users to define font styles (e.g. 'instructions', 'error', 'title',
    etc.) using :meth:`add_style`, which can then be used by name with the
    :meth:`render_text` method.

    By default, the :class:`FontTTF` class defines font sizes in points (pt), a
    common unit of font size used by many libraries and text editors. However,
    you can also define font sizes in units of *pixel height* (px), i.e. the
    ascent height of the font's tallest alphanumeric ASCII character. This is
    done by calculating each font's px-to-pt scaling factor on import, meaning
    that some rounding error may occur. If using a font that does not include
    all alphanumeric ASCII characters (A-Z, a-z, 0-9) or wanting to scale the
    maximum pixel height to a different subset of characters (e.g. just 0-9
    digits), you will need to specifiy a custom 'height_chars' string when
    creating the font object.

    .. note::
       If loading a font from an SDL RWops file object, you must not free the
       file object until you are done with the font. Otherwise, SDL_ttf will
       try to render with a closed font and hard-crash Python. 
    
    Args:
        font (str or :obj:`SDL_RWops`): The relative (or absolute) path to the
            font to load, or an SDL file object containing the font data.
        size (int or str): The default size for the font, either as an integer
            (assumed to be in pt) or as a string specifying the unit of size
            (e.g. '12pt' or '22px').
        color (~sdl2.ext.Color or tuple): The default color to use for
            rendering text. Defaults to white if not specified.
        index (int, optional): The index of the font face to load if the font
            file contains multiple faces. Defaults to 0 (first face in the file)
            if not specified.
        height_chars (str, optional): The set of font characters to use for
            calculating the maximum height (in pixels) of the font for 
    
    """
    def __init__(self, font, size, color, index=0, height_chars=None, styleflags=0):
        # Load the font, either from a file or an SDL file object
        if isinstance(font, rwops.SDL_RWops):
            fname = None
            self._font_file = None
            self._font_rw = font
        elif _is_text(font):
            fullpath, fname = _validate_path(font, "a font")
            fullpath = byteify(fullpath)
            self._font_file = open(fullpath, "rb")
            self._font_rw = rwops.rw_from_object(self._font_file)
        else:
            e = "'font' must be a path string or an SDL file object (got {0})."
            raise ValueError(e.format(type(font).__str__))
    
        # Initialize the TTF library (if not already initialized)
        self._ttf_init_count = ext.ttf._ttf_init()  # pyright: ignore[reportPrivateUsage]
        self._index = index
        self.styleflags = styleflags

        # Get the px-to-pt scaling factor for the font
        if not height_chars:
            caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            height_chars = caps + caps.lower() + "0123456789"
        self._scale_factor = self._get_scale_factor(height_chars, fname)

        # Initialize font styles and add the default style    
        self._styles = {}
        self.add_style("default", size, color)

    def _check_if_closed(self):
        # Makes sure the font hasn't been closed, raising an exception if it has
        ttf_was_closed = _ttf_init_count > self._ttf_init_count
        if self._font_rw == None:
            e = "The font has been closed and can no longer be used."
            raise RuntimeError(e)
        elif sdlttf.TTF_WasInit() < 1 or ttf_was_closed:
            e = "The SDL_ttf library has been de-initialized since creating the "
            e += "font. The font can no longer be used."
            raise RuntimeError(e)

    def _get_scale_factor(self, testchars, fname):
        # Calculate the pt -> px conversion factor for the current font.
        tmpsize = 40  # Font size in pt at which to calculate pt -> px scale factor
        max_ascent = 0
        minX, maxX, minY, maxY = c_int(0), c_int(0), c_int(0), c_int(0)
        advance = c_int(0)
        tmpfont = sdlttf.TTF_OpenFontIndexRW(self._font_rw, 0, tmpsize, self._index)
        if not tmpfont:
            e = "initializing the font"
            if fname:
                e += " '{0}'".format(fname)
            raise_sdl_err(e)
        for char in testchars:
            if sdlttf.TTF_GlyphIsProvided(tmpfont, ord(char)) == 0:
                e = "The current font does not provide a glyph for character "
                e += "'{0}'. Please initialize the font with a different "
                e += "'height_chars' string."
                sdlttf.TTF_CloseFont(tmpfont)
                raise RuntimeError(e.format(char.encode('utf-8')))
            sdlttf.TTF_GlyphMetrics(
                tmpfont, ord(char), byref(minX), byref(maxX),
                byref(minY), byref(maxY), byref(advance)
            )
            if maxY.value > max_ascent:
                max_ascent = maxY.value
        sdlttf.TTF_CloseFont(tmpfont)
        return tmpsize / float(max_ascent)

    def _parse_size(self, size):
        # Parse and validate a font size, which can be an int or a string
        if isinstance(size, str):
            if '-' in size or '.' in size:
                e = "Font size must be a positive whole number (got '{0}')."
                raise ValueError(e.format(size))
            sz = "".join([i for i in size if i.isdigit()])
            unit = size[len(sz):]
            sz = int(sz)
            if unit == "px":
                sz = int(sz * self._scale_factor)
            elif unit not in ["pt", "px"]:
                e = "Font size units must be either 'pt' or 'px' (got '{0}')."
                raise ValueError(e.format(unit))
        else:
            sz = int(size)
        return sz

    def _parse_line_height(self, height, default_skip):
        if height is None:
            h = default_skip
        elif isinstance(height, str):
            # If line height specified as a percentage of the default line skip
            if height[-1] == "%":
                pct = float(height[:-1])
                if not pct > 0:
                    e = "Relative line heights must be greater than 0% (got '{0}')."
                    raise ValueError(e.format(height))
                h = int(default_skip * (pct / 100.0))
            # If line height specified explicitly in pixels
            elif height[-2:] == "px":
                if '-' in height or '.' in height:
                    e = "Line height must be a positive whole number (got '{0}')."
                    raise ValueError(e.format(height))
                h = int("".join([i for i in height if i.isdigit()]))
            else:
                e = "Line height units must be either 'px' or '%' (got '{0}')."
                raise ValueError(e.format(height))
        else:
            # If numeric, assume pixels
            if height != int(height) or height < 1:
                e = "Line height must be a positive integer (got {0})."
                raise ValueError(e.format(height))
            h = int(height)
        return max(h, 1)

    def get_line_size(self, line, style):
        # Get the height and width of a given line of text in a given style
        # This method has also been made public because I am full of hubris and
        # believe the lack of error checking won't possibly come back to bite
        # me in the arse. See the note below about split_lines for more info.
        font = self._styles[style]['font']
        if len(line) == 0:
            return (0, sdlttf.TTF_FontHeight(font))
        lw, lh = c_int(0), c_int(0)
        ret = sdlttf.TTF_SizeUTF8(font, byteify(line), byref(lw), byref(lh))
        if ret != 0:
            raise_sdl_err("rendering text with the '{0}' style".format(style))
        return (lw.value, lh.value)

    def _wrap_line(self, line, style, line_width, width):
        # Splits a single line of text into separate lines in order to fit
        # within a given width with a given text style
        lines = []
        while line_width > width:

            # First, estimate the position of the wrap word and move to the
            # end of it
            pos = int((width / float(line_width)) * len(line))
            words = _split_on_whitespace(line)
            for i in range(len(words)):
                split_word = i + 1
                segment = "".join(words[:split_word])
                if len(segment) >= pos and len(segment) < len(line):
                    pos = len(segment)
                    break

            # Then, work backwards until the line fits within the width
            segment_w = self.get_line_size(segment, style)[0]
            while segment_w > width:
                if split_word > 1:
                    split_word -= 1
                    segment = "".join(words[:split_word])
                    pos = len(segment)
                elif pos > 1:
                    pos -= 1
                    segment = segment[:pos]
                else:
                    e = "Character '{0}' exceeds maximum width of text"
                    raise RuntimeError(e.format(line[0]))
                segment_w = self.get_line_size(segment, style)[0]

            # Append the trimmed line & remove the text from the line, then
            # recalculate the width of the remaining text to see if it fits
            lines.append(segment)
            line = line[pos:].lstrip()
            line_width = self.get_line_size(line, style)[0]

        lines.append(line)
        return lines

    def split_lines(self, text, style, width=None):
        # Splits one or more lines of text to ensure they all fit within a given
        # width (in pixels) when rendered with a given text style
        # I have changed this method from private to public, as I need a line
        # splitter for widgets and other assorted stuff. AFAICT the reason it
        # was private is that it doesn't do error checking- if you request a style
        # that doesn't exist, you get an unhandled exception. Well maybe I want
        # unhandled exceptions, have you considered that?! Seriously, though,
        # given the way fonts are organized in GHC I don't expect this to be a
        # problem.
        unwrapped_lines = text.split("\n")
        if width is None:
            return unwrapped_lines

        lines = []
        for line in unwrapped_lines:
            lw = self.get_line_size(line, style)[0]
            if lw > width:
                # If line is too long and contains trailing whitespace, try w/o
                if len(line) < len(line.rstrip()):
                    line = line.rstrip()
                    lw = self.get_line_size(line, style)[0]
                # If line width exceeds wrap width, we break it into smaller lines
                lines += self._wrap_line(line, style, lw, width)
            else:
                lines.append(line)

        return lines

    def get_font_spacing(self, style):
        """Return the default line spacing in pixels."""
        font = self._styles[style]['font']
        return sdlttf.TTF_FontLineSkip(font)

    def get_lines_height(self, lines, style, line_h=None):
        """Return the height of this set of lines."""
        font = self._styles[style]['font']
        font_height = sdlttf.TTF_FontHeight(font)
        default_skip = sdlttf.TTF_FontLineSkip(font)
        line_h = self._parse_line_height(line_h, default_skip)
        return line_h * (len(lines) - 1) + font_height

    def _render_lines(self, lines, style, line_h, width, align, color=None):
        # Renders one or more lines of text to an SDL surface, optionally with
        # a custom line height, wrap width, and/or text alignment
        font = self._styles[style]['font']
        color = color or self._styles[style]['color']
        bg_col = self._styles[style]['bg']
        if not bg_col:
            c = color
            bg_col = (c.r, c.g, c.b, 0)  # Default bg = font color w/ full transparency

        # Actually render the text
        rendered = []
        for line in lines:
            if len(line) == 0:
                rendered.append(None)
                continue
            fontsf = sdlttf.TTF_RenderUTF8_Blended(font, byteify(line), color)
            if not fontsf:
                raise_sdl_err("rendering text with the '{0}' style".format(style))
            rendered.append(fontsf)

        # If single line of text w/ no background fill or custom width, return as-is
        if len(rendered) == 1 and width == None and bg_col is None:
            return rendered[0]

        # Determine height and width of background surface
        font_height = sdlttf.TTF_FontHeight(font)
        default_skip = sdlttf.TTF_FontLineSkip(font)
        line_h = self._parse_line_height(line_h, default_skip)
        height = line_h * (len(lines) - 1) + font_height
        if width == None:
            width = max([line.contents.w for line in rendered if line])

        # Create background surface for the text and render lines to it
        sf = _create_surface((width, height), bg_col, errname="background")
        line_y = 0
        for line in rendered:
            if line:
                lw, lh = (line.contents.w, line.contents.h)
                if align == "left":
                    line_x = 0
                elif align == "center":
                    line_x = int((width - lw) / 2)
                elif align == "right":
                    line_x = width - lw
                line_rect = rect.SDL_Rect(line_x, line_y, lw, lh)
                surface.SDL_BlitSurface(line, None, sf, line_rect)
                surface.SDL_FreeSurface(line)
            line_y += line_h

        return sf

    def get_ttf_font(self, style='default'):
        """Returns the base :obj:`~sdl2.sdlttf.TTF_Font` for a given font style.

        This method provides access to the base ctypes object for each font
        style so that they can be used with the full set of :mod:`~sdl2.sdlttf`
        functions.

        Args:
            style (str, optional): The font style for which the base ctypes font
                object will be retrieved. Defaults to the 'default' style if not
                specified.

        Returns:
            :obj:`~sdl2.sdlttf.TTF_Font`: The base ctypes font for the style.

        """
        self._check_if_closed()
        if style not in self._styles.keys():
            e = "The '{0}' style is not defined for the current font."
            raise ValueError(e.format(style))
        return self._styles[style]['font'].contents

    def add_style(self, name, size, color, bg_color=None):
        """Defines a named font style for the current font.

        Currently, a font style defines a font size, color, and background color
        combination to use for rendering text. Additional style attributes may
        be added in future releases.

        Args:
            name (str): The name of the new font style (e.g. 'title').
            size (int or str): The font size for the style, either as an integer
                (assumed to be in pt) or as a string specifying the unit of size
                (e.g. '12pt' or '22px').
            color (~sdl2.ext.Color): The font color for the style.
            bg_color (~sdl2.ext.Color, optional): The background surface color
                for the style. Defaults to a fully-transparent background if not
                specified.
    
        """
        # Preprocess and validate style values
        self._check_if_closed()
        if name in self._styles.keys():
            e = "A style named '{0}' is already defined for the current font."
            raise ValueError(e.format(name))
        size_pt = self._parse_size(size)
        if size_pt < 1:
            e = "Font size must be at least 1pt, got {0} (specified as '{1}')"
            raise ValueError(e.format(size_pt, size))
        c = convert_to_color(color)
        if bg_color is not None:
            bg_color = convert_to_color(bg_color)

        # Actually create font object for style
        rwops.SDL_RWseek(self._font_rw, 0, rwops.RW_SEEK_SET)
        font = sdlttf.TTF_OpenFontIndexRW(self._font_rw, 0, size_pt, self._index)
        if not font:
            raise_sdl_err("initializing the '{0}' font style".format(name))
        
        if self.styleflags:
            sdlttf.TTF_SetFontStyle(font, self.styleflags)

        self._styles[name] = {
            'font': font,
            'size': size_pt,
            'color': pixels.SDL_Color(c.r, c.g, c.b, c.a),
            'bg': bg_color
        }

    def render_text(self, text, style='default', line_h=None, width=None, align='left', color=None):
        """Renders a string of text to a new surface.

        If a newline character (``\\n``) is encountered in the string, it will
        be rendered as a line break in the rendered text. Additionally, if a
        surface width is specified, any lines of text that exceed the width of
        the surface will be wrapped. Multi-line text can be left-aligned
        (the default), right-aligned, or centered, and the spacing between lines
        can be modified using the `line_h` argument.

        Line heights can be specified in pixels (e.g. ``20`` or ``'20px'``) or
        as percentages of the TTF-suggested line spacing for the font (e.g.
        ``'150%'``).

        Args:
            text (str): The string of text to render to the target surface.
            style (str, optional): The font style with which to render the
                given string. Defaults to the 'default' style if not specified.
            line_h (int or str, optional): The line height to use for each
                line of the rendered text, either in pixels or as a percentage
                of the font's suggested line height. If not specified, the
                suggested line height for the font will be used.
            width (int, optional): The width (in pixels) of the output surface.
                If a line of text exceeds this value, it will be automatically
                wrapped to fit within the specified width. Defaults to ``None``.
            align (str, optional): The alignment of lines of text for multi-line
                strings. Can be 'left' (left-aligned), 'right' (right-aligned),
                or 'center' (centered). Defaults to 'left'.

        Returns:
            :obj:`~sdl2.SDL_Surface`: A 32-bit ARGB surface containing the
            rendered text.

        """
        self._check_if_closed()
        if len(text) == 0:
            raise ValueError("Cannot render an empty string.")
        if style not in self._styles.keys():
            e = "The '{0}' style is not defined for the current font."
            raise ValueError(e.format(style))
        if align not in ["left", "right", "center"]:
            e = "Text alignment mode must be 'left', 'right', or 'center'."
            raise ValueError(e)
        if color and not isinstance(color, sdl2.SDL_Color):
            color = convert_to_color(color)
            color = sdl2.SDL_Color(color.r, color.g, color.b)

        # Actually render the text
        lines = self.split_lines(utf8(text), style, width)
        sf = self._render_lines(lines, style, line_h, width, align, color)
        return sf.contents

    def close(self):
        """Cleanly closes the font and frees all associated memory.

        This method should be called when you are finished with the font to free
        the resources taken up by the font and its styles. Once this method has
        been called, the font can no longer be used.

        """
        ttf_was_closed = _ttf_init_count > self._ttf_init_count
        if self._font_rw != None:
            if sdlttf.TTF_WasInit() > 0 and not ttf_was_closed:
                for name, style in self._styles.items():
                    sdlttf.TTF_CloseFont(style['font'])
            self._styles = None
            if self._font_file:
                rwops.SDL_RWclose(self._font_rw)
            self._font_rw = None
            self._font_file = None

    def contains(self, c):
        """Checks whether a given character exists within the font.
        
        Args:
            c (str): The glpyh (i.e. character) to check for within the font.

        Returns:
            bool: ``True`` if the font contains the glpyh, otherwise ``False``.
    
        """
        self._check_if_closed()
        font = self._styles['default']['font']
        return sdlttf.TTF_GlyphIsProvided(font, ord(c)) != 0

    @property
    def family_name(self):
        """str: The family name (e.g. "Helvetica") of the loaded font.
        
        """
        self._check_if_closed()
        name = sdlttf.TTF_FontFaceFamilyName(self._styles['default']['font'])
        return stringify(name) if name else None

    @property
    def style_name(self):
        """str: The style name (e.g. "Bold") of the loaded font.
        
        """
        self._check_if_closed()
        name = sdlttf.TTF_FontFaceStyleName(self._styles['default']['font'])
        return stringify(name) if name else None

    @property
    def is_fixed_width(self):
        """bool: Whether the current font face is fixed-width (i.e. monospaced).

        If ``True``, all characters in the current font have the same width.

        """
        self._check_if_closed()
        font = self._styles['default']['font']
        return sdlttf.TTF_FontFaceIsFixedWidth(font) != 0


