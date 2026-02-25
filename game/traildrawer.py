import pbge

def draw_trail( sprite
              , trailmarker, endcursor
              , path
              ):
    ''' Common code to draw a trail, showing where one action point
    is completely spent.
    '''
    for i in range(len(path) - 1):
        p = path[i]
        if i != 0:
            pbge.my_state.view.overlays[p] = (sprite, trailmarker)
    if endcursor:
        pbge.my_state.view.overlays[path[-1]] = (sprite, endcursor)
