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


class UpdateMetaIdName(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Update MetaId Name"
        self.description = """Oppdatere MetaId navn (navn til Class/SubClass/Relation...) 
                                i et Intrasis prosjekt basert på Musit malen.
                            Utviklet av Kulturhistorisk museum.
                            Excel-filen må ha disse kolonnene:
                            MetaId: for eksisterende MetaId i prosjektet
                            Name: for exsisterende Name i prosjektet
                            New_Name: for det nye Name som skal erstatte det eksisterende Name"""
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

        log_folder = arcpy.Parameter(
            displayName="Output Log Folder",
            name="log_folder",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        log_folder.filter.list = ["File System"]
        log_folder.description = "Folder to save output log file"

        params = [pg_version, db_user, db_password,
                  db_name, in_excel, log_folder]
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
        log_folder = parameters[5].valueAsText
        in_metaid = 'MetaId'
        in_old_name = 'Name'
        in_new_name = 'New_Name'

        psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(
               pg_version)

        my_env["PGUSER"] = str(db_user)
        my_env["PGPASSWORD"] = str(db_password)
        my_env["PGDATABASE"] = str(db_name)

        log_file = os.path.join(
            log_folder, 'updateMetaIdName_' + str(db_name) + '.log')
        messages.addMessage('Log file will be saved to: {}'.format(log_file))
        return_messages = []

        fields = [in_metaid, in_old_name, in_new_name]
        updates_data = [(str(int(row[0])), row[1], row[2])
                        for row in arcpy.da.SearchCursor(in_excel, fields)]
        updates_data_str = ", ".join(
            ["('" + "', '".join(row) + "')" for row in updates_data])

        select_sql = """SELECT "MetaId", "Name" FROM public."Definition", 
            (VALUES {}) AS update_payload (metaid, old_name, new_name)
            WHERE "MetaId" = update_payload.metaid::INTEGER AND "Name" = update_payload.old_name""".format(updates_data_str)
        fd, filepath = tempfile.mkstemp(suffix=".sql")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(select_sql)
            return_msg = runcmd([psql, '-f', filepath], my_env)
            if return_msg[1]:
                messages.addMessage(
                    "MetaId Names update that will run: {}".format(return_msg[1]))
                return_messages.append(
                    "MetaId Names update that will run: {}".format(return_msg[1]))
            else:
                messages.addWarningMessage(
                    "ERROR: MetaId Names select could not run: {}".format(return_msg))
                return_messages.append(
                    "ERROR: MetaId Names select could not run: {}".format(return_msg))
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
                    "MetaId Names update has run: {}".format(return_msg[1]))
                return_messages.append(
                    "MetaId Names update has run: {}".format(return_msg[1]))
            else:
                messages.addWarningMessage(
                    "ERROR: MetaId Names update could not run: {}".format(return_msg))
                return_messages.append(
                    "ERROR: MetaId Names update could not run: {}".format(return_msg))
        finally:
            os.unlink(updater_filepath)

        with open(log_file, "w") as f:
            for msg in return_messages:
                f.write('%s\n' % msg)
        return