# cython: language_level=3
#  Drakkar-Software OctoBot-Channels
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
from octobot_channels.producer cimport Producer

cdef class Channel(object):
    cdef object logger

    cdef public list producers

    cdef public dict consumers

    cdef public Producer internal_producer

    cdef bint is_paused

cdef class Channels:
    @staticmethod
    cdef void set_chan(Channel chan, str name)

    @staticmethod
    cdef void del_chan(str name)