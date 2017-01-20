# Comet_Hunters

A python based program to generate simulated MBC images. 

Python libraries required:

numpy
matplotlib
astropy
scipy
sys
configparser
os

Steps:

1. Enter the necessary information in the param.ini file:
    
    1.1. Type of object you want to generate
    1.2. Parameters corresponding to that object type
    1.3. Paths to folders where you want to store the generated .fits and .png files

2. Run the master.py file. 


Note: 

1.  Individual objects can also be generated using the main_coma.py and main_tail.py scripts. You will need to provide arguments
    while running the file from command line. Please refer to the definition of the main() function in these scripts to know which
    parameters need to be supplied. 

    For example, to generate a coma with eta = 10.0, speed = 50.0 arcsec/hour, angle = 90.0 degrees,
    exposure_time = 150 seconds and the folder paths to store generated images as 'fits_path' and 'png_path':

    >>> python main_coma.py 10.0 50.0 90.0 150.0 fits_path png_path
    
2.  An ascii table named 'info.txt' will be maintained in the folder containing all the fits files. This .txt file will store
    the parameter values used to generate each file. 
    



