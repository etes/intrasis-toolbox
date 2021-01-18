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

intrasisScripts = os.path.join(os.path.dirname(__file__), "Scripts")
sys.path.append(intrasisScripts)

from updatesubclass import UpdateSubClass
from checkCoordSys import CheckCoordSys
from updateCoordSys import UpdateCoordSys
from updateMetaIdName import UpdateMetaIdName
from updateMetaId import UpdateMetaId
from createGrid import CreateGrid

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Intrasis"
        self.description = "A set of tools for managing and updating an Intrasis project"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [UpdateSubClass, CreateGrid, CheckCoordSys, UpdateCoordSys, UpdateMetaIdName, UpdateMetaId]

