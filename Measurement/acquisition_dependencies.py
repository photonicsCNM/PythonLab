#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 18:05:29 2018

@author: nils
"""


# 3rd party; shipped with conda
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import os
import subprocess
import traceback
import json
import warnings

# Own stuff
from modules import GPIO
from modules.MyMeasurement import Measurement

def jdefault(o):
    return o.__dict__

def flush(params):
    with open(saving_to +'acquisition.params', 'w') as params_bak:
        json.dump(params, params_bak, indent=4, default=jdefault)

