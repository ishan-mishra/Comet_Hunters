#!/usr/bin/env python3

import re, os, sys, collections as clct, numpy as np
from fnmatch import filter as fnfilt
from getopt import getopt
from matplotlib import pyplot as plt

#from multiproc import usePool
#from db import sqlite as sql
from imutil import reduction as imred
#from imutil import suprimecam as spc
from imutil import plot as kplt
from imutil.plot import ImageList
import drawtools as draw

DBCOLS = {'mba': 'Obj.frameid,Obj.subid,Obj.ObjNumber,Obj.ObjName,' + \
                 'Obj.x0,Obj.y0,Obj.xc,Obj.yc,Obj.sep,Obj.fpeak,Obj.fwhm,' + \
                 'Obj.reff,Obj.class,Obj.flag' }

DBGET = 'SELECT %s From' + \
        ' (SELECT frameid From ObsData WHERE strftime("%%Y%%m",datetime) = ?' + \
        ' AND exptime > 120 AND (filter = "g" OR filter = "r")) as Obs' + \
        ' INNER JOIN %s as Obj on Obs.frameid = Obj.frameid'

DBTBLS = { 'mba' : 'ObjFoundData', 'ref' : 'RefstarData' }

IMGFNFMT = '%s/%s.fits'
SEPLIM = 25. # pixels (0.2 arcsec per pixel)
SEPMAX = 50. # pixels
PEAKMAX = 15000.

def mkfn(fn, subid):
    expid = fn.replace('HSCA', 'CORR-0')
    return expid[:-2] + '-%03d' % (subid)

def insertMBA(d, key, key2, val):
    if key in d.keys():
        if key2 in d[key].keys():
            d[key][key2]['mba'] += val['mba']
        else:
            d[key][key2] = val
    else:
        d[key] = { key2 : val }

def getDataFromDB(dbname, date):
    """
    date should have the format of %Y%m, e.g. 201604

    """
    with sql.open(dbname) as db:
        dbarg = DBGET % (DBCOLS['mba'],DBTBLS['mba'])
        objs = sql.execute(db).fetch(dbarg, (date,))

    objdict = clct.defaultdict(dict)
    for o in objs:
        name = o[2] if o[2] != 9999999 else o[3]
        insertMBA(objdict[o[0]], mkfn(o[0],o[1]), str(name), {'mba' : [o[4:]]})

    return objdict

def cleanObjects(objid, locs, sepcol=4, fpeakcol=3):
    """
    sepcol is the column index of separation in the output of database
    fpeakcol is the column index of flux-peak in the revised object info

    """
    objs = sorted(locs['mba'], key=lambda t:t[sepcol])
    if objs[0][sepcol] > SEPMAX:
        #print('%06d:' % objid, 'drop this object (sep=%.1f)...' % objs[0][sepcol])
        return objid, []
    elif objs[0][sepcol] > SEPLIM or objs[1][sepcol] <= SEPLIM:
        # use the predicted location because
        # 1. away from center more that 10 pixels
        # 2. multiple sources within 10 pixels
        #print('%06d:' % objid, '+++ use prediected loc +++')
        obj = (objs[0][0], objs[0][1],) + objs[0][sepcol:]
    else:
        # re-center!!!
        #print('%06d:' % objid, '*** re-center ***')
        obj = objs[0][2:]

    # if the object is close to saturate, remove it
    if obj[fpeakcol] > PEAKMAX:
        return objid, []

    return (objid, [obj])

def parseDate(yyyymm):
    if re.match('^(\d{4})(\d{2})$', yyyymm) is None:
        raise ValueError('the format of data is wrong: %s' % (yyyymm))

    return yyyymm

def usage(cmd):
    fmt = 'usage: %s\n' + \
          '    -d <date: YYYYMM> OR -e <date pattern: "YYYY??">\n' + \
          '   (note that qoutes are needed for pattern)\n' + \
          '    -t <db file>\n' + \
          '   [-f <image fits> -l <list of locations>]\n'
    sys.exit(fmt % (cmd.split('/')[-1]))

def getcmdOptions(cmd, argv):
    try:
        opts, args = getopt(argv, 'd:e:f:hl:t:')
    except getopt.GetoptError as err:
        print(err)
        usage(cmd)
        sys.exit(2)

    optdict = {'dates': None, 'dbname': None, 'fitsname': None, 'loclist': None}
    for o, a in opts:
        if o in ('-h', '--help'):
            usage(cmd)
            sys.exit()
        elif o in ('-d', '--date'):
            optdict['dates'] = [a]
        elif o in ('-e', '--dates'):
            optdict['dates'] = sorted(fnfilt(os.listdir(), a))
        elif o in ('-t', '--dbname'):
            optdict['dbname'] = a
        elif o in ('-f', '--fitsfile'):
            optdict['fitsname'] = a
        elif o in ('-l', '--loclist'):
            optdict['loclist'] = a

    if optdict['dates'] is not None:
        if optdict['dbname'] is None:
            usage(cmd)
    if optdict['dbname'] is not None:
        if optdict['dates'] is None:
            usage(cmd)

    return optdict

def fnFITS2PNG(filename, key):
    i = filename.rfind('.fits')
    return filename[:i] + key + '.png'

def fnInv(pngfile, key):
    i = pngfile.rfind('.png')
    return pngfile[:i] + key + '.png'

def mkGallery(filenames, inv=False):
    ims = ImageList.fromfiles(filenames)
    im = ims.mkgallery(bgcolor='white' if inv is False else 'black')
    fn = filenames[0][:filenames[0].rfind('.png')] + '.gallery.png'
    im.save(fn, 'PNG')
    print(fn, 60 * '-', sep='\n')

FNFMT = '-mba_%s-%02d-sep%02.0f'
def mkPoststamp(fname, data, size=(120,120), scale=(3.0,5.0), edgefix=False,
                  ioff=True, usepeak=False, inv=False):
    print(fname)

    objlist = [cleanObjects(num, locs) for num, locs in data.items()]

    if sum([len(obj[1]) for obj in objlist]) == 0:
        print('+++ no object in this fits "%s" for plotting! +++' % fname)
        return

    print(70 * '=')
    stamp = kplt.poststamp.fromfits(fname, hduid=1, sigs=(3.,2.5), ni=8)
    for num, trgs in objlist:
        if len(trgs) == 0:
            continue

        print(60 * '-')
        print(num, trgs)
        objnm = num.replace(' ', '_')
        #print('%06d' % num, refs)

        fns, peaks, marks, colors = [], [], [], []
        for locinfo in trgs:
            stamp.create(locinfo[0:2], size, edgefix=edgefix)
            fns    += [fnFITS2PNG(fname, FNFMT % (objnm, 0, locinfo[2]))]
            peaks  += [locinfo[3]] if usepeak is True else [None]
            marks  += [draw.cross(locinfo[0:2], 15, sep=22, mode='topleft')]
            colors += ['#ee00ee']

        #print(60 * '-')

        stamp.plot(fns=fns if ioff else None, peak=peaks, inv=False,
                   scale=scale, markers=marks, color=colors)
        #if ioff is True:
        #    mkGallery(fns, inv=False)

        if inv is True:
            invfns = [fnInv(fn, '-inv') for fn in fns]
            stamp.plot(fns=invfns if ioff else None, peak=peaks, inv=True,
                       scale=scale, markers=marks, color=colors)
            #if ioff is True:
            #    mkGallery(invfns, inv=True)

        stamp.stamps.clear()

    #input('press: ')
    #plt.close('all')

def mkPoststampWrapper(argtuple):
    filename, data = argtuple

    if os.path.exists(filename) is False:
        return

    mkPoststamp(filename, data, ioff=True, inv=True)

def main(argv=None):
    optdict = getcmdOptions(argv[0].split('/')[-1], argv[1:])
    print(optdict)

    if optdict['dates'] is None:
        return

    for d in optdict['dates']:
        path, objdict = d, getDataFromDB(optdict['dbname'], parseDate(d))

        for frameid, fnnumdata in sorted(objdict.items()):
            args = [(IMGFNFMT % (path, fn), numdata)
                    for fn, numdata in sorted(fnnumdata.items())]
            print('\n', 'FrameID: ', frameid, ' (%d)' % len(args), '\n', sep='')
            #for arg in args:
            #    mkPoststampWrapper(arg)
            usePool(mkPoststampWrapper, args, njob=8)


if __name__ == '__main__':
    sys.exit(main(argv=sys.argv))
