from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.ndimage.interpolation import shift
from scipy import signal
from scipy.ndimage.filters import uniform_filter

############################COMA LIBRARY################################################

class generateComa:

    #This creates a coma defined by the given arguments.
    #pre_pixel_scale is in the units of arcsec/pixel

    def __init__(self,eta,nucleus_value,pre_pixel_scale,image_size,coma_radius):
        self.lower = 0.0
        self.image_size = image_size    
        self.pre_pixel_scale = pre_pixel_scale         #the area which covers all of the MBC
        self.upper = self.image_size/self.pre_pixel_scale
        self.pre_step = 1.0                            #This should always be 1.0
        self.eta = eta
        self.nucleus_value = nucleus_value
        self.coma_radius = coma_radius
        
    
    '''Now we need to find the constant to be multiplied to each pixel of the coma (to be 
      generated later) so that the eta condition is satisfied, ie, the flux in the coma and 
      the flux of the asteroid are in the desired ratio.
     
      This constant is being denoted as scale factor in the following function.
      
    '''
    
    
    def findScaleFactor(self):
       
        #For now, we are assuming an aperture of 5 arsec. 
       
        self.coma_size = int(self.coma_radius/self.pre_pixel_scale)  #coma_size in pixels
        
        #create the 1/r prfile around the nucleus        
        
        x = np.arange(self.lower,self.upper,self.pre_step)
        y = np.arange(self.lower,self.upper,self.pre_step)
        
        xx,yy = np.meshgrid(x,y)
	
        z = np.zeros(xx.shape,dtype=float)
        
        
        #Create a 1/r profile around the central pixel in z.

        m = (xx != self.upper/2)      
        n = (yy != self.upper/2)
        
        o = np.logical_or(m,n)  #Just leave the center pixel as False
        
        z[o] = 1.0/(np.sqrt((xx[o]-self.upper/2)**2 + (yy[o]-self.upper/2)**2))
        
        self.z = z
        
        
       
        #find the intensity in the coma_size area around the nucleus
        
       
        img_size = int(self.upper/self.pre_step)
        center = img_size/2
        
        self.coma_flux = 0
        
        m = (np.sqrt(((xx-center)**2 + (yy-center)**2)) < self.coma_size) #finding indices within the 
                                                                 #coma radius
        coma_count = z[m]   #assimilating all the values from the pixels in coma
        
        self.coma_flux = np.sum(coma_count)
        

        
        self.scale_factor = self.nucleus_value*self.eta/self.coma_flux    
    
    
    def create(self):
        
        print('Creating Coma.... \n')
        
        x = np.arange(self.lower,self.upper,self.pre_step)
        y = np.arange(self.lower,self.upper,self.pre_step)
        
        xx,yy = np.meshgrid(x,y)
	
        z = np.zeros(xx.shape,dtype=float)
        
        #count = 0;
  
        print('size of array: ', xx.shape, '\n')
        
        #for loop optimization
        
        m = (xx != self.upper/2)      
        n = (yy != self.upper/2)
        
        o = np.logical_or(m,n)  #Just leave the center pixel as False
        
        z[o] = self.scale_factor*1.0/(np.sqrt((xx[o]-self.upper/2)**2 + (yy[o]-self.upper/2)**2))
        
        
        #z[center] = self.nucleus_value
        z[int(xx.shape[0]/2),int(xx.shape[0]/2)] = self.nucleus_value
        self.z_pre = z
        
        print('Pre-interpolation part completed...\n')
	

'''Redundant function! (Created during the initial phases of the project)'''

def postInterp(pre_pixel_scale,subaru_pixel_scale,z_pre):  
    
     
    lower = 0.0
    upper = z_pre.shape[0]
    pre_step = 1.0
    
    x = np.arange(lower,upper,pre_step)*100.0/upper
    y = np.arange(lower,upper,pre_step)*100.0/upper
    
    print('Interpolation initiated..')
        
    #Interpolation Step

    f = interpolate.interp2d(x,y,z_pre,kind='linear')
        
    #Post Interpolation Step
    post_step = subaru_pixel_scale/pre_pixel_scale
        
    x_new = np.arange(lower,upper,post_step)*100.0/upper
    y_new = np.arange(lower,upper,post_step)*100.0/upper
    z_new = f(x_new,y_new)
        
    print('Interpolation accomplished. \n ')
    
    return z_new
        

'''Redundant function! (Created during the initial phases of the project)'''
    
'''
def boxCarAvg(input_img,pre_pixel_scale,subaru_pixel_scale):
    
    #Function to apply a moving average to an input image. Size of the averaging window is given by
    #the ration of subaru_pixel_scale to pre_pixel_scale
    
    window_width = int(subaru_pixel_scale/pre_pixel_scale)
    
    #shift = window_width/2
    
    out_dim = int(input_img.shape[0]/window_width)
    
    output_img = np.zeros((out_dim,out_dim))
    
    count_i = 0
    
    count_j = 0
    
    for i in range(input_img.shape[0]):
        
        m = i + window_width
        
        for j in range(input_img.shape[1]):
            
            n = j + window_width
            
            if m < input_img.shape[0] and n < input_img.shape[1]:
                
                temp = input_img[i:m,j:n]
                
                avg = np.sum(temp)/(temp.shape[0]*temp.shape[1])
                
                if count_i < out_dim and count_j < out_dim:                
                    output_img[count_i,count_j] = avg
                
            count_j = count_j + 1
            
            j = j + window_width
            
        
        count_i = count_i + 1
        
        i = i + window_width
        
    return output_img
'''            
            
def binAndSum(input_img,pre_pixel_scale,subaru_pixel_scale):
    
    #Function to overlay the input image with a grid of bin size given by the ratio of 
    #subaru_pixel_scale to pre_pixel_scale and return an array with pixel values corresponding 
    #to sum of pixel values in each bin of the input image (replicating a CCD)
    
        
    
    bin_width = int(subaru_pixel_scale/pre_pixel_scale)     
    
    
    # Need to ensure that bin_width is odd to have a center pixel for each bin
    if bin_width%2 == 1:
        pass
    else: bin_width = bin_width + 1
    
    
    #Apply the uniform filter to the image                                                       
    
    filter_img = uniform_filter(input_img,size = bin_width,mode = 'constant')
    
    #We want total intensity in the window, not the average
    
    filter_img = filter_img*(bin_width**2)  
    
    #select indices which correspond to bin centers
    
    x = np.arange(0,input_img.shape[0],1.0)
    
    xx,yy = np.meshgrid(x,x)
    
    n = (xx%(bin_width) == int(bin_width/2))
    
    m = (yy%(bin_width) == int(bin_width/2))
    
    o = np.logical_and(m,n)
    
    
    #print(sum(sum(item == True for item in n)))
    total_trues = sum(sum(item == True for item in o))
    
    #Assuming input image is square    
    num_rows,num_cols = int(np.sqrt(total_trues)),int(np.sqrt(total_trues)) 
    
    output_img = filter_img[o].reshape(num_rows,num_cols)
    print(output_img.shape)
    
    return output_img
    
        
        
def dispImages(pre_image,post_image,extent):
    
    '''Function to display pre-interpolation and post-interpolation images'''
    
    plt.figure(1)
    
    size = pre_image.shape
    center = int(size[0]/2)
    
    plt.imshow(pre_image[center-extent:center+extent,center-extent:center+extent],cmap='gray')
    plt.title('pre-interpolation image \n (zoomed into central 100 x 100 pixels)')
    
    plt.figure(2)
    
    plt.imshow(post_image,cmap = 'gray')
    plt.title('post-interpolation image \n (of size 100 x 100 pixels)')
    

'''Redundant function! (Created during the initial phases of the project)'''
    
def createGaussian(size,FWHM,center=None):
    
    '''Function to return a 2D square gaussian matrix. Note that we will need to convert FWHM 
       to variance'''
    
    x = np.arange(0,size,1.0)
    y = np.arange(0,size,1.0)
    
    xx,yy = np.meshgrid(x,y)
    
    var = FWHM/(2.0*np.sqrt(2.0*math.log(2)))
    
    if center is None:
        
        x0 = y0 = size//2
        
    else:
        
        x0 = center[0]
        y0 = center[1]

    return np.exp(-((xx - x0)**2 + (yy - y0)**2)/var**2)/(2*np.pi*var**2)
    

class velocity:
    
    '''defining a velocity with speed and direction'''
    
    def __init__(self,speed,angle):
        
        self.speed = speed    #velocity in arcsec/hour
        self.angle = angle          #angle in degrees

class trailObject:
    
    '''Class for creating a trailed version of an input coma image'''
    
    def __init__(self,input_object,velocity,total_time,pixel_scale):
        
        self.input_object = input_object
        self.velocity = velocity        #velocity is an object of type velocity
        self.total_time = float(total_time)    #total exposure time in seconds
        self.dist_mov = self.velocity.speed*self.total_time/3600  #distance moved in arcsec
        self.pixel_scale = pixel_scale
        
    def create(self):
        
        '''Method to create the trailed image'''
        
        output_object = np.zeros_like(self.input_object)
        
        
        '''The algorithm:
        
        1. Start with single exposure time, ie, time interval between two succesive 
        instances of the asteroid in the ccd (because it is getting trailed) as 1.0
        
        2. Use this to define the shift vector, ie, the displacement vector of asteroid 
        in each time step. 
        
        3. Run a loop to check the values of the x and y elements of the shift vector. Keep
           increasing the single exposure time value to correspondingly increase their valus
           too untill they are significant (to be decided by trail and error)
           
        4. Use this shift vector to trail the asteroid for the given exposure time
        '''
        
        #initialize time step        
        self.single_time = 1.0  #initilize with 1 second
        
        #initialize shift vector or the displacement vector
        
        speed = self.velocity.speed/3600  #in arcsec/second
        
        shift_vector = np.array([self.single_time*math.cos(math.radians(self.velocity.angle)),
                                 self.single_time*math.sin(math.radians(self.velocity.angle))])
        
    
        #Divide by the pixel scale
        
        
        print(shift_vector)
        
        #Modify shift vector to appropriate to have appropriate element values
        
        if abs(shift_vector[0]) > 0 or abs(shift_vector[1]) > 0:
            
            while(abs(shift_vector[0]) <= 1 and abs(shift_vector[1])<=1):
                self.single_time = self.single_time*10.0 
                
                shift_vector = np.array([self.single_time*math.cos(math.radians(self.velocity.angle)),
                                 self.single_time*math.sin(math.radians(self.velocity.angle))])

        #round of to nearest integer

        shift_vector = shift_vector/self.pixel_scale
        
        shift_vector = shift_vector*speed
        
        roundOff = np.vectorize(round)
        shift_vector = roundOff(shift_vector).astype(int)
        
        

        print(shift_vector)             
        self.shift_vector = shift_vector
        #self.shift_vector = np.array([1,1])    #for testing integer shift vectors
                        
        #Find the number of times the asteroid needs to be displaced to cover the total distance        
        self.num_snaps = int(self.total_time/self.single_time)        
        
        #Trail the asteroid        
        
        initial_object = self.input_object
        
        print('Trailing process initiated..')
        
        for i in range(-int(self.num_snaps/2),int(self.num_snaps/2),1):
            
            temp = shift(initial_object,shift=self.shift_vector*i,order=1,mode='nearest')#/self.num_snaps
            
            output_object = output_object + temp
            
            #print('Number:', repr(i),'\n')            
            #print(output_coma)
            
        print('Trailing accomplished.')
        
                
        
        self.output_object = output_object/output_object.max()
            
           
            
def convolveBgd(coma_img,background_img,background_crop):
    
    #Function to convolve the trailed coma with a background star
    
    #define the background image 
    center = np.where(background_img == background_img.max())
    x = center[0][0]    
    y = center[1][0]   
    
    shift = background_crop
    
    '''We ensure that the background image is also of size 100x100'''
    
    if background_img.shape[0] == coma_img.shape[0]:
        return signal.convolve2d(coma_img,background_img,boundary='symm',mode='same')
    else: 
        background = background_img[x-shift:x+shift+1,y-shift:y+shift+1]
        return signal.convolve2d(coma_img,background,boundary='symm',mode='same')
    

######################################################################################


#####################TAIL LIBRARY########################################


class generateTail:
    
    #Function to generate an astroid with a horizontal tail having 1/ profile        

    
    def __init__(self,eta,nucleus_value,pre_pixel_scale,image_size,length,angle):
        
        
        self.eta = eta
        self.nucleus_value = nucleus_value
        self.pre_pixel_scale = pre_pixel_scale
        self.length = int(length/self.pre_pixel_scale)  #convert to pixels
        self.lower = 0.0
        self.image_size = image_size
        self.upper = self.image_size/self.pre_pixel_scale
        self.pre_step = 1.0                        #This should always be 1.0
        self.angle = angle 
        
        self.step = 1.0                           #Default step for shifting the pixels while 
                                                   #creating the tail
            
    def createTail(self):
    
        
        #create the 1/r tail from the nucleus       
        
        x = np.arange(self.lower,self.upper,self.pre_step)
        y = np.arange(self.lower,self.upper,self.pre_step)
        
        xx,yy = np.meshgrid(x,y)
        
        mm,nn = np.meshgrid(x,y)
        
        mm = mm*100.0/self.upper
        nn = nn*100.0/self.upper
	
        z = np.zeros(xx.shape,dtype=float)
        
        z[int(self.upper/2),int(self.upper/2)] = 1.0
        
        
       
        #initialize the shift vector
        
        shift_vector = np.array([self.step*math.cos(math.radians(self.angle)),
                                 self.step*math.sin(math.radians(self.angle))])
        
         
        print(shift_vector)
        
        #Modify shift vector to appropriate to have appropriate element values
        
        if abs(shift_vector[0]) > 0 or abs(shift_vector[1]) > 0:
            
            while(abs(shift_vector[0]) <= 1 and abs(shift_vector[1]) <=1):
                self.step = self.step*10.0 
                
                shift_vector = np.array([self.step*math.cos(math.radians(self.angle)),
                                 self.step*math.sin(math.radians(self.angle))])

       
        
        
    
        roundOff = np.vectorize(round)
        shift_vector = roundOff(shift_vector).astype(int)

        print(shift_vector)            
        self.shift_vector = shift_vector
        #self.shift_vector = np.array([1,1])    #for testing integer shift vectors
                        
        
        '''limit = int(self.length/self.step)
        
        output_tail = np.empty_like(z)
        
        print('Trailing process initiated..')
        
        for i in range(0,limit,1):
            
            temp = shift(z,shift=self.shift_vector*i,order=1,mode='nearest')#/self.num_snaps
            
            output_tail = output_tail + temp'''
        
        i = int(self.upper/2)
        j = int(self.upper/2)   
        
        m = int(self.upper/2)
        n = int(self.upper/2)
        
        
        
        while(np.sqrt((i-self.upper/2)**2 + (j-self.upper/2)**2) < self.length and i > 0 and j > 0):
            
            den = np.sqrt((mm[m,n]-50.0)**2 + (nn[m,n]-50.0)**2)

            if den == 0:
                z[i,j] = 1.0
            else:
                z[i,j] = 1.0/den
                
            i = i + shift_vector[0]
            j = j + shift_vector[1]
            
            #m = m + 1
            #n = n + 1
            m = m + shift_vector[0]
            n = n + shift_vector[1]
        
        #z[o] = 1.0/(np.sqrt((xx[o]-self.upper/2)**2 + (yy[o]-self.upper/2)**2))
        
        self.z = z
        
        
        
        #Calculate the flux in the tail
        
        img_size = int(self.upper/self.pre_step)
        center = img_size/2
        
        self.tail_flux = 0
        
        m = (np.sqrt(((xx-center)**2 + (yy-center)**2)) < self.length)  
                                                                 
        coma_count = z[m]   #gathering all the values from the pixels in tail
        
        self.tail_flux = np.sum(coma_count)
  
        
        #Calculate the flux in the tail        
        
        self.scale_factor = self.nucleus_value*self.eta/self.tail_flux  
        #self.scale_factor = 1.0
         
        z = z*self.scale_factor
        
        
        #set center pixel to 1.0
        
        z[int(z.shape[0]/2),int(z.shape[0]/2)] = self.nucleus_value
        
        self.z_pre = z
         
         
#############################################################################3333
    
#################################MISC. FUNCTIONS##########################
    
   
        
        