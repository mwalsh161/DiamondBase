from PIL import Image
import os

def to_PNG(fname,delete=True):
    im = Image.open(fname)
    name,ext=os.path.splitext(fname)
    im.save(name+'.png')
    if delete:
        os.remove(fname)
    return name+'.png'

def check_and_replace_TIFF(fname,delete=True):
    ext = os.path.splitext(fname)[1]
    if ext.lower() in '.tiff':   #Gets '.tif and .tiff'
        try:
            fname = to_PNG(fname,delete)
        except:
            pass
    return fname

def thumbnail(fname,new_height=256,new_file_always=False):
    try:
        im = Image.open(fname)
        width,height = im.size
        if height > new_height:
            ratio = new_height/float(height)
            new_width = round(width*ratio)
            size=(new_height,new_width)
            im.thumbnail(size)
        if new_file_always or height > new_height:
            fname = os.path.splitext(fname)[0]
        im.save(fname+'-th.png')
    except:
        pass
