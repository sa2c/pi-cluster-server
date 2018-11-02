#!/usr/bin/env python

from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, KeepInFrame
from reportlab.lib.utils import ImageReader

from PySide2.QtCore import QRunnable
from PIL import Image
from io import BytesIO
from numpy import uint8
from subprocess import call

from brand import erdf_logo, scw_logo, scw_bg, get_styles


def build_document(output_filename,
                   top_left, top_right, bottom_left, bottom_right,
                   name, score):
    page = canvas.Canvas(
        output_filename,
        pagesize=(432, 288),
    )

    styles = get_styles()

    scw_bg.drawOn(page, 0, 0)

    img_width = 136.417
    img_height = 102.313
    page.drawImage(
        top_left, 12, 178.5,
        width=img_width, height=img_height
    )
    page.drawImage(
        top_right, 151, 178.5,
        width=img_width, height=img_height
    )
    page.drawImage(
        bottom_left, 12, 60,
        width=img_width, height=img_height
    )
    page.drawImage(
        bottom_right, 151, 60,
        width=img_width, height=img_height
    )

    scw_logo.drawOn(page, 290, 107)
    erdf_logo.drawOn(page, 290, 7.184)

    name = KeepInFrame(
        275,
        41.3,
        [Paragraph(name, styles["Normal"])],
        mode='shrink'
    )
    name.wrapOn(page, 275, 46)
    name.drawOn(page, 20, 9)

    drag_caption = KeepInFrame(
        127.559,
        20.272,
        [Paragraph("Drag", styles["Heading2"])],
        mode='shrink'
    )
    drag_caption.wrapOn(page, 127.559, 20.272)
    drag_caption.drawOn(page, 289, 256.5)

    drag_figure = KeepInFrame(
        127.559,
        50.551,
        [Paragraph(f"{score}", styles["Heading2"])],
        mode='shrink'
    )
    drag_figure.wrapOn(page, 127.559, 50.551)
    drag_figure.drawOn(page, 289, 210)

    page.showPage()
    page.save()


class PDFGenerator(QRunnable):
    def __init__(self,
                 output_filename,
                 image_array_top_left, image_array_top_right,
                 image_array_bottom_left, image_array_bottom_right,
                 visitor_name, visitor_score):
        self.output_filename = output_filename
        self.image_arrays = [
            image_array_top_left,
            image_array_top_right,
            image_array_bottom_left,
            image_array_bottom_right
        ]
        self.visitor_name = visitor_name
        self.visitor_score = visitor_score

    def run(self):
        images = []
        for image_array in self.image_arrays:
            image_io = BytesIO()
            Image.fromarray(uint8(image_array)).save(image_io, format='JPEG')
            image_io.seek(0)
            images.append(ImageReader(image_io))

        build_document(
            self.output_filename,
            *images,
            self.visitor_name,
            self.visitor_score
        )
        call(['lpr', '-o', 'landscape', self.output_filename])


if __name__ == "__main__":
    # build_document(
    #     'test.pdf',
    #     'test1.jpg', 'test2.jpg', 'test3.jpg', 'test4.jpg',
    #     'Test User', 100
    # )
    import matplotlib.pyplot as plt

    image1 = plt.imread('test1.jpg')
    image2 = plt.imread('test2.jpg')
    image3 = plt.imread('test3.jpg')
    image4 = plt.imread('test4.jpg')

    generator = PDFGenerator('test_pil.pdf',
                             image1, image2, image3, image4,
                             'Test user with PIL', 69)
#    import pdb; pdb.set_trace()
    generator.run()
