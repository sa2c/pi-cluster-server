#!/usr/bin/env python

from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, KeepInFrame

from brand import erdf_logo, scw_logo, get_styles


def build_document(output_filename,
                   top_left, top_right, bottom_left, bottom_right,
                   name, score):
    page = canvas.Canvas(
        output_filename,
        pagesize=(432, 288),
    )

    styles = get_styles()

    img_width = 136.417
    img_height = 102.313
    page.drawImage(
        top_left, 12, 178.5,
        width=img_width, height=img_height
    )
    page.drawImage(
        top_right, 152.917, 178.5,
        width=img_width, height=img_height
    )
    page.drawImage(
        bottom_left, 12, 60,
        width=img_width, height=img_height
    )
    page.drawImage(
        bottom_right, 152.917, 60,
        width=img_width, height=img_height
    )

    scw_logo.drawOn(page, 294, 107.587)
    erdf_logo.drawOn(page, 294, 7.184)

    name = KeepInFrame(
        283,
        41.3,
        [Paragraph(name, styles["Normal"])],
        mode='shrink'
    )
    name.wrapOn(page, 283, 46)
    name.drawOn(page, 12, 9)

    drag_caption = KeepInFrame(
        127.559,
        20.272,
        [Paragraph("Drag", styles["Heading2"])],
        mode='shrink'
    )
    drag_caption.wrapOn(page, 127.559, 20.272)
    drag_caption.drawOn(page, 297, 256.5)

    drag_figure = KeepInFrame(
        127.559,
        50.551,
        [Paragraph(f"{score}", styles["Heading2"])],
        mode='shrink'
    )
    drag_figure.wrapOn(page, 127.559, 50.551)
    drag_figure.drawOn(page, 297, 210)

    page.showPage()
    page.save()


if __name__ == "__main__":
    build_document(
        'test.pdf',
        'test1.jpg', 'test2.jpg', 'test3.jpg', 'test4.jpg',
        'Test User', 100
    )
