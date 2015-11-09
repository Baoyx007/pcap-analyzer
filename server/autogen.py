# -*- coding: utf-8 -*-
import os
import pyshark
from server import UPLOAD_FOLDER

__author__ = 'PCPC'


def gen_config_1_json(pcapfile, frame_ids):
    cap = pyshark.FileCapture(os.path.join(UPLOAD_FOLDER, pcapfile))
    data_list = []
    for id in frame_ids:
        package = cap[id - 1]
        # 过滤非http层
        if not hasattr(package, 'http'):
            continue
        # 分为req和response
        if hasattr(package.http, 'request'):
            # TODO 以后要增加TXL
            mid_data = extract_mid_data(package)
        else:
            if hasattr(package.http, 'request_in'):
                req_id = int(package.http.request_in)
            else:
                req_id = int(package.http.prev_request_in)
            mid_data = extract_mid_data(cap[req_id - 1])

        data_list.append(mid_data)

    # import json
    # return json.dumps(data_list)
    return data_list


def extract_mid_data(package):
    mid_data = dict(TYPE='LBS')
    mid_data['HOST'] = package.http.host
    mid_data['URL'] = package.http.request_uri
    mid_data['METHOD'] = package.http.request_method
    mid_data['NAME'] = package.http.host
    return mid_data
