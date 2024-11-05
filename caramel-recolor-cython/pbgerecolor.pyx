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

# cython: language_level=3


import pygame

import numpy as np

# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# currently part of the Cython distribution).
cimport numpy as np
#np.import_array()



# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPE = np.uint32
CHANTYPE = np.uint8

# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.
ctypedef np.uint32_t DTYPE_t
ctypedef np.uint8_t CHANTYPE_t

cdef CHANTYPE_t generate_value(CHANTYPE_t vmax, CHANTYPE_t vmin, CHANTYPE_t level):
    return vmin + ((vmax - vmin) * level // 215)


cdef class Gradient(object):
    cdef (CHANTYPE_t,CHANTYPE_t,CHANTYPE_t,CHANTYPE_t,CHANTYPE_t,CHANTYPE_t) color_range
    def __init__(cls, name, (CHANTYPE_t,CHANTYPE_t,CHANTYPE_t,CHANTYPE_t,CHANTYPE_t,CHANTYPE_t) color_range):
        cls.name = name
        cls.color_range = color_range

    def generate_color( Gradient cls, int color_level):
        # The COLOR_RANGE is a tuple of six values: r g b at highest intensity,
        # and r g b at lowest intensity.
        color_level = max(color_level - 40, 0)
        cdef int r = generate_value(cls.color_range[0], cls.color_range[3], color_level)
        cdef int g = generate_value(cls.color_range[1], cls.color_range[4], color_level)
        cdef int b = generate_value(cls.color_range[2], cls.color_range[5], color_level)
        return (r << 16) | (g << 8) | b


def recolor( np.ndarray[DTYPE_t, ndim=2] par,color_channels):
    red_channel, yellow_channel, green_channel, cyan_channel, magenta_channel = color_channels

    cdef int x
    cdef int y
    cdef int height = par.shape[1]
    cdef int width = par.shape[0]
    cdef int r
    cdef int g
    cdef int b

    for y in range(height):
        for x in range(width):

            r = 0xFF & ( par[x, y] >> 16)
            g = 0xFF & ( par[x, y] >> 8)
            b = 0xFF &  par[x, y]


            if (r > 0) and (g == 0) and (b == 0):
                par[x, y] = red_channel.generate_color(r)
                # par[x,y] = cls.generate_color(red_channel,c.r)
            elif (r > 0) and (g > 0) and (b == 0):
                par[x, y] = yellow_channel.generate_color(r)
            elif (r > 0) and (g == 0) and (b > 0):
                par[x, y] = magenta_channel.generate_color(r)
            elif (r == 0) and (g > 0) and (b == 0):
                par[x, y] = green_channel.generate_color(g)
            elif (r == 0) and (g > 0) and (b > 0):
                par[x, y] = cyan_channel.generate_color(g)


