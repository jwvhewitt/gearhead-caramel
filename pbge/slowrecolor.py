#
# Implementation for the caramelrecolor.recolor() method.
# Uses bits taken from the caramelrecolor.c program by Sander in 't Veld.
#
# Part of the Caramel Recolor library
# developed by A Bunch of Hacks
# commissioned by Joseph Hewitt.
#
# Copyright (c) 2019 A Bunch of Hacks
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <https://www.gnu.org/licenses/>.
#
# [authors:]
# Sander in 't Veld (sander@abunchofhacks.coop)

import pygame


def generate_value(vmax, vmin, level):
    return vmin + ((vmax - vmin) * level // 215)


class Gradient(object):
    def __init__(self, name, color_range):
        self.name = name
        self.color_range = color_range

    def generate_color( self, color_level):
        # The COLOR_RANGE is a tuple of six values: r g b at highest intensity,
        # and r g b at lowest intensity.
        color_level = max(color_level - 40, 0)
        r = generate_value(self.color_range[0], self.color_range[3], color_level)
        g = generate_value(self.color_range[1], self.color_range[4], color_level)
        b = generate_value(self.color_range[2], self.color_range[5], color_level)
        return r, g, b


def recolor(surf: pygame.Surface, color_channels):
    red_channel, yellow_channel, green_channel, cyan_channel, magenta_channel = color_channels

    width, height = surf.get_size()
    pixarray = pygame.surfarray.pixels3d(surf)

    for y in range(height):
        for x in range(width):

            r = pixarray[x,y,0]
            g = pixarray[x,y,1]
            b = pixarray[x,y,2]

            if (r > 0) and (g == 0) and (b == 0):
                pixarray[x,y,0], pixarray[x,y,1], pixarray[x,y,2] = red_channel.generate_color(r)
                # par[x,y] = cls.generate_color(red_channel,c.r)
            elif (r > 0) and (g > 0) and (b == 0):
                pixarray[x,y,0], pixarray[x,y,1], pixarray[x,y,2] = yellow_channel.generate_color(r)
            elif (r > 0) and (g == 0) and (b > 0):
                pixarray[x,y,0], pixarray[x,y,1], pixarray[x,y,2] = magenta_channel.generate_color(r)
            elif (r == 0) and (g > 0) and (b == 0):
                pixarray[x,y,0], pixarray[x,y,1], pixarray[x,y,2] = green_channel.generate_color(g)
            elif (r == 0) and (g > 0) and (b > 0):
                pixarray[x,y,0], pixarray[x,y,1], pixarray[x,y,2] = cyan_channel.generate_color(g)

    del pixarray
