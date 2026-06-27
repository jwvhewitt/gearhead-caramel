# Load one image file, use it for multiple images.

import sdl2
from sdl2 import ext
from sdl2.ext import compat
import weakref

from . import my_state, fontstyles, frects
import os.path
import glob

import pbgerecolor
from pbgerecolor import Gradient  # pyright: ignore[reportUnusedImport]

from ctypes import c_uint8

# Keep a list of already-loaded images, to save memory when multiple objects
# need to use the same image file.
pre_loaded_images = weakref.WeakValueDictionary()
search_path = list()

def glob_images(pattern):
    mylist = list()
    for p in search_path:
        myglob = glob.glob(os.path.join(p,pattern))
        for fname in myglob:
            mylist.append(os.path.basename(fname))
    mylist.sort()
    return mylist


class ProtoImage:
    # An image with no image data... just the measurements for cutting up an image.
    def __init__(self, size, frame_width=0, frame_height=0, custom_frames=None):
        self.size = size

        if frame_width == 0:
            frame_width = self.size[0]
        if frame_height == 0:
            frame_height = self.size[1]

        if frame_width > self.size[0]:
            frame_width = self.size[0]
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.custom_frames = custom_frames
        self.frames_per_row = self.size[0] // self.frame_width

    def _get_frame_area(self, frame):
        if self.custom_frames and frame < len(self.custom_frames):
            area = sdl2.SDL_Rect(self.custom_frames[frame])
        else:
            area_x = (frame % self.frames_per_row) * self.frame_width
            area_y = (frame // self.frames_per_row) * self.frame_height
            area = sdl2.SDL_Rect(area_x, area_y, self.frame_width, self.frame_height)
        return area

    def get_rect(self, frame):
        # Return a rect of the correct size for this frame.
        if self.custom_frames and frame < len(self.custom_frames):
            return frects.PyRect(0, 0, self.custom_frames[frame][2], self.custom_frames[frame][3])
        else:
            return frects.PyRect(0, 0, self.frame_width, self.frame_height)


class SurfImage(ProtoImage):
    """A wrapper for SDL surfaces. Used for editing and compositing an image before converting it into a texture."""
    def __init__(self, fname=None, frame_width=0, frame_height=0, color=None, custom_frames=None,
                 transparent=False):
        if fname:
            if not os.path.exists(fname):
                for p in search_path:
                    if os.path.exists(os.path.join(p, fname)):
                        fname = os.path.join(p, fname)
                        break

            self.bitmap: sdl2.SDL_Surface = ext.image.load_img(fname)

            if color:
                self.recolor(self.bitmap, color)
        super().__init__((self.bitmap.w, self.bitmap.h), frame_width, frame_height, custom_frames)

    @staticmethod
    def recolor(bitmap: sdl2.SDL_Surface, color_channels):
        # Uses the pbgerecolor extension module.
        data = ext.pixelaccess.pixels2d(bitmap)
        
        pbgerecolor.recolor(data, list(color_channels))
        
        sdl2.SDL_UnlockSurface(bitmap)

    def __del__(self):
        sdl2.SDL_FreeSurface(self.bitmap)


class Image(ProtoImage):
    def __init__(self, fname=None, frame_width=0, frame_height=0, color=None, custom_frames=None,
                 transparent=False, surf: sdl2.SDL_Surface|SurfImage|None=None):
        """Load image file or create an image from an existing surface"""
        if fname:
            self.texture = self.get_pre_loaded(fname, color, transparent)
            if not self.texture:
                surfer = SurfImage(fname, frame_width, frame_height, color, custom_frames, transparent)
                # Convert to texture
                self.texture = ext.renderer.Texture(my_state.screen, surfer.bitmap)

                self.record_pre_loaded(fname, color, self.texture, transparent)
                del surfer
        elif surf:
            if isinstance(surf, SurfImage):
                self.texture = ext.renderer.Texture(my_state.screen, surf.bitmap)
            else:
                self.texture = ext.renderer.Texture(my_state.screen, surf)
        else:
            raise ValueError("Image can be created from either a filename or a surface. You provided neither. This is a message to Joe, probably not you the user.")

        super().__init__(self.texture.size, frame_width, frame_height, custom_frames)

        self.fname = fname
        self.transparent = transparent
        if transparent:
            self.set_alpha(transparent)

    def set_alpha(self, alpha=155):
        alpha = int(alpha)
        if alpha <= 1:
            alpha = 155
        elif alpha > 255:
            alpha = 255
        sdl2.render.SDL_SetTextureAlphaMod(self.texture.tx, c_uint8(alpha))

    @staticmethod
    def get_pre_loaded(ident, colorset, transparent):
        return pre_loaded_images.get((ident,repr(colorset),transparent))

    @staticmethod
    def record_pre_loaded(ident, colorset, bitmap, transparent=False):
        pre_loaded_images[(ident, repr(colorset), transparent)] = bitmap

    def render(self, dest=(0, 0), frame=0, colormod: tuple[int, int, int]|None=None) -> None:
        # Render this Image onto the provided surface.
        # colormod is an r,g,b tuple for modifying the color of the render
        # Start by determining the correct sub-area of the image.
        if colormod:
            sdl2.SDL_SetTextureColorMod(self.texture.tx, *colormod)
        else:
            sdl2.SDL_SetTextureColorMod(self.texture.tx, 255, 255, 255)
        source_rect = self._get_frame_area(frame)

        if compat.isiterable(dest) and len(dest) == 2:
            dest = frects.PyRect(dest[0], dest[1], source_rect.w, source_rect.h)

        sdl2.SDL_RenderCopy(my_state.screen.renderer, self.texture.tx, source_rect, dest)

        #_=my_state.screen.copy(self.texture, dstrect=dest, srcrect=source_rect)

    def render_c(self, dest: tuple[int,int]=(0, 0), frame=0 ) -> None:
        # As above, but the dest coordinates point to the center of the image.
        source_rect = self._get_frame_area(frame)
        dest_c = self.get_rect(frame)
        dest_c.center = dest
        _=my_state.screen.copy(self.texture, dstrect=dest_c, srcrect=source_rect)

    def render_montage(self, dest, h_frames=1, v_frames=1 ) -> None:
        # Render a section of this spritesheet.
        mydest = dest.copy()
        area = sdl2.SDL_Rect(0, 0, h_frames*self.frame_width, v_frames*self.frame_height)
        mydest.area = area.w, area.h
        _=my_state.screen.copy(self.texture, dstrect=mydest, srcrect=area)

    def num_frames(self):
        if self.custom_frames:
            return len(self.custom_frames)
        else:
            frames_per_row = self.size[0] // self.frame_width
            frames_per_column = self.size[1] // self.frame_height
            return frames_per_row * frames_per_column

    def __reduce__(self):
        # Rather than trying to save the bitmap image, just save the filename.
        return Image, (self.fname, self.frame_width, self.frame_height)

    def tile(self, dest=None, frame=0, x_offset=0, y_offset=0):
        if not dest:
            dest = my_state.screen.get_rect()
        grid_w = dest.w // self.frame_width + 2
        grid_h = dest.h // self.frame_height + 2
        sdl2.SDL_RenderSetClipRect(my_state.screen.sdlrenderer, dest)
        my_rect = self.get_rect(frame)

        for x in range(-1, grid_w):
            my_rect.x = dest.x + x * self.frame_width +x_offset
            for y in range(-1, grid_h):
                my_rect.y = dest.y + y * self.frame_height +y_offset
                self.render(my_rect, frame)

        sdl2.SDL_RenderSetClipRect(my_state.screen.sdlrenderer, None)

    def copy(self,ident=None):
        nu_sprite = Image(frame_height=self.frame_height,frame_width=self.frame_width,)
        nu_sprite.bitmap = self.bitmap.copy()
        if ident:
            self.record_pre_loaded(ident, None, nu_sprite.bitmap)
        return nu_sprite

    def __del__(self):
        if self.texture not in pre_loaded_images.values():
            _=self.texture.destroy()


class TextImage(Image):
    def __init__(self, txt='?????', frame_width=128, style: fontstyles.FontStyle|None=None, color=None, align=fontstyles.ALIGN_LEFT):
        """Create an image of the provided text"""
        if not style:
            style = fontstyles.ANIMFONT

        self.txt = txt
        bitmap = style.render_text( txt, frame_width, align=align, color=color)
        super().__init__(surf=bitmap)
        sdl2.SDL_FreeSurface(bitmap)

    def __reduce__(self):
        # Rather than trying to save the bitmap image, just save the filename.
        return TextImage, (self.txt, self.frame_width, self.frame_height)


def flush_images():
    pre_loaded_images.clear()

def init_image(def_image_folder):
    search_path.append(def_image_folder)
