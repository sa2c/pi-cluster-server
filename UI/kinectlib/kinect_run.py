#!/usr/bin/env python3
import sys, termios, tty, os, time
import cv2
import numpy as np
from scipy import interpolate

min_distance = 230 # out of 255
dmin = 1000
dmax = 3000
num_points = 150
smoothing_interval = 61
measurements = 10

dx = -5
dy = 35
dpx = 0.95
dpy = 0.9

fake = False
if len(sys.argv) > 1:
    if sys.argv[1] == 'fake':
        num_im = 1
        fake = True
        fake_depth = np.load("kinect_data.npy")
        fake_video = np.load("color_kinect_data.npy")
    else:
        from freenect import sync_get_depth, sync_get_video
        from freenect import DEPTH_MM
        num_im = int(sys.argv[1])
else:
    from freenect import sync_get_depth, sync_get_video
    from freenect import DEPTH_MM
    num_im = 1


fake_d_ind = 0
fake_v_ind = 0
def get_depth():
    global fake_d_ind
    if fake:
        depth = fake_depth[fake_d_ind%500]
        fake_d_ind+=1
        time.sleep(0.05)
    else:
        (depth,_) = sync_get_depth(format=DEPTH_MM)
    return depth

def get_video():
    global fake_v_ind
    if fake:
        rgb = fake_video[fake_v_ind%500]
        fake_v_ind+=1
        time.sleep(0.05)
    else:
        (rgb,_) = sync_get_video()
    return rgb


def threshold(d):
    t = d*(d>=1) + dmax*(d<1)
    t = (t-dmin)*(t>dmin)
    t = t*(d<dmax) + (dmax-dmin)*(d>=dmax)
    t = (t.astype(np.float32)*255/(dmax-dmin))
    return t

def remove_background(im,bg):
    diff = im - bg
    return im*( diff<-3 ) + 254*( diff>=-3 )

def measure_depth( n = measurements ):
    depth = get_depth()
    depth = threshold(depth)
    depth = depth.astype(np.float32)/n
    for m in range(1,n):
        d = get_depth()
        d = threshold(d)
        d = d.astype(np.float32)/n
        depth += d
    return depth

def measure_background():
    print("Measuring background")
    depth = measure_depth( 20 )
    np.save("floor.npy", depth)

def doloop():
    global min_distance, num_im, dx, dy, dpx, dpy
    while True:
        # Get a fresh frame
        rgb = get_video()
        depth = measure_depth()
        depthimage = np.dstack((depth,depth,depth)).astype(np.uint8)

        # remove the background
        if not os.path.exists("floor.npy"):
            measure_background()
        floor = np.load("floor.npy")
        depth = remove_background(depth,floor)

        cutimage = np.dstack((depth,depth,depth)).astype(np.uint8)

        #Find contour
        gray = cv2.cvtColor(cutimage,cv2.COLOR_BGR2GRAY)
        _, thresholded = cv2.threshold(gray,min_distance,255,cv2.THRESH_BINARY_INV)
        
        try:
          contours, hierarchies = cv2.findContours(thresholded,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
          contour = max(contours, key=cv2.contourArea)
          cv2.drawContours(depthimage, contour, -1, (0,0,255), 2)

          outline = np.copy(contour[:,0,:])
          tck, u = interpolate.splprep(outline.transpose(), s=0)
          du = 1/(num_points-1)        
          unew = np.arange(0, 1.0, du)
          out = interpolate.splev(unew, tck)
          
          outline[1,:] = outline[1,:]*dpy
          outline[1,:] = outline[1,:]+dy
          outline[0,:] = outline[0,:]*dpx
          outline[0,:] = outline[0,:]+dx
  
          outline = outline.transpose().reshape((-1,1,2))
          
          cv2.drawContours(rgb, [outline.astype(int)], -1, (0,0,255), 2)
          
          mask = np.zeros_like(rgb)
          cv2.drawContours(mask, [outline.astype(int)], -1, (255,255,255), -1)
          cropped = np.zeros_like(rgb)
          cropped[mask==255] = rgb[mask==255]
          
          da = np.hstack((depthimage,rgb))
          db = np.hstack((mask,cropped))
          da = np.vstack((da,db))
        except Exception as error:
          #raise error
          da = np.hstack((depthimage,rgb))

        # Simple Downsample
        cv2.imshow('both',np.array(da))
        #cv2.imshow('both',np.array(da[::2,::2,::-1]))

        key = cv2.waitKey(5)
        if chr( key & 255) == ' ': #space
            print('Writing contour')
            outline = outline.reshape((-1,2))
            outline[:,1:] = 480-outline[:,1:]
            #outline[:,0] = 640-outline[:,0]
            np.savetxt("scf{}-outline-coords.dat".format(num_im), outline, fmt='%i %i')
            cv2.imwrite("scf{}-depthimage.png".format(num_im),depthimage)
            cv2.imwrite("scf{}-colorimage.png".format(num_im), cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR) )
            cv2.imwrite("scf{}-fullcolorimage.png".format(num_im), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
            cv2.imwrite("scf{}-blackandwhiteimage.png".format(num_im), cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
            num_im += 1
        elif chr( key & 255) == 'b' : 
            measure_background()
        elif chr( key & 255) == 'w' :
            dy-=5
        elif chr( key & 255) == 's' :
            dy+=5
        elif chr( key & 255) == 'a' : 
            dx-=5
        elif chr( key & 255) == 'd' : 
            dx+=5
        elif chr( key & 255) == 'r' :
            dpy*=1.02
        elif chr( key & 255) == 'f' :
            dpy/=1.02
        elif chr( key & 255) == 't' :
            dpx*=1.02
        elif chr( key & 255) == 'g' :
            dpx/=1.02
        elif key == 65362: #up on linux
            min_distance += 10
            print("threshold ",min_distance)
        elif key == 65364: #down on linux
            min_distance -= 10
            print("threshold ",min_distance)
        elif key == -1: #none
            continue
        else:
            print(key)
        print(dx,dy,dpx,dpy) 

doloop()

