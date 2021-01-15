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
                            Utviklet av Kulturhistorisk museum

                            Excel-filen må ha disse kolonnene:
                            MetaId: for eksisterende MetaId i prosjektet
                            Name: for exsisterende Name i prosjektet
                            New_MetaId: for ny MetaId som skal erstatte det eksisterende MetaId
                            New_Name: for ny Name som skal erstatte det eksisterende Name
                            SubClass_ClassId: for ClassId til SubClass type
                            Type: for Type Class, SubClass, RelationType"""
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
        in_name = 'Name'
        in_new_metaid = 'New_MetaId'
        in_new_name = 'New_Name'
        in_classid = 'SubClass_ClassId'
        in_type = 'Type'

        psql = "C:\\Program Files\\PostgreSQL\\{0}\\bin\\psql.exe".format(
               pg_version)
        
        my_env["PGUSER"] = str(db_user)
        my_env["PGPASSWORD"] = str(db_password)
        my_env["PGDATABASE"] = str(db_name)

        log_file = os.path.join(
            log_folder, 'updateMetaId_' + str(db_name) + '.log')
        messages.addMessage('Log file will be saved to: {}'.format(log_file))
        return_messages = []
        
        update_metaid_functions = os.path.join(__location__, 'updateMetaId.sql')
        return_msg = runcmd([psql, '-f', update_metaid_functions], my_env)
        if return_msg[1]:
            messages.addMessage(
                "Update MetaId functions created: {}".format(return_msg[1]))
            return_messages.append(
                "Update MetaId functions created: {}".format(return_msg[1]))
        else:
            messages.addErrorMessage(
                "Update MetaId functions could not be created: {}".format(return_msg))
            return_messages.append(
                "Update MetaId functions could not be created: {}".format(return_msg))
            raise arcpy.ExecuteError

        fields = [in_metaid, in_name, in_new_metaid,
                  in_new_name, in_classid, in_type]
        updates_data = [dict(zip(fields, row))
                        for row in arcpy.da.SearchCursor(in_excel, fields)]

        subclasses = list(
            filter(lambda d: d[in_type] == 'SubClass', updates_data))

        if subclasses:
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
                        "SubClass MetaId update has run: {}".format(return_msg[1]))
                    return_messages.append(
                        "SubClass MetaId update has run: {}".format(return_msg[1]))
                else:
                    messages.addWarningMessage(
                        "SubClass MetaId update has not run: {}".format(return_msg))
                    return_messages.append(
                        "SubClass MetaId update has not run: {}".format(return_msg[1]))

        classes = list(filter(lambda d: d[in_type] == 'Class', updates_data))
        if classes:
            for cl in classes:
                if cl[in_new_name] and cl[in_new_name].strip():
                    update_sql = """SELECT * FROM update_class_metaid({0}, {1}, '{2}', '{3}')""".format(
                        str(int(cl[in_metaid])), str(int(cl[in_new_metaid])), cl[in_name], cl[in_new_name])
                else:
                    update_sql = """SELECT * FROM update_class_metaid({0}, {1}, '{2}', '{3}')""".format(
                        str(int(cl[in_metaid])), str(int(cl[in_new_metaid])), cl[in_name], cl[in_name])

                return_msg = runcmd([psql, '-Atc', update_sql], my_env)
                if return_msg[1]:
                    messages.addMessage(
                        "Class MetaId update has run: {}".format(return_msg[1]))
                    return_messages.append(
                        "Class MetaId update has run: {}".format(return_msg[1]))
                else:
                    messages.addWarningMessage(
                        "Class MetaId update has not run: {}".format(return_msg))
                    return_messages.append(
                        "Class MetaId update has not run: {}".format(return_msg[1]))

        # Filter RelationTypes
        relation_types = list(
            filter(lambda d: d[in_type] == 'RelationType', updates_data))

        if relation_types:
            for rt in relation_types:
                if rt[in_new_name] and rt[in_new_name].strip():
                    update_sql = """SELECT * FROM update_relationtype_metaid({0}, {1}, '{2}', '{3}')""".format(
                        str(int(rt[in_metaid])), str(int(rt[in_new_metaid])), rt[in_name], rt[in_new_name])
                else:
                    update_sql = """SELECT * FROM update_relationtype_metaid({0}, {1}, '{2}', '{3}')""".format(
                        str(int(rt[in_metaid])), str(int(rt[in_new_metaid])), rt[in_name], rt[in_name])

                return_msg = runcmd([psql, '-Atc', update_sql], my_env)
                if return_msg[1]:
                    messages.addMessage(
                        "RelationType MetaId update has run: {}".format(return_msg[1]))
                    return_messages.append(
                        "RelationType MetaId update has run: {}".format(return_msg[1]))
                else:
                    messages.addWarningMessage(
                        "RelationType MetaId update has not run: {}".format(return_msg))
                    return_messages.append(
                        "RelationType MetaId update has not run: {}".format(return_msg[1]))

        with open(log_file, "w") as f:
            for msg in return_messages:
                f.write('%s\n' % msg)
        return