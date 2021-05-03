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
import os
import sys
import subprocess
import csv
from utils import runcmd

reload(sys)
sys.setdefaultencoding("utf-8")

#global variables
#Path to psql """
psql = 'C:\\Program Files\\PostgreSQL\\9.6\\bin\\psql.exe'
#psql = 'C:\\Program Files\\PostgreSQL\\9.2\\bin\\psql.exe'
#set environment variables for psql
my_env = os.environ.copy()
my_env["PATH"] = "C:\\Program Files\\PostgreSQL\\9.6\\bin" + os.pathsep + my_env["PATH"]
my_env["PGHOST"] = 'localhost'
my_env["PGPORT"] = '5432'

class UpdateSubClass(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update SubClass"
        self.description = "Endres Arkeologisk objekt SubClasser til Avskrevet"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        in_csv = arcpy.Parameter(
            displayName="Input CSV",
            name="in_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        in_csv.filter.list = ['txt', 'csv']
        in_csv.description = "Input csv file containing IntrasisIds"

        db_user = arcpy.Parameter(
            displayName="Database user",
            name="db_user",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        db_user.value = "postgres"

        db_password = arcpy.Parameter(
            displayName="Database password",
            name="db_password",
            datatype="GPStringHidden",
            parameterType="Required",
            direction="Input")

        db_name = arcpy.Parameter(
            displayName="Database name",
            name="db_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        db_name.parameterDependencies = [db_user.name, db_password.name]

        subClass = arcpy.Parameter(
            displayName="New SubClass",
            name="subClass",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        subClass.filter.type = "ValueList"
        subClass.filter.list= ["Avskrevet"]
        subClass.value = "Avskrevet"

        params = [in_csv, db_user, db_password, db_name, subClass]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        global psql
        if parameters[1].value and parameters[2].value:
            my_env["PGUSER"] = str(parameters[1].value)
            my_env["PGPASSWORD"] = str(parameters[2].value)
            args = [psql, '-Atc', 'select datname from pg_database']
            returnMessage = runcmd(args, my_env)
            parameters[3].filter.list = returnMessage[1].split()
        else:
            parameters[3].filter.list = []
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        global psql
        in_csv = parameters[0].valueAsText
        db_user = parameters[1].valueAsText
        db_password = parameters[2].valueAsText
        db_name = parameters[3].valueAsText

        table_dict = list(csv.DictReader(open(in_csv), delimiter=';'))
        IntrasisIds = [int(row['IntrasisId']) for row in table_dict]

        update_expression = '''UPDATE "Object" obj SET "SubClassId" = 10009
                    WHERE obj."PublicId" in {};
        '''.format(tuple(IntrasisIds))

        my_env["PGUSER"] = str(db_user)
        my_env["PGPASSWORD"] = str(db_password)
        my_env["PGDATABASE"]= str(db_name)

        args = [psql, '-Atc', update_expression]
        returnMessage = runcmd(args, my_env)
        messages.addMessage("Updated rows: {0}".format(returnMessage[1]))
        return


# The map is not the territory