#!/usr/bin/python

import functools
import Image as Img

from Tkinter import *
from ImageTk import PhotoImage
from epuck import Controller

c = Controller('/dev/rfcomm0', asynchronous=True)

root = Tk()
img_camera = Label(root)
img_camera.pack()
img_modified = Label(root)
img_modified.pack()

def hue(r, g, b):
    M = max(r, g, b)
    m = min(r, g, b)
    C = M - m

    if C == 0:
        return None
    if M == r:
        h = float(g-b)/C % 6
    elif M == g:
        h = float(b-r)/C + 2
    elif M == b:
        h = float(r-g)/C + 4

    return h

def reduce_noise(image):
    step = 2
    for i in range(0, image.size[0]-step, step):
        for j in range(0, image.size[1]-step, step):
            pixels = [image.getpixel((i+x, j+y)) for x in range(step) for y in range(step)]
            sum_pixels = functools.reduce(
                lambda (r1,g1,b1), (r2,g2,b2): (r1+r2, g1+g2, b1+b2),
                pixels)
            avg_pixel = map(lambda x: x / (step * step), sum_pixels)

            for x in range(step):
                for y in range(step):
                    image.putpixel((i+x, j+y), tuple(avg_pixel))

def saturation(r, g, b):
    V = M = max(r,g,b)
    m = min(r,g,b)
    C = M - m
    if C == 0:
        return 0
    else:
        return float(C)/V

def value(r, g, b):
    return max(r, g, b) / 255.0

def filter_red(image):
    saturation_threshold = 0.4
    value_threshold = 0.3
    data = []
    for (r,g,b) in image.getdata():
        h = hue(r, g, b)
        if (h < 0.3 or h > 5.7) \
           and saturation(r, g, b) > saturation_threshold \
           and value(r, g, b) > value_threshold:
            data.append((255, 255, 255))
        else:
            data.append((0, 0, 0))

    image.putdata(data)
    return image

def get_image():
    global img_camera, img_modified
    i = c.get_photo().get_response().resize((100,100), Img.ANTIALIAS)
    reduce_noise(i)

    img = PhotoImage(i)
    img_camera.configure(image=img)
    img_camera.img = img

    img_m = PhotoImage(filter_red(i))
    img_modified.configure(image=img_m)
    img_modified.img = img_m

    img_camera.after(100, get_image)

get_image()
root.mainloop()


