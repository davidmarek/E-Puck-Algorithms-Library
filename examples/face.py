#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

from Tkinter import *
from ImageTk import PhotoImage

import cv
import ImageDraw
import Image as Img

from epuck.controller import Controller


logging.basicConfig(level=logging.ERROR)

c = Controller('/dev/rfcomm0', timeout=5, asynchronous=True)

# Set camera properties
c.set_front_led(1)
c.set_camera(Controller.GREYSCALE_MODE, 55, 55, 8)

# Create the application layout
root = Tk()
img_face = Label(root)
img_face.pack()

cascade = cv.Load('haarcascade_frontalface_alt.xml')

def show_photo():
    # Get the photo
    img = c.get_photo() \
        .get_response() \
        .resize((200, 200), Img.ANTIALIAS)

    # Convert the photo for OpenCV
    cv_img = cv.CreateImageHeader(img.size, cv.IPL_DEPTH_8U, 1)
    cv.SetData(cv_img, img.tostring())

    # Find any faces in the image
    storage = cv.CreateMemStorage(0)
    cv.EqualizeHist(cv_img, cv_img)
    faces = cv.HaarDetectObjects(cv_img, cascade, storage, 1.2, 2,
                                cv.CV_HAAR_DO_CANNY_PRUNING)

    if faces:
        for f in faces:
            # Draw a border around a found face.
            draw = ImageDraw.Draw(img)
            draw.setfill(0)
            draw.rectangle([(f[0][0], f[0][1]), (f[0][0] + f[0][2], f[0][1] + f[0][3])])

    image = PhotoImage(img)
    img_face.config(image=image)
    img_face.img = image

    img_face.after(10, show_photo)

    #k = cv.WaitKey(1)

show_photo()
root.mainloop()







