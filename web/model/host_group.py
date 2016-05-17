# -*- coding:utf-8 -*-
__author__ = 'Ulric Qin'
from .bean import Bean
from frame.config import MAINTAINERS
from frame.store import db


class HostGroup(Bean):
    _tbl = 'grp'
    _cols = 'id, grp_name, create_user, come_from'
    _id = 'id'

    def __init__(self, _id, grp_name, create_user, come_from):
        self.id = _id
        self.grp_name = grp_name
        self.create_user = create_user
        self.come_from = come_from

    def writable(self, login_user):
        if self.create_user == login_user or login_user in MAINTAINERS:
            return True

        return False
        @classmethod
    def query(cls, page, limit, query, me, create_user_team=None):
        where = ''
        params = []
        create_user_team = ','.join(cls.query_team(me))
        cls.update_team(create_user_team,me)
        if create_user_team is not None:
            for team in create_user_team.split(','):
                where += 'create_user_team like %s or '
                team = 'open-falcon-test' if len(team)==0 else team
                params.append('%'+team+'%')
        where=where[0:-3]
        where = '('+where+')'
        if query:
            where += ' and ' if where else ''
            where += 'grp_name like %s'
            params.append('%' + query + '%')
        vs = cls.select_vs(where=where, params=params, page=page, limit=limit, order='grp_name')
        total = cls.total(where, params)
        return vs, total
    @classmethod
    def update_team(cls,create_user_team,user_name):
        clause = 'create_user_team = %s where create_user = %s'
        params = [create_user_team,user_name]
        cls.update(clause=clause,params=params)

    @classmethod
    def query_team(cls,user_name):
        team = []
        conn = connect_db(config,db_name = 'uic')
        cursor = conn.cursor()
        cursor.execute("select id from user where name = '%s'" % user_name)
        id = cursor.fetchall()[0][0]
        cursor.execute("select tid from rel_team_user where uid = %s" % id)
        tid = cursor.fetchall()
        for id in tid:
            cursor.execute("select name from team where id = %s" % id[0])
            team.append(cursor.fetchall()[0][0])
        cursor.close()
        conn.close()
        return team


    @classmethod
    def create(cls, grp_name, user_name, create_user_team, come_from):
        # check duplicate grp_name
        if cls.column('id', where='grp_name = %s', params=[grp_name]):
            return -1
        create_user_team = ','.join(create_user_team)
        return cls.insert({'grp_name': grp_name, 'create_user': user_name, 'create_user_team' : create_user_team,'come_from': come_from})


    @classmethod
    def all_group_dict(cls):
        rows = db.query_all('select id, grp_name from grp where come_from = 0')
        return [{'id': row[0], 'name': row[1]} for row in rows]

    @classmethod
    def all_set(cls):
        sql = 'select id, grp_name from %s' % cls._tbl
        rows = db.query_all(sql)
        name_set = dict()
        name_id = dict()
        for row in rows:
            name = row[1]
            name_set[name] = set(name.split('_'))
            name_id[name] = row[0]
        return name_set, name_id
