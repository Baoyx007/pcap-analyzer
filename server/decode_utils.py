# -*- coding: utf-8 -*-
__author__ = 'PCPC'
import zlib


def decode_gzip(data):
    decode_data = zlib.decompress(data, 16 | zlib.MAX_WBITS)
