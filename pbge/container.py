#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       
#       Copyright 2012 Anne Archibald <peridot.faceted@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
# 

class ContainerError(ValueError):
    """Error signaling something went wrong with container handling"""
    pass

class Container(object):
    """A container is an object that manages objects it contains.

    The objects in a container each have a .container attribute that
    points to the container. This attribute is managed by the container
    itself. 

    This class is a base class that provides common container functionality,
    to be used to simplify implementation of list and dict containers.
    """
    def _set_container(self, item):
        if hasattr( item, "container" ) and item.container not in (None,self):
#            raise ContainerError("Item %s was added to container %s but was already in container %s" % (item, self, item.container))
            item.container.remove( item )
        item.container = self
    def _unset_container(self, item):
        if item.container is not self:
            raise ContainerError("Item %s was removed from container %s but was not in it" % (item, self))
        item.container = None
    def _set_container_multi(self, items):
        """Put items in the container in an all-or-nothing way"""
        r = []
        try:
            for i in items:
                self._set_container(i)
                r.append(i)
            r = None
        finally: # Make sure items don't get added to this if any fail
            if r is not None:
                for i in r:
                    try:
                        self._unset_container(i)
                    except ContainerError:
                        pass
    def _unset_container_multi(self, items):
        """Remove items from the container in an all-or-nothing way"""
        r = []
        try:
            for i in items:
                self._unset_container(i)
                r.append(i)
            r = None
        finally: 
            if r is not None:
                for i in r:
                    try:
                        self._set_container(i)
                    except ContainerError:
                        pass


class ContainerList(list,Container):
    """A ContainerList is a list whose children know they're in it.

    Each element in the ContainerList has a .container attribute which points
    to the ContainerList itself. This container pointer is maintained automatically.
    """
    def __init__(self, items=[], owner=None):
        list.__init__(self, items)
        self._set_container_multi(items)
        self.owner = owner

    def __repr__(self):
        return "<CL %s>" % list.__repr__(self)


    def append(self, item):
        self._set_container(item)
        list.append(self,item)
    def extend(self, items):
        self._set_container_multi(items)
        list.extend(self,items)
    def insert(self, i, item):
        self._set_container(item)
        list.insert(self,i,item)
    def remove(self, item):
        self._unset_container(item)
        list.remove(self,item)
    def pop(self, i=-1):
        self._unset_container(self[i])
        return list.pop(self,i)

    # These don't work because they make the elements part of more than one list, or one list more than once
    def __add__(self, other):
        raise NotImplementedError
    def __radd__(self, other):
        raise NotImplementedError
    def __imul__(self,other):
        raise NotImplementedError
    def __mul__(self, other):
        raise NotImplementedError
    def __rmul__(self,other):
        raise NotImplementedError

    # only works if other is not also a Container
    def __iadd__(self, other):
        self.extend(other)
        return self

    def __setitem__(self, key, value):
        # FIXME: check slices work okay
        if isinstance(key, slice):
            self._unset_container_multi(self[key])
            try:
                self._set_container_multi(value)
            except ContainerError:
                self._set_container_multi(self[key])
                raise
        else:
            self._unset_container(self[key])
            try:
                self._set_container(value)
            except ContainerError:
                self._set_container(self[key])
                raise
        list.__setitem__(self,key,value)
    def __delitem__(self, key):
        # FIXME: check slices work okay
        if isinstance(key, slice):
            self._unset_container_multi(self[key])
        else:
            self._unset_container(self[key])
        list.__delitem__(self,key)
    # Needed for python2, forbidden for python3
    def __delslice__(self,i,j):
        del self[slice(i,j,None)]

class ContainerDict(dict,Container):
    """A ContainerDict is a dict whose children know they're in it.

    Each element in the ContainerDict has a .container attribute which points
    to the ContainerDict itself. This container pointer is maintained automatically.
    """
    def __init__(self, contents=None, **kwargs):
        if contents is None:
            dict.__init__(self, **kwargs)
        else:
            dict.__init__(self, contents, **kwargs)
        self._set_container_multi(self.values())

    def __repr__(self):
        return "<CD %s>" % dict.__repr__(self)

    def __setitem__(self, key, value):
        if key in self:
            self._unset_container(self[key])
        try:
            self._set_container(value)
        except ContainerError:
            if key in self:
                self._set_container(self[key])
            raise
        dict.__setitem__(self,key,value)
    def __delitem__(self, key):
        if key in self:
            self._unset_container(self[key])
        dict.__delitem__(self,key)
    def pop(self, key):
        if key in self:
            self._unset_container(self[key])
        return dict.pop(self,key)
    def popitem(self):
        key, value = dict.popitem(self)
        self._unset_container(value)
        return key, value
    def setdefault(self, key, default=None):
        if key not in self:
            self._set_container(default)
        dict.setdefault(self, key, default)
    def update(self, other):
        for (k,v) in other.items():
            self[k] = v

if __name__=='__main__':

    class Gear(object):
        def __init__(self, name, container=None):
            self.name = name
            self.container = container

        def __repr__(self):
            return "<G "+str(self.name)+">"



    gears = [Gear(n) for n in range(10)]
    a = Gear("A")
    b = Gear("B")
    c = Gear("C")
    d = Gear("D")
    e = Gear("E")

    p = ContainerList([a,b,c])

    print p

    try:
        p.append(a)
    except ContainerError, err:
        print err
    else:
        raise AssertionError

    print p[1]
    print p[::2]
    p[1] = d
    print p

    p[1] = b
    p[::2] = [d,e]
    print p

    del p[:]

    p2 = ContainerList([a,b,c])
    print p2

    p2.extend([d,e])
    print p2
    
    print p2.pop()
    print p2

    p2.remove(d)
    print p2

    p2 += [d,e]
    print p2    

    try:
        d = ContainerDict(a=a, b=b, c=c)
    except ContainerError, err:
        print err
    else:
        raise AssertionError
    del p2[:]

    d = ContainerDict(a=a, b=b, c=c)

    print d
    print d["a"]
    d["a"] = a
    try:
        d["a"] = b
    except ContainerError, err:
        print err
    else:
        raise AssertionError
    del d["a"]
    d["a"] = a
    d.pop("a")
    print d
    d["a"] = a
    k,v = d.popitem()
    d[k] = v

    d.setdefault("e",e)
    d.setdefault("e",e)
    print d

    del d["e"]
    d.update(dict(e=e))
    print d
