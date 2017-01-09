# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 22:55:42 2016

@author: ishan
"""

import library
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy import random,signal
import pyds9
import imutil.plot as kplt
import drawtools as draw

import sys

def main(eta, speed, angle, exposure_time, fits_path, png_path):

    ''' Main program to generate a trailed asteroid image with/without a coma'''

    '''Define the necessary parameters

    The parameters needed as input are:

    1. eta : ratio of intensity/flux of coma to intensity/flux of asteroid.

             eta = 0 implies no coma. 

    2. nucleus_value : The intensity value of asteroid, which is just a single pixel at the
                   center of the image throughout this work. The default value is 1.
                   
    3. pre_pixel_scale: The high resolution used for the first couple of stages. This needs to be 
                    much higher than the Subaru pixel scale. Default value: 0.01 arcsec/pixel.
                    Note that the minimum value of this scale is decided by the computational
                    strength of your machine. (Works fine till 0.004 arcsec/pixel in Ishan's PC)
                    
    4. subaru_pixel_scale: Pixel scale of the images obtained from Subaru Telescope. Assumed as
                       0.17 arcsec/pixel
                       
    5. coma_size: radius of coma used for calculating flux in the coma, which in turn is used to 
              calculate the eta value defined above. Default value: 2 arcsec
              
    6. image_size: The size of the image. Default value: 20 arcsec

    7. speed: The speed with which the asteroid is moving in the plane of the sky. 
          Default value: 50 arcsec/hour
          
    8. angle: The direction in which the asteroid is moving. This is given as an angle from the 
          x axis of the image (image[:,0]).
                  
    9. exposure_time: The exposure time of the camera in the actual telescope. Here it decides the
                  length of trail of the asteroid. 
                 


    '''


    #eta, speed, angle and exposure_time provided by the user
    nucleus_value = 1.0
    pre_pixel_scale = 0.01  #in arcsec/pixel
    subaru_pixel_scale = 0.17  #in arcsec/pixel
    coma_size = 2.0 #arcsec  
    image_size = 20.0 #arcsec
    
   
   

    '''Warning! Don't make the ratio image_size/pre_pixel_scale greater than about 5000. You will get a memory
    error'''


    '''Part 1: High resolution asteroid with coma image'''

    coma = library.generateComa(eta,nucleus_value,pre_pixel_scale,image_size,coma_size)
   #no_coma = library.generateComa(0,10,0.1,10.0,0,nucleus_value,pixel_scale)

    coma.findScaleFactor()
    #no_coma.findScaleFactor()

    coma.create()
    #no_coma.create()

    coma_high_res = coma.z_pre

    center = int(coma.z_pre.shape[0]/2)

    #plt.figure(1)
    #plt.imshow(coma.z_pre[center-50:center+50,center-50:center+50],cmap='gray')
    #plt.title('With coma (eta='+repr(eta)+')')
    
    #plt.figure(2)
    #plt.imshow(no_coma.z_post,cmap='gray')
    #plt.title('Without coma (eta=0)')


   
    '''Part 2: Trailing
    
    We will use the module trailComa. It needs to be initialized with the following arguments:
    
            1) input_coma: the input coma image
            2) velocity: velocity is an object of type velocity
            3) total_time: total exposure time in seconds
            4) pre_pixel_scale: the initial high resolution pixel scale
            
      To account for velocity as a vector, we have defined a class 'velocity' which takes the 
      arguments:
      
            1) speed: in arcsec/hour
            2) angle: in degrees
            
    '''
    
    #defne velocity  
    
    
    vel = library.velocity(speed,angle)
    
    #initialize an object of type trailComa
    
    trailed_coma = library.trailObject(coma_high_res,vel,exposure_time,pre_pixel_scale)
    
    #Create trailed image
    
    trailed_coma.create()
    
    trailed_high_res = trailed_coma.output_object
    #display the trailed image
    
    #shift = int(trailed_coma.dist_mov/(2*pre_pixel_scale))
    
    #shift = 250
    
    #plt.figure(2)
    #plt.imshow(trailed_coma.output_coma[center-shift:center+shift,center-shift:center+shift],cmap = 'gray')
    #plt.title('Trailed coma pre-interpolation (pixel scale = Subaru/'+repr(subaru_pixel_scale/coma.pre_pixel_scale)
    #+')'+ '(eta='+repr(eta)+')'+'Angle ='+repr(angle))
    
    
    
    
    '''Part 3: Downgrading the high resolution trailed image to subaru's resolution'''
    
    
    
    #Grid and Sum the image as in CCD
    
    trailed_low_res = library.binAndSum(trailed_high_res,pre_pixel_scale,subaru_pixel_scale)
    
    
    #Ensure image is 100x100 sized.
    if trailed_low_res.shape[0] > 101:
        shift = int((trailed_low_res.shape[0] - 101)/2)
        trailed_low_res = trailed_low_res[shift:(trailed_low_res.shape[0]-shift-1),shift:(trailed_low_res.shape[0]-shift-1)]
    
    
    trailed_low_res = trailed_low_res/trailed_low_res.max()
    
    
    '''Part 4: Convolve with Background star'''
    
    
    
    #hdulist = fits.open('/home/ishan/CometHunters@laserfloyd/Data/psf/psf.10.fits')
    hdulist = fits.open('/home/ishan/CometHunters@laserfloyd/Data/psf_edited/psf.10a.fits')
    hdulist1 = fits.open('/home/ishan/CometHunters@laserfloyd/Data/psf_no_stars/psf.10b.fits')
    
    
    background = hdulist[0].data
    background = background - background.min() #negative values found in the image
    
    '''We need to divide the background star's flux by the number of times the asteroid
    is repeated on the trailed image. This is to ensure that the total flux in the final convovled
    asteroid is same as the total flux of the original background star.
    
    We are working under the assumption that the asteroid and the background star are of the same
    magnitude.
    
    '''
    
    #finding number of times the asteroid gets copied in the trailed image 
    asteroid_count = trailed_coma.total_time/trailed_coma.single_time 
     
    #background = background/30.0
    background = background/asteroid_count
    
    
    conv_coma = library.convolveBgd(trailed_low_res,background,50)
    
    #conv_coma = conv_coma - conv_coma.min()
    #conv_coma = conv_coma/conv_coma.max()
    
    '''Part 5: Generate trailed background'''
    
    
    #Remove the central star from the abckground image (Trial and Error)
    background[45:55,45:55] = background[0:10,0:10]
    #background[44:56,44:56] = background[0:12,0:12]
    
    '''hdulist1 = fits.open('/home/ishan/CometHunters@laserfloyd/Data/psf_no_stars/psf.10b.fits')
    
    
    background = hdulist1[0].data
    background = background - background.min() #negative values found in the image
    background = background/30.0'''
    
    
    #convolve model trailed asteroid with the nosiy background
    trailed_bgd = signal.convolve2d(trailed_low_res,background,boundary='symm',mode='same')
    
    
    
    '''Part 6: Trailed Background Subtraction'''
    
    
    
    coma_mod2 = conv_coma - trailed_bgd
    
    #temp = np.ones_like(coma_mod2)
    
    #temp = temp*np.mean(background)
    
    #temp = random.poisson(temp)
    
    #coma_mod2 = coma_mod2 + temp
    
    coma_mod2 = coma_mod2 - coma_mod2.min()   #min value negative fot eta = 0 case
    
    
    '''Part 7: Add Noise'''
    
    coma_mod2 = coma_mod2 + np.mean(background)
    
    
    
    coma_mod2 = random.poisson(coma_mod2)
    
    final_image = np.copy(coma_mod2)
    
    #save image in a fits file
    
    hdu = fits.PrimaryHDU(final_image)
    
    prihdr = fits.Header()
    
    prihdr['ETA'] = (eta,'ratio of brightness of coma/tail to brightness of asteroid')
    prihdr['IMAGE_SCALE'] = (0.17,'in arcsec/pixel')
    prihdr['IMAGE_SIZE'] = (20.0,'in arcsec')
    prihdr['POS_X_AXIS'] = ('Right edge pointing north','Positive X-Axis convention for angles')
    prihdr['POS_Y_AXIS'] = ('Bottom edge pointing west','Positive Y-Axis convention for angles')
    prihdr['TRAIL SPEED'] = (speed,'in arcsec/hour ')
    prihdr['TRAIL_ANGLE'] = (angle,'in degrees')
    prihdr['EXP_TIME'] = (exposure_time,'exposure time in seconds')
    
    hdu = fits.PrimaryHDU(data=final_image,header=prihdr)

    #Naming covention: cobine eta and angle (unique combination for each object)
    
    file_name = "{:.3f}".format(eta) + '_' + "{:.3f}".format(angle) + '.fits'
    file_path = fits_path + file_name
    
    hdu.writeto(file_path)
    
    #Convert image to stamp
    stamp = kplt.poststamp.fromfits(file_path,hduid=0,sigs=(3.,2.5),ni=8)
    stamp.create((50,50),(50,50),edgefix=False)
    marks = [draw.cross((50,50),10,sep=5,mode='topleft')]
    
    file_name = str(eta) + '_' + str(angle) + '.png'
    file_path = png_path + file_name
    
    stamp.plot(fns=[file_path], peak=2000, scale=(3., 5.), markers=marks, color='#ee00ee')
    stamp.stamps.clear()
    
    #Display in zscale in DS9
    
    #d = pyds9.DS9()
    
    #d.set_np2arr(coma_mod2)
    
    #d.set('zoom to fit')
    
    #d.set('scale zscale')
    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1],sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]))