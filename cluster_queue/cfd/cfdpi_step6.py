##################################################################
#
# This program reads a .vtk file, renders it and creates images.
#
# Author: Dr Chennakesava Kadapa
# Date: 17-Oct-2018
#
##################################################################

# VTK pipeline
#
# source/reader --> filter --> mapper --> actor --> renderer --> renderWindow --> interactor
#
#

import os
import sys
import vtk

#from vtk import vtkUnstructuredGridReader


def generate_velocityvectorplots_from_vtk(filename):
    # Create the reader for the data.
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(filename)
    #reader.SetScalarsName("pressure")
    #reader.SetVectorsName("velocity")
    reader.ReadAllScalarsOff()
    reader.ReadAllVectorsOn()
    #reader.ReadVectorData("VECTORS",0)
    reader.Update()
    print("File read successfully ")

    print(reader.GetScalarsNameInFile(0))
    print(reader.GetVectorsNameInFile(0))

    output = reader.GetOutput()

    vec1 = output.GetPointData().GetArray("velocity")

    scalar_range = output.GetScalarRange()

    print("Number of points = ", output.GetNumberOfPoints())
    print("Number of cells = ",  output.GetNumberOfCells())

    print("Creating the arrow")

    # Create the arrow source
    arrow = vtk.vtkArrowSource()
    #arrow.SetTipResolution(1)
    #arrow.SetTipRadius(0.01)
    #arrow.SetTipLength(0.35)
    #arrow.SetShaftResolution(10)
    #arrow.SetShaftRadius(0.03)

    print("Creating the glyph")
    
    #points = output.GetPoints()

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(output.GetPoints())
    polydata.GetPointData().SetVectors(output.GetPointData().GetArray("velocity"))

    # Create the glyph for the Velocity field
    glyph3D = vtk.vtkGlyph3D()
    glyph3D.SetSourceConnection(arrow.GetOutputPort())
    glyph3D.SetInputData(polydata)
    glyph3D.SetVectorModeToUseVector()
    glyph3D.SetScaleModeToScaleByVector()
    glyph3D.OrientOn()
    glyph3D.SetScaleFactor(200.0)
    glyph3D.Update()

    print("ccccccccc")

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfColors(20)
    #lut.SetHueRange(0.0, 1.0);
    #lut.SetSaturationRange(0.0, 0.0);
    #lut.SetValueRange(0.0, 1.0);
    #lut.SetVectorModeToRGBColors()
    #lut.SetTableRange(output.GetPointData().GetArray("velocity").GetRange());
    #colorSeries.BuildLookupTable(lut, colorSeries.ORDINAL)
    lut.Build()

    lutr = vtk.vtkLookupTable()
    #lutr = ReverseLUT(lut)
    #lutr.Build()
    lutr.DeepCopy(lut)

    lutr.SetVectorModeToMagnitude()

    #lut.ApplyPreset('Cool to Warm', True)

    print("Creating the mapper")
    # Create the mapper
    #mapper = vtk.vtkDataSetMapper()
    #mapper.SetInput(glyph3D.GetOutput())
    #mapper.SetScalarRange(output.GetPointData().GetArray("velocity").GetRange());
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    #mapper.SetLookupTable(lutr)

    print("Creating the actor")
    # Create the actor
    actor = vtk.vtkActor()
    # Set the color for edges of the sphere
    actor.GetProperty().SetEdgeColor(0.0, 0.0, 0.0);
    actor.GetProperty().EdgeVisibilityOn();
    actor.SetMapper(mapper)
    
    print("Creating the renderer")
    # A renderer and render window
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)
    renderer.AddActor(actor)
    
    print("Creating the render window")
    renwin = vtk.vtkRenderWindow()
    renwin.SetSize(640, 480)
    renwin.AddRenderer(renderer)
    
    # An interactor
    #interactor = vtk.vtkRenderWindowInteractor()
    #interactor.SetRenderWindow(renwin)
    
    # Start
    #interactor.Initialize()
    #interactor.Start()
    
    renwin.Render()
    
    print("Writing images")
    # Create the image writer and write the image
    writer = vtk.vtkPNGWriter()
    windowto_image_filter = vtk.vtkWindowToImageFilter()
    windowto_image_filter.SetInput(renwin)
    #windowto_image_filter.SetScale(1)  # image quality
    windowto_image_filter.SetInputBufferTypeToRGB()
    # Read from the front buffer.
    windowto_image_filter.ReadFrontBufferOff()
    windowto_image_filter.Update()
    
    fname_data = filename.split(".")

    image_name_pres = fname_data[0]+"-velovectors.png"
    writer.SetFileName(image_name_pres)
    writer.SetInputConnection(windowto_image_filter.GetOutputPort())
    writer.Write()

    return
###############################################
###############################################

def create_prescontours_from_vtk(filename):
    # Create the reader for the data.
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(filename)
    #reader.SetScalarsName("pressure")
    #reader.SetVectorsName("velocity")
    reader.ReadAllScalarsOn()
    reader.ReadAllVectorsOn()
    reader.Update()
    print("File read successfully ")

    print(reader.GetScalarsNameInFile(0))
    print(reader.GetVectorsNameInFile(0))

    output = reader.GetOutput()

    #vec1 = output.GetPointData().GetVector("velocity")

    scalar_range = output.GetScalarRange()
    #vector_range = output.GetVectorRange()

    #npoints = output.GetNumberOfPoints()
    #ncells  = output.GetNumberOfCells()
    #print("Number of points = ", npoints)
    #print("Number of cells = ",  ncells)
    
    print("Creating the mapper")
    # Create the mapper
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(output)
    mapper.SetScalarModeToUsePointData()
    mapper.SetColorModeToMapScalars()
    #mapper.InterpolateScalarsBeforeMappingOn()
    #mapper.UseLookupTableScalarRangeOn()
    #print("GetArrayName=", mapper.GetArrayName())
    #print("GetArrayId=", mapper.GetArrayId())
    #mapper.SetArrayName("velocity")
    #mapper.SelectColorArray("velocity")
    #mapper.ColorByArrayComponent(reader.GetVectorsNameInFile(0),0)
    mapper.SetScalarRange(scalar_range)
    #mapper.SetScalarRange(output.GetPointData().GetArray("velocity").GetRange());
    
    print("Creating the actor")
    # Create the actor
    actor = vtk.vtkActor()
    # Set the color for edges of the sphere
    actor.GetProperty().SetEdgeColor(0.0, 0.0, 0.0);
    actor.GetProperty().EdgeVisibilityOn();
    actor.SetMapper(mapper)
    
    print("Creating the renderer")
    # A renderer and render window
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)
    renderer.AddActor(actor)
    
    print("Creating the render window")
    renwin = vtk.vtkRenderWindow()
    renwin.SetSize(640, 480)
    renwin.AddRenderer(renderer)
    
    # An interactor
    #interactor = vtk.vtkRenderWindowInteractor()
    #interactor.SetRenderWindow(renwin)
    
    # Start
    #interactor.Initialize()
    #interactor.Start()
    
    renwin.Render()
    
    print("Writing images")
    # Create the image writer and write the image
    writer = vtk.vtkPNGWriter()
    windowto_image_filter = vtk.vtkWindowToImageFilter()
    windowto_image_filter.SetInput(renwin)
    #windowto_image_filter.SetScale(1)  # image quality
    windowto_image_filter.SetInputBufferTypeToRGB()
    # Read from the front buffer.
    windowto_image_filter.ReadFrontBufferOff()
    windowto_image_filter.Update()
    
    fname_data = filename.split(".")

    image_name_pres = fname_data[0]+"-pres.png"
    writer.SetFileName(image_name_pres)
    writer.SetInputConnection(windowto_image_filter.GetOutputPort())
    writer.Write()

    return
##################################################
##################################################


# Generates the images for all the time steps requested
#
def generate_images_vtk(project_name, if_serial, num_timesteps):
    #print("Loading ", filename_prefix)

    print("The dir is: %s", os.getcwd())
    #dst="./" + project_name + "/mesh/"
    #dst="./mesh/"
    #os.chdir(dst)

    fname_temp="elmeroutput"

    if if_serial:
        for fnum in range(num_timesteps):
            filename = fname_temp + str(fnum+1) + ".vtk"
            print(filename)
            generate_velocityvectorplots_from_vtk(filename)
    else:
        filename_prefix=test.vtk
    
        for fnum in range(num_timesteps):
            filename = filename_prefix + "." + str(fnum-1)
            generate_velocityvectorplots_from_vtk(filename)

    return
##################################################
##################################################
