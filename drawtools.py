#!/usr/bin/python

import re,os,sys
import numpy as np, matplotlib.pyplot as plot

class point(object):
    def __init__(self, loc):
        self.loc = loc
        self.x, self.y = loc

class line(object):
    def __init__(self, loc1, loc2):
        self.locs = np.array([ loc1, loc2 ])
        self.xs, self.ys = self.locs.T[0], self.locs.T[1]

    def draw(self, ax, color='r', lw=2.0):
        ax.plot(self.xs, self.ys, color=color, lw=lw)

CROSSHAIRMODE = { 'all'         : [ 0, 1, 2, 3 ],
                  'topleft'     : [ 0, 3 ],
                  'topright'    : [ 1, 3 ],
                  'bottomleft'  : [ 0, 2 ],
                  'bottomright' : [ 1, 2 ] }
class cross(object):
    def __init__(self, ctr, len, sep=0, mode='all'):
        sht = len + sep
        lines = [ line([ctr[0] - sep, ctr[1]], [ctr[0] - sht, ctr[1]]),
                  line([ctr[0] + sep, ctr[1]], [ctr[0] + sht, ctr[1]]),
                  line([ctr[0], ctr[1] - sep], [ctr[0], ctr[1] - sht]),
                  line([ctr[0], ctr[1] + sep], [ctr[0], ctr[1] + sht]) ]
        self.lines = [lines[i] for i in CROSSHAIRMODE[mode]]

    def draw(self, ax, **kwargs):
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        for l in self.lines:
            l.draw(ax, **kwargs)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

class circle(object):
    def __init__(self, loc, size):
        self.loc, self.r = loc, size

    kw = { 'marker': 'o', 'mfc': 'None', 'mew': 1.3 }
    def draw(self, ax, color='r'):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.plot(*self.loc, ms=self.r, mec=color, **self.kw)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
