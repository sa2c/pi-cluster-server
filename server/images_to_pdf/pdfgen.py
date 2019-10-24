from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, KeepInFrame
from reportlab.lib.utils import ImageReader

from PIL import Image
from io import BytesIO
import numpy as np
from subprocess import call
from images_to_pdf.brand import erdf_logo, scw_logo, scw_bg, get_styles
import model


def convert_to_reportlab(im):
    # Convert a PIL image for reportlab
    if type(im) is Image.Image:
        im_data = BytesIO()

        if im.mode == 'RGBA':
            im = im.convert('RGB')

        im.save(im_data, format='png')
        im_data.seek(0)

        return ImageReader(im_data)

    elif type(im) == np.ndarray:
        im = Image.fromarray(im[:, :, ::-1])
        return convert_to_reportlab(im)

    else:
        return None


def build_sim_document(sim_id, images):
    """
    Builds the pdf postcard for the document
    """
    sim = model.get_simulation(sim_id)
    filename = model.sim_filepath(sim_id, 'postcard.pdf')

    name = sim['name']
    drag = sim['drag']

    build_document(filename, images, name, drag)


def build_document(filename, images, name, drag):
    """
    Takes a filename, a list of four PIL Image objects, a name and a value of drag
    and generates a PDF document.
    """

    page = canvas.Canvas(
        filename,
        pagesize=(432, 288),
    )

    rl_images = [convert_to_reportlab(image) for image in images]

    styles = get_styles()

    scw_bg.drawOn(page, 0, 0)

    img_width = 136.417
    img_height = 102.313

    x = [12, 151, 12, 151]
    y = [178.5, 178.5, 60, 60]

    for args in zip(rl_images, x, y):
        page.drawImage(*args, width=img_width, height=img_height)

    scw_logo.drawOn(page, 290, 107)
    erdf_logo.drawOn(page, 290, 7.184)

    name = KeepInFrame(275,
                       41.3, [Paragraph(name, styles["Normal"])],
                       mode='shrink')
    name.wrapOn(page, 275, 46)
    name.drawOn(page, 20, 9)

    drag_caption = KeepInFrame(127.559,
                               20.272, [Paragraph("Drag", styles["Heading2"])],
                               mode='shrink')
    drag_caption.wrapOn(page, 127.559, 20.272)
    drag_caption.drawOn(page, 289, 256.5)

    drag_figure = KeepInFrame(127.559,
                              50.551,
                              [Paragraph(f"{drag:.1f}", styles["Heading2"])],
                              mode='shrink')
    drag_figure.wrapOn(page, 127.559, 50.551)
    drag_figure.drawOn(page, 289, 210)

    page.showPage()
    page.save()

    print("pdf file saved to {filename}".format(filename=filename))
