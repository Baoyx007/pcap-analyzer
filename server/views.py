#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: le4f.net

from server.func import *
from server.autogen import *
from flask import session, flash
import ChangeAtoB


# 主页
@app.route('/')
def index():
    return redirect(url_for('upload'), 302)


# 上传
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        CapFiles = []
        list_file(CapFiles)
        return render_template('upload.html', CapFiles=show_entries())
    elif request.method == 'POST':
        file = request.files['pcapfile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # 获取安全文件名，仅支持ascii字符
            filename = time.strftime('%Y%m%d_%H%M_', time.localtime(time.time())) + filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            size = os.path.getsize(UPLOAD_FOLDER + filename)
            result = (filename, 'PCAP', size)
            return simplejson.dumps({"files": [result]})
        else:
            pass


# 下载
@app.route('/download/<id>', methods=['GET'])
def download(id):
    pcapfile = get_pcap_entries(id)
    file = pcapfile[0]['filename']
    return send_file("../" + UPLOAD_FOLDER + file, attachment_filename=file, as_attachment=True)


# 分析包
@app.route('/analyze/<id>', methods=["GET"])
def analyze(id):
    id = int(id)
    pcapfile = get_pcap_entries(id)
    file = pcapfile[0]['filename']
    filter = request.args.get('filter')
    details = decode_capture_file(file, filter)
    pcapstat = get_statistics(file)
    ipsrc = get_ip_src(file)
    ipdst = get_ip_dst(file)
    dstport = get_port_dst(file)
    # 如生产环境需注意可能存在的XSS
    # pcapstat['mail'] = get_mail(file)
    session['TYPE'] = request.args.get('type', 'LBS')
    coord_info = request.args.to_dict()
    coord_info.pop('type')
    pcapstat['web'], marked = get_web(file, coord_info)
    # dns, pcapstat['dnstable'] = get_dns(file)
    pcapstat['ipsrc'] = dict(ipsrc)
    pcapstat['ipdst'] = dict(ipdst)
    pcapstat['dstport'] = dict(dstport)
    # pcapstat['dns'] = dict(dns)
    try:
        return render_template('analyze.html', pcapfile=pcapfile[0], details=details, pcapstat=pcapstat,
                               marked=marked)
    except:
        details = decode_capture_file(file)
        return render_template('analyze.html', pcapfile=pcapfile[0], details=details, pcapstat=pcapstat,
                               marked=marked)


# 获取包细节
@app.route('/packetdetail/<id>/<num>', methods=["GET"])
def packetdetail(id, num):
    id = int(id)
    pcapfile = get_pcap_entries(id)
    file = pcapfile[0]['filename']
    try:
        num = int(num)
        return get_packet_detail(file, num), 200
    except:
        return 0


# 产生中间配置1
@app.route('/autogen_1/<id>', methods=['POST', 'GET'])
def gen_config_1(id):
    if request.method == 'POST':
        frame_ids = request.get_json()['frameids']
        name = request.get_json()['name']
        businesss_type = request.get_json()['type']
        session['TYPE'] = businesss_type
        session['NAME'] = name
        id = int(id)
        # TODO 文件可能不存在
        file = get_pcap_entries(id)[0]['filename']
        ids_int = []
        for id in frame_ids.split(','):
            ids_int.append(int(id))

        session['MID_DATA_LIST'] = gen_config_1_json(file, ids_int, businesss_type, name)
        return render_template("gen_1.html")
    elif request.method == 'GET':
        mid_data = session['MID_DATA_LIST']
        return render_template('gen_1.html', DataList=mid_data)


# 下载autoge_1 的文件
@app.route('/autogen_1/down', methods=['GET'])
def autogen_1_down():
    ChangeAtoB.gen_1_xml(session['MID_DATA_LIST'])
    session.pop('MID_DATA_LIST', None)
    file = 'yj_hp_in.conf'
    return send_file("cfg/yj_hp_in.conf", attachment_filename=file, as_attachment=True)


# 读取pair中的请求对，返还给前端
@app.route('/autogen_2/<id>', methods=['GET'])
def gen_config_2(id):
    # 遍历所有产生的请求对
    # cookie 记录遍历到第几对
    pair = read_pair('server/pair')
    business_type = request.args.get('type', 'TXL')
    if business_type == 'LBS':
        xx_interface = get_interface('LBS')
        info = get_interface('INFO_TXL')
    elif business_type == 'TXL':
        xx_interface = get_interface('TXL')
        info = get_interface('INFO_TXL')
    return render_template('gen_2.html', frame=pair, xx_interface=xx_interface, info=info)


# data1 是site的 信息
# data2 是filter的信息
@app.route('/autogen_2_filter', methods=['POST', 'GET'])
def gen_config_2_filter():
    if request.method == 'POST':
        filters = []
        # 为每个filter创建一个pack
        for my_filter in request.get_json():
            # locations 中是regex树
            locs = my_filter['locations']
            locs_send = parse_locations(locs)
            print(locs_send)
            pack = pack_senddata(locs_send, my_filter['infoDef'], host=my_filter['host'].strip(), url=my_filter['url'],
                                 method=my_filter['method'])
            print(pack)
            filters.append(simplejson.loads(pack))
        # 另外一种解析方式 content.*?point.*?x":"([^"]*)
        # 占时可以选择不解析
        data1 = {"name": session['NAME'], "type": session['TYPE']}
        session['data1'] = data1
        session['data2'] = filters

        return 'success'
    elif request.method == 'GET':
        template = render_template('template.xml', data1=session['data1'], data2=session['data2'])
        session.pop('data1', None)
        session.pop('data2', None)

        response = make_response(template)
        response.headers['Content-Type'] = 'application/xml'
        return response


# 删除包
@app.route('/delete/<id>', methods=["POST"])
def delete_file(id):
    delids = id.split(',')
    db = get_connection()
    for delid in delids:
        try:
            delid = int(delid)
        except:
            print 'Notice : You are being attacked.'
            exit()
        cur = db.execute('select file from pcap where id = ' + str(delid) + ';')
        sql_exec('delete from pcap where id = ' + str(delid) + ';')
        os.remove(os.path.join(UPLOAD_FOLDER, cur.fetchall()[0][0]));
    return 'ok'


# 加载数据库
@app.before_request
def before_request():
    g.db = connect_db()


# 关闭数据库
@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/hello/<user>')
def hello(user):
    flash('a test')
    return redirect(url_for('index'))
