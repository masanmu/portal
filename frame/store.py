# -*- coding:utf-8 -*-
__author__ = 'Ulric Qin'

import logging
import MySQLdb
from frame import config


def connect_db(host,port,user,passwd,db):
    try:
        conn = MySQLdb.connect(
            host=host,
            port=port,
            user=user,
            passwd=passwd,
            db=db,
            use_unicode=True,
            charset="utf8")
        return conn
    except Exception, e:
        logging.getLogger().critical('connect db: %s' % e)
        return None


class DB(object):
    def __init__(self, host,port,user,passwd,db):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.conn = connect_db(host,port,user,passwd,db)

    def get_conn(self):
        if self.conn is None:
            self.conn = connect_db(self.host,self.port,self.user,self.passwd,self.db)
        return self.conn

    def execute(self, *a, **kw):
        cursor = kw.pop('cursor', None)
        try:
            cursor = cursor or self.get_conn().cursor()
            cursor.execute(*a, **kw)
        except (AttributeError, MySQLdb.OperationalError):
            self.conn and self.conn.close()
            self.conn = None
            cursor = self.get_conn().cursor()
            cursor.execute(*a, **kw)
        return cursor

    # insert one record in a transaction
    # return last id
    def insert(self, *a, **kw):
        cursor = None
        try:
            cursor = self.execute(*a, **kw)
            row_id = cursor.lastrowid
            self.commit()
            return row_id
        except MySQLdb.IntegrityError:
            self.rollback()
        finally:
            cursor and cursor.close()

    # update in a transaction
    # return affected row count
    def update(self, *a, **kw):
        cursor = None
        try:
            cursor = self.execute(*a, **kw)
            self.commit()
            row_count = cursor.rowcount
            return row_count
        except MySQLdb.IntegrityError:
            self.rollback()
        finally:
            cursor and cursor.close()

    def query_all(self, *a, **kw):
        cursor = None
        try:
            cursor = self.execute(*a, **kw)
            return cursor.fetchall()
        finally:
            cursor and cursor.close()

    def query_one(self, *a, **kw):
        rows = self.query_all(*a, **kw)
        if rows:
            return rows[0]
        else:
            return None

    def query_column(self, *a, **kw):
        rows = self.query_all(*a, **kw)
        if rows:
            return [row[0] for row in rows]
        else:
            return []

    def commit(self):
        if self.conn:
            try:
                self.conn.commit()
            except MySQLdb.OperationalError:
                self.conn = None

    def rollback(self):
        if self.conn:
            try:
                self.conn.rollback()
            except MySQLdb.OperationalError:
                self.conn = None


db = DB(
        config.PORTAL_DB_HOST,
        config.PORTAL_DB_PORT,
        config.PORTAL_DB_USER,
        config.PORTAL_DB_PASS,
        config.PORTAL_DB_NAME)
uic_db_conn = DB(
        config.UIC_DB_HOST,
        config.UIC_DB_PORT,
        config.UIC_DB_USER,
        config.UIC_DB_PASS,
        config.UIC_DB_NAME)
