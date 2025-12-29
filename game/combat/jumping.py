import gears
import pbge

def get_jump_points(camp: gears.GearHeadCampaign, mover: gears.base.Mover):
    # Return a set of points this mover can jump to.
    mypoints = set()
    jump_speed = mover.get_speed(gears.tags.Jumping)
    if jump_speed > 10:
        max_map_dist = (jump_speed + 9)//10

        for dx in range(-max_map_dist, max_map_dist+1):
            for dy in range(-max_map_dist, max_map_dist+1):
                x, y = mover.pos[0]+dx, mover.pos[1]+dy
                if not camp.scene.tile_blocks_movement(x, y, mover.mmode) and camp.scene.distance((x,y), mover.pos) <= max_map_dist and (x,y) != mover.pos:
                    mypoints.add((x,y))

        mypoints = mypoints.difference(camp.scene.get_blocked_tiles())

    return mypoints


