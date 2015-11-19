# -*- coding: utf-8 -*-
import os
import pyshark
from server import UPLOAD_FOLDER
import simplejson as json

__author__ = 'PCPC'


class RegexTree:
    def __init__(self, name, value=''):
        self.name = name
        self.value = value
        self.childrens = []

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.name+':'+self.value) + "\n"
        for child in self.childrens:
            ret += child.__repr__(level + 1)
        return ret


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
    # 将所有的中间pair按时间顺序排序
    # 这样相邻两个pair为一个请求对
    pairs = [os.path.join(path, x) for x in os.listdir(path) if os.path.isfile(os.path.join('.', path, x))]
    pairs.sort(cmp=lambda x, y: cmp(os.path.getctime(x), os.path.getctime(y)), reverse=True)
    # 每个frame分为4个部分request_head,request_body,response_head,response_body
    frame_list = list()
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
        frame_list.append(frame)
    # p = re.compile(r'\n')
    # for k in frame.keys():
    #     frame[k] = p.sub(r'<br>', frame[k])
    return frame_list


def get_interface(business):
    with open('server/conf/interface.json') as f:
        xx_interface = json.load(f)
        return xx_interface[business]


# 将一条叶子节点到root的路径合并到树中
def mergeTree(total_tree, single_root):
    if total_tree is None:
        return single_root
    # 先判断他们是不是一个树
    if total_tree.name != single_root.name:
        return total_tree.append(single_root)
    # pt比p大一层
    p = single_root.childrens[0]
    pt = total_tree
    # 每层节点对比
    while p is not None or pt is not None:
        i = 0
        for node in pt.childrens:
            if p.name == node.name:
                break
            i += 1
        if i >= len(pt.childrens):
            pt.childrens.append(p)
            return total_tree
        p = p.childrens[0]
        pt = pt.childrens[i]
    if pt is None and p is not None:
        pt.childrens.append(p)
    return total_tree


def parse_locations(locs):
    locs = json.loads(locs)
    # 遍历location中的response。。requestBody
    loc_tree = []
    for loc in locs:
        # 遍历每一个infoname
        total_tree = None
        for info in locs[loc]:
            traces = info['value'].split('~')
            # 对每一个infoname的value 建立一个单孩子的树
            p = None
            for trace in traces:
                node = RegexTree(trace)
                if p:
                    p.childrens.append(node)
                    p = p.childrens[0]
                else:
                    root = node
                    p = root

            p.value = info['infoname'] + '~' + info['regex']
            total_tree = mergeTree(total_tree, root)
        loc_tree.append(total_tree)
    return total_tree
