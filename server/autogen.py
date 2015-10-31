# -*- coding: utf-8 -*-
import os
import pyshark
import json
from server import UPLOAD_FOLDER
import flask

__author__ = 'PCPC'


def gen_config_1_json(pcapfile, frame_ids):
    cap = pyshark.FileCapture(os.path.join(UPLOAD_FOLDER, pcapfile))
    data_list = []
    for id in frame_ids:
        package = cap[id]
        if not hasattr(package,'http'):
            continue
        if hasattr(package.http,'request') :
            mid_data = dict({'TYPE':'LBS'})
            mid_data['HOST'] = package.http.host
            mid_data['URL'] = package.http.request_uri
            mid_data['METHOD'] = package.http.request_method
            mid_data['NAME'] = package.http.host
        elif hasattr(package.http,'response'):
            package.http.prev_request_in

        data_list.append(mid_data)

    from flask import make_response
    import json
    res = make_response(json.dumps(data_list))
    return res
