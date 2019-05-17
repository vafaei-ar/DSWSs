#! /home/gf/packages/anaconda3/bin/python

import numpy as np
import cv2
from tkinter import *
#import tkinter as tk
from PIL import Image, ImageTk
import signal
import sys

def signal_handler(sig, frame):
    ans = input('Do you wanna shut it down?\n')
    if ans[0]=='y': 
        webcam.cap.release()
        webcam.window.destroy()
        sys.exit(0)
    else:
        geo = whichpos(ans)
        webcam.change_pos(geo)
    
def whichpos(pos):
    if pos=='ul':
        geo = "+0+28"
    elif pos=='ll':
        geo = "+0-20"
    elif pos=='ur':
        geo = "-0+28"
    elif pos=='lr':
        geo = "-0-20"
    else:
        exit()
    return geo

class WebCam(object):
    def __init__(self,geo):
        self.window = Tk()  #Makes main window
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)
        self.window.geometry(geo)
        self.display1 = Label(self.window)
        self.display1.grid(row=1, column=0, padx=0, pady=0)  #Display 1
        self.cap = cv2.VideoCapture(0)

    def show_frame(self):
        _, frame = self.cap.read()
        frame = cv2.resize(frame, (200,150))
        #frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(master = self.display1, image=img)
        self.display1.imgtk = imgtk #Shows frame for display 1
        self.display1.configure(image=imgtk)
        self.window.after(1, self.show_frame)
        
    def __call__(self):
        self.show_frame()
        self.window.mainloop()
        
    def change_pos(self,geo):
        self.cap.release()
        self.window.destroy()
        self.__init__(geo)
        self.__call__()

signal.signal(signal.SIGINT, signal_handler)
try:
    pos = sys.argv[1]
except:
    pos = 'ul'
    
geo = whichpos(pos)
webcam = WebCam(geo)
webcam()

