#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup  
import py2exe

options = {"py2exe":  
            {   "compressed": 1,
                "optimize": 2,
                "includes":"os,sys",
                "bundle_files": 1
            }
          }
setup(
    version = "0.3.1",
    description = "Send google reader to your kindle",
    name = "kindlereader",
    options = options,
    zipfile=None,
    console=[{"script": "kindlereader.py"}],
 )