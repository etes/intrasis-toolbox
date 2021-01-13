# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Intrasis
# Purpose:
#
# Author:      Ermias B. Tesfamariam
#
# Created:     12.11.2020
# Copyright:   (c) ermiasbt 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
import os
import sys
import subprocess
import tempfile
reload(sys)
sys.setdefaultencoding("utf-8")

#global variables
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
#set environment variables for Postgresql
my_env = os.environ.copy()
my_env["PGHOST"] = 'localhost'
my_env["PGPORT"] = '5432'


def runcmd(cmd, env):
        """
        A generic subprocess.Popen function to run a command which suppresses consoles on Windows
        """
        if os.name == 'nt':
            #Windows starts up a console when a subprocess is run from a non-console
            #app like pythonw unless we pass it a flag that says not to...
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= 1
        else:
               startupinfo = None
        proc = subprocess.Popen(cmd, env=env, startupinfo=startupinfo,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        if os.name == 'nt':
              proc.stdin.close()
        stdout, stderr = proc.communicate()
        exit_code = proc.wait()
        return exit_code, stdout, stderr


class UpdateMetaId(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update MetaId"
        self.description = """Oppdatere MetaId til Class/SubClass/RelationType... 
                                i et Intrasis prosjekt basert på input tabell.
                            Utviklet av Kulturhistorisk museum"""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        pg_version = arcpy.Parameter(
            displayName="Select PostgreSQL version",
            name="pg_version",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        pg_version.filter.type = "ValueList"
        pg_version.filter.list = ["12", "11", "10",
                                  "9.6", "9.5", "9.4", "9.3", "9.2", "9.1", "9"]
        pg_version.value = "9.6"

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
        db_name.parameterDependencies = [
            pg_version.name, db_user.name, db_password.name]

        in_excel = arcpy.Parameter(
            displayName="Input Excel",
            name="in_excel",
            datatype="DETable",
            parameterType="Required",
            direction="Input")
        in_excel.description = "Excel file containing the fields metaid, old name and new name"

        in_metaid = arcpy.Parameter(
            displayName="Old MetaId Field",
            name="in_metaid",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_metaid.parameterDependencies = [in_excel.name]
        in_metaid.description = "Input old MetaId field"
        in_metaid.value = "MetaId"

        in_name = arcpy.Parameter(
            displayName="Old Name Field",
            name="in_name",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_name.parameterDependencies = [in_excel.name]
        in_name.description = "Input old name field"
        in_name.value = "Name"

        in_new_metaid = arcpy.Parameter(
            displayName="New MetaId Field",
            name="in_new_metaid",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_new_metaid.parameterDependencies = [in_excel.name]
        in_new_metaid.description = "Input New MetaId field"
        in_new_metaid.value = "New_MetaId"

        in_new_name = arcpy.Parameter(
            displayName="New Name Field",
            name="in_new_name",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_new_name.parameterDependencies = [in_excel.name]
        in_new_name.description = "Input new name field"
        in_new_name.value = "New_Name"

        in_classid = arcpy.Parameter(
            displayName="ClassId Field",
            name="in_classid",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_classid.parameterDependencies = [in_excel.name]
        in_classid.description = "Input ClassId field"
        in_classid.value = "SubClass_ClassId"

        in_type = arcpy.Parameter(
            displayName="Type Field",
            name="in_type",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_type.parameterDependencies = [in_excel.name]
        in_type.description = "Input Type field"
        in_type.value = "Type"

        params = [pg_version, db_user, db_password, db_name,
                  in_excel, in_metaid, in_name, in_new_metaid, in_new_name, in_classid, in_type]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[0].valueAsText:
            pg_version = parameters[0].valueAsText
            psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(
                   pg_version)
            if not os.path.isfile(psql):
                self.params[0].setErrorMessage("PostgreSQL version is invalid \
                    Please select the correct PostgreSQL version.")

        if parameters[1].value and parameters[2].value:
            my_env["PGUSER"] = str(parameters[1].value)
            my_env["PGPASSWORD"] = str(parameters[2].value)
            args = [psql, '-Atc', 'select datname from pg_database']
            return_message = runcmd(args, my_env)
            parameters[3].filter.list = return_message[1].split()
        else:
            parameters[3].filter.list = []

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #global psql
        pg_version = parameters[0].valueAsText
        db_user = parameters[1].valueAsText
        db_password = parameters[2].valueAsText
        db_name = parameters[3].valueAsText
        in_excel = parameters[4].valueAsText
        in_metaid = parameters[5].valueAsText
        in_name = parameters[6].valueAsText
        in_new_metaid = parameters[7].valueAsText
        in_new_name = parameters[8].valueAsText
        in_classid = parameters[9].valueAsText
        in_type = parameters[10].valueAsText

        psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(
               pg_version)

        my_env["PGUSER"] = str(db_user)
        my_env["PGPASSWORD"] = str(db_password)
        my_env["PGDATABASE"] = str(db_name)
        
        update_metaid_functions = os.path.join(__location__, 'updateMetaId.sql')
        return_msg = runcmd([psql, '-f', update_metaid_functions], my_env)
        if return_msg[1]:
            messages.addMessage(
                "Update MetaId functions created: {}".format(return_msg[1]))
        else:
            messages.addErrorMessage(
                "Update MetaId functions could not be created: {}".format(return_msg))
            raise arcpy.ExecuteError

        fields = [in_metaid, in_name, in_new_metaid, in_new_name, in_classid, in_type]
        updates_data = [dict(zip(fields, row))
                         for row in arcpy.da.SearchCursor(in_excel, fields)]

        subclasses = list(filter(lambda d: d[in_type] == 'SubClass', updates_data))

        if subclasses:
            return_messages = []
            for sc in subclasses:
                if sc[in_new_name] and sc[in_new_name].strip():
                    update_sql = """SELECT * FROM update_subclass_metaid({0}, {1}, {2}, '{3}', '{4}')""".format(
                        str(int(sc[in_metaid])), str(int(sc[in_classid])),
                        str(int(sc[in_new_metaid])), sc[in_name], sc[in_new_name])
                else:
                    update_sql = """SELECT * FROM update_subclass_metaid({0}, {1}, {2}, '{3}', '{4}')""".format(
                        str(int(sc[in_metaid])), str(int(sc[in_classid])),
                        str(int(sc[in_new_metaid])), sc[in_name], sc[in_name])

                return_msg = runcmd([psql, '-Atc', update_sql], my_env)
                if return_msg[1]:
                    messages.addMessage(
                        "MetaId ble oppdatert: {}".format(return_msg[1]))
                    return_messages.append("Success: {}".format(return_msg[1]))
                else:
                    messages.addWarningMessage(
                        "Ingen MetaId ble oppdatert: {}".format(return_msg))
                    return_messages.append("Error: {}".format(return_msg[1]))
        
        classes = list(filter(lambda d: d[in_type] == 'Class', updates_data))
        relation_types = list(
            filter(lambda d: d[in_type] == 'RelationType', updates_data))

        return
