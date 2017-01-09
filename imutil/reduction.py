#!/usr/bin/env python3

import sys, numpy as np, numpy.ma as ma #, pyfits as fits

'''def editFITSfn(fn, key=''):
    return fn[:fn.rfind('.fits')] + key + '.fits'

def editSuffixfn(fn, suffix=''):
    i = fn.rfind('.')
    return fn[:i if i != -1 else len(fn)] + suffix
'''
def sigmalim(avg, std, lowsig, uppsig):
    """
    avg -/+ std * (lowsig, uppsig)

    """
    return (avg - std * lowsig, avg + std * uppsig)

def fixsigma(sigs):
    t = type(sigs)
    tup = tuple(sigs) if t is tuple or t is list else (sigs, sigs)
    return tup if len(tup) == 2 else 2 * tup if len(tup) == 1 else tup[:2]

def sigmaclip(a, sigs=(3.,), ni=3):
    sigtup = fixsigma(sigs)

    b = ma.array(a)
    for i in range(ni):
        low, upp = sigmalim(b.mean(), b.std(), *sigtup)
        b = ma.masked_where((a < low) | (a > upp), a)

    return b.mean(), b.std()
'''
def argsigmaclip(a, sigs=(3.,), ni=3):
    sigtup = fixsigma(sigs)
    low, upp = sigmalim(*(sigmaclip(a, sigs=sigtup, ni=3) + sigtup))
    return np.where((a >= low) & (a <= upp))

def basefn(filename):
    return filname.split('/')[-1]

def imcomb(aaa, mode='mean'):
    if   mode == 'mean':   return aaa.mean(axis=0)
    elif mode == 'median': return aaa.median(axis=0)
    else:                  return aaa.sum(axis=0)

def imarith(a, b, op='-'):
    """
    a and b is HDU and a will be modified after operation
    op can be +, -, *, /

    """
    if a.shape != b.shape:
        raise ValueError('inconsist dimension between to two HDUList[0]')
    if   op == '+': a.data += b.data
    elif op == '-': a.data -= b.data
    elif op == '*': a.data *= b.data
    elif op == '/': a.data /= b.data
    else:
        raise ValueError('operator %s is not supported' % (op))

    a.header.add_history('imarith operation:')
    a.header.add_history('%s %s %s' % (a.filename(), op, b.filename()))

def hdutype(hdu):
    """
    return Image or Table, could be None

    """
    if hdu.header['NAXIS'] < 2:
        return 'None'

    name = hdu.__class__.__name__
    if 'Primary' in name: return 'Image'
    elif 'Image' in name: return 'Image'
    elif 'Table' in name: return 'Table'
    else:                 return 'None'
    


class HDUList(fits.HDUList):
    def __init__(self, hdus=[], file=None):
        super().__init__(hdus, file=file)

    def clean(self, bias, flat, ids=[0]):
        if not bias:
            for i in ids if len(ids) else range(len(self)):
                if hdutype(self[i]) == 'Image':
                    imarith(self[i], bias, op='-')
        if not flat:
            for i in ids if len(ids) else range(len(self)):
                if hdutype(self[i]) == 'Image':
                    imarith(self[i], flat, op='/')

def fitsopen(filename, mode='readonly', memmap=None, **kwargs):
    if not filename:
        raise ValueError('Empty filename: %s' % repr(filename))

    if memmap is None:
        from pyfits import USE_MEMMAP
        memmap = USE_MEMMAP

    return HDUList.fromfile(filename, mode, memmap, **kwargs)

class ImageHDUList(list):
    def __init__(self, hdus=[], fns=[]):
        """
        hdus is a list of HDUs
        fns is file names related to each hdu

        """
        fnlist = fns if len(fns) == len(hdus) else len(hdus) * ['None']
        imhdus, self.filenames = [], []
        for hdu, fn in zip(hdus, fnlist):
            if hdu.is_image:
                imhdus += [hdu]
                self.filenames += [fn]

        super().__init__(imhdus)

    @classmethod
    def fromfiles(cls, files, hduids=[0]):
        ulist, flist = [], []
        for hdus in (fitsopen(f) for f in files):
            fn = basefn(hdus.filename())
            ulist += [hdu[i] for i in hduids]
            flist += ['%s[%d]' % (fn, i) for i in hduids]

        return cls(ulist, flist)

    def combine(self, mode='median'):
        cube = np.array([ hdu.data for hdu in self ])
        return imcomb(cube, mode=mode)

def mkmaster(filenames, mode='median'):
    hduset = ImageHDUList.fromfiles(filenames)
    data = hduset.combine(mode=mode)
    hdr = hduset[0].header.copy()
    hdr.add_history('make master frame with %s)' % mode)
    for v in hduset.filenames:
        hdr.add_history(v)

    return fits.PrimaryHDU(data, hdr)
    
'''

class boundary(object):
    def __init__(self, x1, x2, y1, y2):
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2

    @classmethod
    def fromsize(cls, x1, xs, y1, ys):
        return cls(x1, x1 + xs, y1, y1 + ys)

    @classmethod
    def fromshape(cls, ny, nx):
        return cls(1, nx, 1, ny)

    @classmethod
    def frombox(cls, cx, cy, lx, ly):
        wh = np.array([lx,ly], dtype=int)
        b1 = np.array([cx,cy], dtype=int) - (wh / 2).astype(int)
        b2 = b1 + wh - 1
        return cls(b1[0], b2[0], b1[1], b2[1])

    def toextent(self):
        """
        for the argument of extent in imshow in matplotlib

        """
        bd = np.array([self.x1, self.x2, self.y1, self.y2])
        return tuple(bd + np.array([-0.5, +0.5, -0.5, +0.5]))

    def copy(self):
        return boundary(self.x1, self.x2, self.y1, self.y2)

    def tolen(self):
        return (self.x2 - self.x1 + 1, self.y2 - self.y1 + 1)

    def fixbbox(self, bbox, edgefix=False):
        fixed = bbox.copy()
        #
        # the corner close to origin (x1, y1)
        if  bbox.x1 <  self.x1:
            fixed.x1 =  self.x1
            if edgefix is True:
                fixed.x2 += self.x1 - bbox.x1

        if  bbox.y1 <  self.y1:
            fixed.y1 =  self.y1
            if edgefix is True:
                fixed.y2 += self.y1 - bbox.y1
        #
        # the corner away from origin (x2, y2)
        if  bbox.x2 >  self.x2:
            fixed.x2 =  self.x2
            if edgefix is True:
                fixed.x1 += self.x2 - bbox.x2

        if  bbox.y2 >  self.y2:
            fixed.y2 =  self.y2
            if edgefix is True:
                fixed.y1 += self.y2 - bbox.y2

        return fixed
