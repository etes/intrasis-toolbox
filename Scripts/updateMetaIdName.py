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
import tempfile
reload(sys)
sys.setdefaultencoding("utf-8")

#global variables
#Path to psql """
#psql = 'C:\\Program Files\\PostgreSQL\\9.6\\bin\\psql.exe'
#set environment variables for Postgresql
my_env = os.environ.copy()
#my_env["PATH"] = "C:\\Program Files\\PostgreSQL\\9.6\\bin" + os.pathsep + my_env["PATH"]
my_env["PGHOST"] = 'localhost'
my_env["PGPORT"] = '5432'


def runcmd(cmd, env):  
        """ 
        A generic subprocess.Popen function to run a command which suppresses consoles on Windows
        """  
        if os.name=='nt':  
            #Windows starts up a console when a subprocess is run from a non-console  
            #app like pythonw unless we pass it a flag that says not to...  
            startupinfo=subprocess.STARTUPINFO()  
            startupinfo.dwFlags |= 1              
        else:startupinfo=None  
        proc=subprocess.Popen(cmd, env=env, startupinfo=startupinfo,  
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,  
                            stdin=subprocess.PIPE)  
        if os.name=='nt':proc.stdin.close()  
        stdout,stderr=proc.communicate()  
        exit_code=proc.wait()  
        return exit_code, stdout, stderr


class UpdateMetaIdName(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update MetaId Name"
        self.description = """Oppdatere MetaId navn (navn til Class/SubClass/Relation...) 
                                i et Intrasis prosjekt basert på Musit malen.
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
        pg_version.filter.list= ["12", "11", "10", "9.6", "9.5", "9.4", "9.3", "9.2", "9.1", "9"]
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
        db_name.parameterDependencies = [pg_version.name, db_user.name, db_password.name]

        in_excel = arcpy.Parameter(
            displayName="Input Excel",
            name="in_excel",
            datatype="DETable",
            parameterType="Required",
            direction="Input")
        in_excel.description = "Excel file containing the fields metaid, old name and new name"

        in_metaid = arcpy.Parameter(
            displayName="MetaId Field",
            name="in_metaid",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_metaid.parameterDependencies = [in_excel.name]
        in_metaid.description = "Input MetaId field"

        in_old_name = arcpy.Parameter(
            displayName="Old Name Field",
            name="in_old_name",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_old_name.parameterDependencies = [in_excel.name]
        in_old_name.description = "Input old name field"
        
        in_new_name = arcpy.Parameter(
            displayName="New Name Field",
            name="in_new_name",
            datatype="Field",
            parameterType="Required",
            direction="Input")
        in_new_name.parameterDependencies = [in_excel.name]
        in_new_name.description = "Input new name field"
                
        params = [pg_version, db_user, db_password, db_name, in_excel, in_metaid, in_old_name, in_new_name]
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
            psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(pg_version)
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
        in_old_name = parameters[6].valueAsText
        in_new_name = parameters[7].valueAsText

        psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(pg_version)
        
        my_env["PGUSER"] = str(db_user)
        my_env["PGPASSWORD"] = str(db_password)
        my_env["PGDATABASE"]= str(db_name)
        
        fields = [in_metaid, in_old_name, in_new_name]
        updates_data = [(str(int(row[0])), row[1], row[2]) for row in arcpy.da.SearchCursor(in_excel, fields)]
        updates_data_str = ", ".join(["('" + "', '".join(row) + "')" for row in updates_data])
        messages.addMessage(
            "MetaId, old_name, new_name : {}".format(updates_data_str))
                
        select_sql = """SELECT "MetaId", "Name" FROM public."Definition", 
            (VALUES {}) AS update_payload (metaid, old_name, new_name)
            WHERE "MetaId" = update_payload.metaid::INTEGER AND "Name" = update_payload.old_name""".format(updates_data_str)
        fd, filepath = tempfile.mkstemp(suffix = ".sql")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(select_sql)
            return_msg = runcmd([psql, '-f', filepath], my_env)
            messages.addMessage(
                "MetaId navn som skal oppdateres: {}".format(return_msg[1]))
        finally:
            os.unlink(filepath)
        
        update_sql = """UPDATE public."Definition"
            SET "Name" = update_payload.new_name
            FROM (VALUES {}) AS update_payload (metaid, old_name, new_name)
            WHERE "MetaId" = update_payload.metaid::INTEGER AND "Name" = update_payload.old_name""".format(updates_data_str)
        
        updater_file, updater_filepath = tempfile.mkstemp(suffix=".sql")
        try:
            with os.fdopen(updater_file, "w") as f:
                f.write(update_sql)
            return_msg = runcmd([psql, '-f', updater_filepath], my_env)
            if return_msg[1]:
                messages.addMessage(
                    "{} MetaId navn ble oppdatert".format(return_msg[1]))
            else:
                messages.addWarningMessage(
                    "Ingen navn til MetaId ble oppdatert: {}".format(return_msg))
        finally:
            os.unlink(updater_filepath)
        
        return

