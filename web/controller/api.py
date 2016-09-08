# -*- coding:utf-8 -*-
__author__ = 'Ulric Qin'
from web import app
from flask import request, jsonify, render_template
from frame.api import uic
from frame.store import db
from web.service import group_service
from web.model.template import Template
from web.model.action import Action
from web.model.host_group import HostGroup
from web.model.host import Host
from web.model.group_host import GroupHost
from web.model.expression import Expression
from web.model.strategy import Strategy
from frame import utils
from frame.config import MARATHON_ADDRESS

@app.route('/api/version')
def api_version():
    return '2.0.0'


@app.route('/api/health')
def api_health():
    return 'ok'


@app.route('/api/uic/group')
def api_query_uic_group():
    q = request.args.get('query', '').strip()
    limit = int(request.args.get('limit', '10'))
    return jsonify(data=uic.query_group(q, limit))

@app.route('/api/marathon',methods=["POST"])
def api_marathon_health():
    marathon_stats = request.get_json()

    if marathon_stats["eventType"] == "deployment_success":
        action_type = marathon_stats["plan"]["steps"][-1]["actions"][-1]["type"]
        app = marathon_stats["plan"]["steps"][-1]["actions"][-1]["app"].lstrip("/")
        if action_type == "StopApplication":
            grp_id = HostGroup.query_grp_id(app)
            if grp_id > 0:
                group_service.delete_group(grp_id)
        else:
            grp_id = HostGroup.create(app,"root",1)
            if grp_id < 0:
                grp_id = HostGroup.query_grp_id(app)
                if grp_id < 0:
                    return 'grp_name no exist'
            import requests,json
            r = requests.get(MARATHON_ADDRESS+"/v2/apps/"+app)
            app_info = json.loads(r.text)
            marathon_hosts = []
            for i in app_info["app"]["tasks"]:
                marathon_hosts.append(i["host"])
            vs,_ = Host.query(1, 10000000, '', '0', grp_id)
            of_names = [v.hostname for v in vs]

            of_names_set = set(of_names)
            marathon_hosts_set = set(marathon_hosts)
            delete_hosts = list(of_names_set - marathon_hosts_set)
            add_hosts = list(marathon_hosts_set - of_names_set)

            for h in add_hosts:
                msg = GroupHost.bind(grp_id,h)
            of_ids = [int(v.id) for v in vs if v.hostname in delete_hosts]
            if len(delete_hosts)>0:
                ids = ",".join('%s' % id for id in of_ids)
                msg = GroupHost.unbind(int(grp_id[0]),ids)
    return 'ok'


@app.route('/api/template/query')
def api_template_query():
    q = request.args.get('query', '').strip()
    limit = int(request.args.get('limit', '10'))
    ts, _ = Template.query(1, limit, q)
    ts = [t.to_json() for t in ts]
    return jsonify(data=ts)


@app.route('/api/template/<tpl_id>')
def api_template_get(tpl_id):
    tpl_id = int(tpl_id)
    t = Template.get(tpl_id)
    if not t:
        return jsonify(msg='no such tpl')

    return jsonify(msg='', data=t.to_json())


@app.route('/api/action/<action_id>')
def api_action_get(action_id):
    action_id = int(action_id)
    a = Action.get(action_id)
    if not a:
        return jsonify(msg="no such action")

    return jsonify(msg='', data=a.to_json())


@app.route("/api/expression/<exp_id>")
def api_expression_get(exp_id):
    exp_id = int(exp_id)
    expression = Expression.get(exp_id)
    if not expression:
        return jsonify(msg="no such expression")
    return jsonify(msg='', data=expression.to_json())


@app.route("/api/strategy/<s_id>")
def api_strategy_get(s_id):
    s_id = int(s_id)
    s = Strategy.get(s_id)
    if not s:
        return jsonify(msg="no such strategy")
    return jsonify(msg='', data=s.to_json())
    

@app.route('/api/metric/query')
def api_metric_query():
    q = request.args.get('query', '').strip()
    limit = int(request.args.get('limit', '10'))
    names = utils.metric_query(q, limit)
    names.append(q)
    return jsonify(data=[{'name': name} for name in names])


# 给ping监控提供的接口
@app.route('/api/pings')
def api_pings_get():
    names = db.query_column("select hostname from host")
    return jsonify(hosts=names)


@app.route('/api/debug')
def api_debug():
    return render_template('debug/index.html')


@app.route('/api/group/<grp_name>/hosts.json')
def api_group_hosts_json(grp_name):
    group = HostGroup.read(where='id = %s', params=[grp_name])
    if not group:
        group = HostGroup.read(where='grp_name = %s', params=[grp_name])
        if not group:
            return jsonify(msg='no such group %s' % grp_name)

    vs, _ = Host.query(1, 10000000, '', '0', group.id)
    names = [v.hostname for v in vs]
    return jsonify(msg='', data=names)

