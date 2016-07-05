# -*- coding:utf-8 -*-
__author__ = 'Ulric Qin'
from .bean import Bean
from frame.config import MAINTAINERS
from frame.store import db
from frame.store import uic_db_conn

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
        user_team_id = self.query_user_team(login_user)
        user_id = self.query_user_in_team(user_team_id)
        user_name = self.query_user_name_by_id(user_id)
        if self.create_user in user_name or login_user in MAINTAINERS:
            return True

        return False

    @classmethod
    def query_user_team(cls,create_user):
        rows = uic_db_conn.query_all("select a.tid from rel_team_user as a,user as b where b.name = '%s' and a.uid = b.id" % create_user)
        tid = []
        for id in rows:
            tid.append(id[0])
        uic_db_conn.close()
        return tid

    @classmethod
    def query_user_in_team(cls,user_team_id):
        sql = 'select uid from rel_team_user where'
        for id in user_team_id:
            sql += ' tid = %s or' % id
        sql += ' tid = ""'
        rows = uic_db_conn.query_all(sql)
        uid = []
        for id in rows:
            uid.append(id[0])
        uic_db_conn.close()
        return uid

    @classmethod
    def query_user_name_by_id(cls,user_id):
        sql = 'select name from user where'
        for id in user_id:
            sql += ' id = %s or' % id
        sql += ' id = ""'
        rows = uic_db_conn.query_all(sql)
        user_name = []
        for name in rows:
            user_name.append(name[0])
        uic_db_conn.close()
        return user_name

    @classmethod
    def query(cls, page, limit, query, me=None):
        where = ''
        params = []
        user_team_id = cls.query_user_team(me)
        if len(user_team_id) == 0:
            where = 'create_user = %s'
            params = [me]
        else:
            user_id = cls.query_user_in_team(user_team_id)
            user_name = cls.query_user_name_by_id(user_id)
            for name in user_name:
                where += ' or ' if where else '('
                where += 'create_user = %s'
                params.append(name)
            where += ')'

        if query:
            where += ' and ' if where else ''
            where += 'grp_name like %s'
            params.append('%' + query + '%')

        vs = cls.select_vs(where=where, params=params, page=page, limit=limit, order='grp_name')
        total = cls.total(where, params)
        return vs, total
    
    @classmethod
    def create(cls, grp_name, user_name, come_from):
        # check duplicate grp_name
        if cls.column('id', where='grp_name = %s', params=[grp_name]):
            return -1

        return cls.insert({'grp_name': grp_name, 'create_user': user_name, 'come_from': come_from})

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
