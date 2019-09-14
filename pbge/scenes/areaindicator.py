from pbge import image
import pbge


class AreaIndicator(object):
    def __init__(self, imagename, imagewidth=64):
        self.image = image.Image(imagename,imagewidth,imagewidth)

    def calc_edges_and_corners( self, tile_set, x, y ):
        """Return the wall border frame for this tile."""
        edges = 0
        check_nw,check_ne,check_sw,check_se=True,True,True,True
        if (x-1,y) not in tile_set:
            edges += 1
            check_nw,check_sw=False,False
        if (x,y-1) not in tile_set:
            edges += 2
            check_nw,check_ne=False,False
        if (x+1,y) not in tile_set:
            edges += 4
            check_ne,check_se=False,False
        if (x,y+1) not in tile_set:
            edges += 8
            check_sw,check_se=False,False
        corners = 16
        if check_nw and (x-1,y-1) not in tile_set:
            corners += 1
        if check_ne and (x+1,y-1) not in tile_set:
            corners += 2
        if check_se and (x+1,y+1) not in tile_set:
            corners += 4
        if check_sw and (x-1,y+1) not in tile_set:
            corners += 8

        return edges,corners


    def update(self, view, tile_set ):
        # Add overlays for all the tiles in tile_set.
        view.overlays.clear()
        for pos in tile_set:
            edges,corners = self.calc_edges_and_corners(tile_set,pos[0],pos[1])
            if edges > 0 or corners > 16:
                view.overlays[pos] = (self,(edges,corners))

    def render(self, dest, frame_tuple):
        edges,corners = frame_tuple
        offset = ((pbge.my_state.anim_phase // 5 ) % 4) * 32
        if edges > 0:
            self.image.render(dest, edges + offset)
        if corners > 16:
            self.image.render(dest, corners + offset)
