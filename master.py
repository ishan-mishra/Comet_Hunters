# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 18:19:03 2016

@author: ishan

"""

#import main_coma
#import main_tail

#from astropy.table import Table

'''Master file to generate multiple images'''

import configparser
import sys
import numpy as np
import main_coma
import main_tail
import os
from astropy.io import ascii
from astropy.table import Table

#import information from the param.ini file. This file should be in the sam directory as the 
#master.py file


config = configparser.ConfigParser()

config.read('param.ini')

#Get the type of object that the user wants to generate

obj_type = str(config['OBJ TYPE']['type'])


if obj_type == 'C':
    
    param = 'PARAMS COMA'
    
elif obj_type == 'T':
    
    param = 'PARAMS TAIL'
    
else:
    sys.exit('Please enter correct input for file_type in the param.ini file')
    
print('The user wants to generate ', obj_type, 'type images')


#Get the number of objects the user wants to generate

num_objs = int(config[param]['num_objs'])

#Get the input type: specific values or range limits

val_type = str(config[param]['val_type'])


#Get the parameters for image


if obj_type == 'C':

    if val_type == 'specific':
    
        eta = str(config[param]['eta']).split()
        eta = [float(i) for i in eta]
    
        #check if the number of entries for eta is equal to the value of num_objs
    
        if len(eta) != num_objs:
            sys.exit('Number of entries for \'eta\' do not match the total number of objects')
        
    
        speed = str(config[param]['speed']).split()
        speed = [float(i) for i in speed]

        if len(speed) != num_objs:
            sys.exit('Number of entries for \'speed\' do not match the total number of objects')    
    
        angle = str(config[param]['angle']).split()
        angle = [float(i) for i in angle]
    
        if len(angle) != num_objs:
            sys.exit('Number of entries for \'angle\' do not match the total number of objects') 
        
        exposure_time = str(config[param]['exposure_time']).split()
        exposure_time = [float(i) for i in exposure_time]
    
        if len(exposure_time) != num_objs:
            sys.exit('Number of entries for \'exposure_time\' do not match the total number of objects')
    

    elif val_type == 'range':
    
        limits = str(config[param]['eta']).split()
    
        #check if the number of entries for eta is equal to 2, ie, the upper and lower limits of 
        #the range
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'eta\' should be equal to 2')
        
        eta = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)
    
    
        limits = str(config[param]['speed']).split()
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'speed\' should be equal to 2')
        
        speed = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)
    
        limits = str(config[param]['angle']).split()
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'angle\' should be equal to 2')
        
        angle = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)
    
        limits = str(config[param]['exposure_time']).split()
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'exposure_time\' should be equal to 2')
        
        exposure_time = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)
    
    
    else: 
    
        sys.exit('Please enter the correct entry for val_type')
  
  
elif obj_type == 'T':

    if val_type == 'specific':
    
        eta = str(config[param]['eta']).split()
        eta = [float(i) for i in eta]
    
        #check if the number of entries for eta is equal to the value of num_objs
    
        if len(eta) != num_objs:
            sys.exit('Number of entries for \'eta\' do not match the total number of objects')

        tail_length = str(config[param]['tail_length']).split()
        tail_length = [float(i) for i in tail_length]

        if len(tail_length) != num_objs:
            sys.exit('Number of entries for \'tail_length\' do not match the total number of objects')
            
        tail_angle = str(config[param]['tail_angle']).split()
        tail_angle = [float(i) for i in tail_angle]

        if len(tail_angle) != num_objs:
            sys.exit('Number of entries for \'tail_angle\' do not match the total number of objects')
    
        speed = str(config[param]['speed']).split()
        speed = [float(i) for i in speed]

        if len(speed) != num_objs:
            sys.exit('Number of entries for \'speed\' do not match the total number of objects')    
    
        angle = str(config[param]['angle']).split()
        angle = [float(i) for i in angle]
    
        if len(angle) != num_objs:
            sys.exit('Number of entries for \'angle\' do not match the total number of objects') 
        
        exposure_time = str(config[param]['exposure_time']).split()
        exposure_time = [float(i) for i in exposure_time]
    
        if len(exposure_time) != num_objs:
            sys.exit('Number of entries for \'exposure_time\' do not match the total number of objects')
    

    elif val_type == 'range':
    
        limits = str(config[param]['eta']).split()
    
        #check if the number of entries for eta is equal to 2, ie, the upper and lower limits of 
        #the range
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'eta\' should be equal to 2')
        
        eta = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)

        limits = str(config[param]['tail_length']).split()
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'tail_length\' should be equal to 2')
        
        tail_length = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)
        
        limits = str(config[param]['tail_angle']).split()
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'tail_angle\' should be equal to 2')
        
        tail_angle = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)        
    
        limits = str(config[param]['speed']).split()
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'speed\' should be equal to 2')
        
        speed = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)
    
        limits = str(config[param]['angle']).split()
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'angle\' should be equal to 2')
        
        angle = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)
    
        limits = str(config[param]['exposure_time']).split()
    
        if len(limits) != 2:
            sys.exit('Number of entries for \'exposure_time\' should be equal to 2')
        
        exposure_time = np.random.uniform(float(limits[0]),float(limits[1]),num_objs)
    
    
    else: 
    
        sys.exit('Please enter the correct entry for val_type')
        
        

#Get the paths to the folders where you want to store the fits and png images

fits_path = str(config['PATHS']['fits_path'])
png_path = str(config['PATHS']['png_path'])


#Generate the images

if obj_type == 'C':
    
    for i in range(num_objs):
        
        main_coma.main(eta[i], speed[i], angle[i], exposure_time[i], fits_path, png_path)
        
elif obj_type == 'T':
    
    for i in range(num_objs):
        
        main_tail.main(eta[i], tail_length[i], tail_angle[i], speed[i], angle[i], \
        exposure_time[i], fits_path, png_path)
        
        
        
#Generate an ascii table storing information about the images

#Get list of all fits files in the directory

fits_list = []

for file in os.listdir(fits_path):
    if file.endswith(".fits"):
        fits_list.append(file) 
        
#Check if an ascii table called info.txt exists. If not, create one and add an empty table 
#to it. It should have the columns file_name, eta, speed, angle, exopsure_time, tail_length and tail_angle.
#The last 2 (tail_angle and tail_length) should be left blank for coma entries.
        
for file in os.listdir(fits_path):
    if file == 'info.txt':
        break
    else: 
        images_file = open(fits_path + 'info.txt','w')
        file_name = []; eta = []; speed = []; angle = []; exposure_time = []; tail_length = [];
        tail_angle = []
        data = Table([file_name, eta, speed, angle, exposure_time, tail_length, tail_angle], \
        names = ['file_name', 'eta', 'speed', 'angle', 'exposure_time', 'tail_length', 'tail_angle'])
        ascii.write(data, fits_path + 'info.txt')
        
#
    

