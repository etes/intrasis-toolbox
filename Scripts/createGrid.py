# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Intrasis
# Purpose:
#
# Author:      Ermias B. Tesfamariam
#
# Created:     12.11.2018
# Copyright:   (c) ermiasbt 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
from arcpy import env
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#global variables

class CreateGrid(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Grid"
        self.description = "Creates grid based on polygon extent"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        in_shp = arcpy.Parameter(
            displayName="Input Polygon feature",
            name="in_shp",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        in_shp.description = "Input Polygon ShapeFile"

        cell_size = arcpy.Parameter(
            displayName="Cell size (meters)",
            name="cell_size",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        cell_size.filter.type = "ValueList"
        cell_size.filter.list= ["0.5", "1"]
        cell_size.value = "0.5"

        # Output grid parameter
        out_grid = arcpy.Parameter(
            displayName="Output grid",
            name="out_grid",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")

        # Output grid center parameter
        out_grid_center = arcpy.Parameter(
            displayName="Output grid center points",
            name="out_grid_center",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        params = [in_shp, cell_size, out_grid, out_grid_center]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        env.outputCoordinateSystem = arcpy.SpatialReference("ETRS 1989 UTM Zone 32N")
        startX, startY, endX, endY = 0, 0, 0, 0
        in_shp = parameters[0].valueAsText
        cell_size = parameters[1].valueAsText
        out_grid = parameters[2].valueAsText
        out_grid_center = parameters[3].valueAsText
        messages.addMessage("Input ShapeFile: {0}".format(in_shp))
        messages.addMessage("Cell size: {0}".format(cell_size))
        desc = arcpy.Describe(in_shp)
        messages.addMessage("ShapeFile Spatial Reference: {0}".format(desc.spatialReference.name))
        if desc.spatialReference and desc.spatialReference.factoryCode == 25832:
            startX = int(desc.extent.XMin)
            startY = int(desc.extent.YMin)
            endX = int(desc.extent.XMax+1)
            endY = int(desc.extent.YMax+1)
        else:
            start = arcpy.PointGeometry(arcpy.Point(desc.extent.XMin,desc.extent.YMin),arcpy.SpatialReference(desc.spatialReference.factoryCode)).projectAs(arcpy.SpatialReference(25832))
            end = arcpy.PointGeometry(arcpy.Point(desc.extent.XMax,desc.extent.YMax),arcpy.SpatialReference(desc.spatialReference.factoryCode)).projectAs(arcpy.SpatialReference(25832))
            startX = int(start.getPart(0).X)
            startY = int(start.getPart(0).Y)
            endX = int(end.getPart(0).X+1)
            endY = int(end.getPart(0).Y+1)
        messages.addMessage("ShapeFile extent: {0}".format(desc.extent))

        arcpy.CreateFishnet_management(out_feature_class=out_grid, 
            origin_coord="{0} {1}".format(startX, startY), 
            y_axis_coord="{0} {1}".format(startX, startY + 10),
            cell_width=cell_size, 
            cell_height=cell_size, 
            corner_coord="{0} {1}".format(endX, endY), 
            labels="NO_LABELS", 
            template="#", 
            geometry_type="POLYGON")
        
        arcpy.AddField_management(in_table=out_grid, field_name="xmin", field_type="DOUBLE")
        arcpy.AddField_management(in_table=out_grid, field_name="ymin", field_type="DOUBLE")
        arcpy.AddField_management(in_table=out_grid, field_name="korrX", field_type="SHORT")
        arcpy.AddField_management(in_table=out_grid, field_name="korrY", field_type="SHORT")
        arcpy.AddField_management(in_table=out_grid, field_name="routeID", field_type="TEXT", field_length="20")
        arcpy.DeleteField_management(in_table=out_grid, drop_field="Id")
        arcpy.AddField_management(in_table=out_grid, field_name="Id", field_type="LONG", field_precision="6")
        arcpy.AddField_management(in_table=out_grid, field_name="GEOCODE", field_type="SHORT", field_precision="2")
        arcpy.AddField_management(in_table=out_grid, field_name="ObjectCode", field_type="TEXT", field_length="4")
        arcpy.AddField_management(in_table=out_grid, field_name="ObjectRef", field_type="TEXT", field_length="32")
        arcpy.AddField_management(in_table=out_grid, field_name="Z", field_type="FLOAT", field_precision="7", field_scale="3")
        shapeName = arcpy.Describe(out_grid).shapeFieldName
        cursor = arcpy.UpdateCursor(out_grid)
        for row in cursor:
            feat = row.getValue(shapeName)
            fid = row.getValue("FID")
            extent = feat.extent
            korrX = extent.YMin%1000
            korrY = extent.XMin%1000
            routeID = generate_routeID(korrX, korrY, cell_size)
            row.setValue("xmin", extent.XMin)
            row.setValue("ymin", extent.YMin)
            row.setValue("korrX", int(korrX))
            row.setValue("korrY", int(korrY))
            row.setValue("routeID", routeID)
            row.setValue("Id", fid + 101)
            row.setValue("GeoID", fid + 101)
            row.setValue("GEOCODE", 2)
            if cell_size == "1":
                row.setValue("ObjectCode", "RC")
            else:
                row.setValue("ObjectCode", "RB")
            cursor.updateRow(row)
        del row
        del cursor
        messages.addMessage("Created grid: {0}".format(out_grid))
        arcpy.FeatureToPoint_management(in_features=out_grid, out_feature_class=out_grid_center, point_location="INSIDE")
        messages.addMessage("Created grid center points: {0}".format(out_grid_center))
        arcpy.DeleteField_management(in_table=out_grid_center, drop_field="ORIG_FID")
        return
    
def generate_routeID(korrX, korrY, cell_size):
    if (cell_size == "1"):
        routeID = str(int(korrX)) +"x "+ str(int(korrY)) +"y"
    else:
        if ((korrX*10)% 10 == 0 and (korrY*10)% 10 == 0):
            Kvadrant = "SV"
        elif((korrX*10)% 10 == 0 and (korrY*10)% 10 == 5):
            Kvadrant = 'SØ'
        elif ((korrX*10)% 10 == 5 and (korrY*10)% 10 == 0):
            Kvadrant = "NV"
        elif ((korrX*10)% 10 == 5 and (korrY*10)% 10 == 5):
            Kvadrant = 'NØ'
        routeID = str(int(korrX)) +"x "+ str(int(korrY)) +"y "+ Kvadrant
    return routeID
