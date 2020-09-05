import pbge

def draw_trail( sprite
              , trailmarker, zero
              , scene, mover
              , mp_remaining
              , path
              ):
    ''' Common code to draw a trail, showing where one action point
    is completely spent.
    '''
    aps = 0 # Action points so far
    for i in range(len(path) - 1):
        p = path[i]
        nextp = path[i + 1]
        marker = trailmarker
        cost = scene.get_move_cost(p, nextp, mover.mmode)
        if cost > mp_remaining:
            # End of current action point.
            mp_remaining += mover.get_current_speed()
            marker = zero + aps
            aps += 1
        mp_remaining -= cost
        if i != 0:
            pbge.my_state.view.overlays[p] = (sprite, marker)
