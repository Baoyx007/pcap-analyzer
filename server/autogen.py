# -*- coding: utf-8 -*-
import os
import pyshark
from server import UPLOAD_FOLDER
import re

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


def read_pair(path):
    pairs = [os.path.join(path, x) for x in os.listdir(path) if os.path.isfile(os.path.join('.', path, x))]
    pairs.sort(cmp=lambda x, y: cmp(os.path.getctime(x), os.path.getctime(y)), reverse=True)
    for i in range(0, len(pairs), 2):
        # print(pairs[i],pairs[i+1])
        frame = dict()
        with open(pairs[i]) as f:
            req = f.read().split('\n\n', 1)
            frame['req_h'] = req[0]
            if len(req) > 1:
                frame['req_b'] = req[1]
        with open(pairs[i + 1]) as f:
            res = f.read().split('\n\n', 1)
            frame['res_h'] = res[0]
            if len(res) > 1:
                frame['res_b'] = res[1]
    # p = re.compile(r'\n')
    # for k in frame.keys():
    #     frame[k] = p.sub(r'<br>', frame[k])
    return frame
