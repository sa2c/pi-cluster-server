#!/bin/env python
import os
from reportlab.platypus import Flowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import CMYKColor

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pdfrw import PdfReader, PdfDict
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl


black = CMYKColor(0, 0, 0, 1)


class PdfImage(Flowable):
    '''from http://stackoverflow.com/questions/31712386/
    loading-matplotlib-object-into-reportlab/'''
    def __init__(self, img_data, width=200, height=200):
        self.img_width = width
        self.img_height = height
        self.img_data = img_data

    def wrap(self, width, height):
        return self.img_width, self.img_height

    def drawOn(self, canv, x, y, _sW=0):
        if _sW > 0 and hasattr(self, 'hAlign'):
            a = self.hAlign
            if a in ('CENTER', 'CENTRE', TA_CENTER):
                x += 0.5*_sW
            elif a in ('RIGHT', TA_RIGHT):
                x += _sW
            elif a not in ('LEFT', TA_LEFT):
                raise ValueError("Bad hAlign value " + str(a))
        canv.saveState()
        img = self.img_data
        if isinstance(img, PdfDict):
            xscale = self.img_width / img.BBox[2]
            yscale = xscale
            self.img_height = img.BBox[3] * yscale

            canv.translate(x, y)
            canv.scale(xscale, yscale)
            canv.doForm(makerl(canv, img))
        else:
            canv.drawImage(img, x, y, self.img_width, self.img_height)
        canv.restoreState()


def get_logo(filename, target_width, width_in_file, height_in_file):
    '''width_in_file and height_in_file can be in any matching units'''
    width_in_file = 191.87
    height_in_file = 54.84
    s = target_width / width_in_file
    target_height = height_in_file * s

    logo = PdfImage(pagexobj(PdfReader(filename).pages[0]),
                    target_width, target_height)
    return logo

__package_dir = os.path.dirname(os.path.abspath(__file__))

def package_dir(name):
    return os.path.join(__package_dir, name)

erdf_logo = get_logo(package_dir('ERDF.pdf'), 127.56, 370, 269)
scw_logo = get_logo(package_dir('scw.pdf'), 126, 447, 303)
scw_bg = get_logo(package_dir('scw-bg.pdf'), 216, 84.86, 84.86)


def get_styles():
    pdfmetrics.registerFont(TTFont('Futura', package_dir('Futura-Book.ttf')))
    pdfmetrics.registerFont(TTFont('FuturaHeavy', package_dir('Futura-Heavy.ttf')))

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "Futura"
    styles["Normal"].fontSize = 72
    styles["Normal"].textColor = black
    styles["Normal"].leading = 76
    styles["Heading2"].fontName = "Futura"
    styles["Heading2"].fontSize = 200
    styles["Heading2"].textColor = black
    styles["Heading2"].leading = 220
    styles["Heading2"].alignment = TA_CENTER

    return styles
