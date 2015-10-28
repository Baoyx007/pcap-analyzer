# -*- coding: utf-8 -*-
import os
import pyshark
from server import UPLOAD_FOLDER

__author__ = 'PCPC'


def gen_config_1_json(pcapfile, num):
    cap = pyshark.FileCapture(os.path.join(UPLOAD_FOLDER, pcapfile))
