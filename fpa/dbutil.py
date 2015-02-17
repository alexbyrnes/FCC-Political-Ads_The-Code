import psycopg2 as pg
import settings as st


def connect():
    conn = pg.connect(st.CONNECTION)
    cur = conn.cursor()
    return (conn, cur)


def disconnect(conn):
    conn.close()


def convertDictToInsert(d, table):
    values = ', '.join(['%s'] * len(d))
    # Prebind these, psycopg only accepts values
    fields = values % tuple(d.keys())

    return "INSERT INTO %s (%s) VALUES (%s)" % (table, fields, values)
