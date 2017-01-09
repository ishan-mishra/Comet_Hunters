#!/usr/bin/env python3

import collections as clct, numpy as np, astropy.io.fits as fits
from matplotlib import pyplot as plt
from matplotlib import cm
import drawtools as draw
from PIL import Image

from imutil.reduction import sigmaclip
from imutil.reduction import boundary as bdr

IMSHOWARGS = { 'cmap' : cm.gray,
               'origin' : 'lower',
               'interpolation' : 'nearest' }
TIGHTPLOTPARS = { 'left' : 0,  'right' : 1, 'bottom' : 0, 'top': 1,
                  'wspace' : 0, 'hspace' : 0 }

def fixPixels(pix, bbox,bg):
    #
    # New pixel canvas
    ny, nx = pix.shape
    lx, ly = bbox.tolen()
    x1, y1, x2, y2 = 1, 1, lx, ly
    fixed = np.ones((ly, lx)) * bg

    if bbox.x1 < 1:
        x1 = 2 - bbox.x1
    if bbox.y1 < 1:
        y1 = 2 - bbox.y1
    if nx < lx:
        x2 = x1 + nx - 1
    if ny < ly:
        y2 = y1 + ny - 1

    fixed[y1 - 1 : y2, x1 - 1 : x2] = pix[:, :]

    return fixed

def trim(pix, bbox):
    return pix[bbox.y1 - 1: bbox.y2, bbox.x1 - 1: bbox.x2]

def subRegion(pix, bbox, bg, edgefix=False):
    pixbbox = bdr.fromshape(*pix.shape)
    subpix = trim(pix, pixbbox.fixbbox(bbox, edgefix=edgefix))
    if edgefix is True:  return subpix
    else:                return fixPixels(subpix, bbox, bg=bg)

def rmTicks(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

class poststamp(object):
    def __init__(self, pix, sigs=2.5, ni=5):
        self.pix = pix
        self.bbox = bdr.fromshape(*self.pix.shape)
        self.avg, self.std = sigmaclip(self.pix, sigs=sigs, ni=ni)
        self.stamps = clct.OrderedDict()

    @classmethod
    def fromfits(cls, filename, hduid=0, **kwargs):
        with fits.open(filename) as hdus:
            pix = np.copy(hdus[hduid].data)

        return cls(pix, **kwargs)

    def create(self, ctr, size, **kwargs):
        """
        1. trim the pixel array into postage stamp size
        2. save into a dictionary for plotting

        """
        bbox = bdr.frombox(*(ctr + size))
        pix = subRegion(self.pix, bbox, bg=self.avg, **kwargs)
        kw = IMSHOWARGS.copy()
        kw['extent'] = bbox.toextent()
        self.stamps.update({'-'.join(4 * ['%d']) % (ctr + size) : (pix, kw)})

    def plot(self, fns=None, figsize=(5,5), peak=None, inv=False, scale=(3.,5.),
             markers=[], color='r'):
        """
        plot the stamps stored in dictionary

        """
        nstamp = len(self.stamps)

        if fns is not None:
            if len(fns) != nstamp:
                raise ValueError('number of files is inconsistent with stamps')
        else:
            plt.ion()

        markobjs = markers + (nstamp - len(markers)) * [None]
        markcolors = color if type(color) is list else nstamp * [color]
        peaks = peak if type(peak) is list else nstamp * [peak]

        for i, (pix, kw) in enumerate(self.stamps.values()):
            kw['cmap'] = cm.gray if inv is False else cm.gray_r

            fig = plt.figure(figsize=figsize, dpi=100)
            if fns:  fig.subplots_adjust(**TIGHTPLOTPARS)

            ax = fig.add_subplot(111)

            vmin = self.avg - scale[0] * self.std
            vmax = self.avg + scale[1] * self.std if peaks[i] is None else \
                   self.avg + 1.1 * peaks[i]
            ax.imshow(pix, vmin=vmin, vmax=vmax, **kw)

            if markobjs[i] is not None:
                markobjs[i].draw(ax, color=markcolors[i], lw=3.)

            if fns is None:
                continue

            rmTicks(ax)

            plt.savefig(fns[i])
            plt.close('all')
#
############################################################################
# make gallery picture
############################################################################
#
def origin(center, size):
    return (int(center[0] - size[0] / 2), int(center[1] - size[1] / 2))

def atcenter(oldwh, newwh):
    o = origin((oldwh[0] / 2, oldwh[1] / 2), newwh)
    return (o[0], o[1], o[0] + newwh[0], o[1] + newwh[1])

def mkOB(imlist, bs, bgcolor='white'):
    big = min(imlist[0].size)
    sml = int((big + 2 * bs - len(imlist) * bs) / (len(imlist) - 1))
    new = Image.new('RGB', (big + sml + 3 * bs, big + 2 * bs), bgcolor)

    new.paste(imlist[0].crop(atcenter(imlist[0].size, 2 * (big,))), (bs, bs))
    for i, im in enumerate(imlist[1:]):
        org = (big + 2 * bs, bs + i * (sml + bs))
        new.paste(im.crop(atcenter(im.size, (sml, sml))), org)

    return new

class ImageList(list):
    def __init__(self, ims=[]):
        super(ImageList, self).__init__(ims)

    @classmethod
    def fromfiles(cls, files):
        """
        files argument can be:
        (1) a string of filename
        (2) a tuple or list of filenames

        """
        t = type(files)
        fns = files if t is list or t is tuple else [files] if t is str else []

        return cls([ Image.open(f) for f in fns ])

    def mkgallery(self, mode='OB', framesize=6, **kwargs):
        bdsz = int((framesize + 1) / 2) * 2
        if mode == 'OB':
            return mkOB(self, bdsz, **kwargs)
        else:
            raise ValueError('this mode is not implemented yet')

        return
