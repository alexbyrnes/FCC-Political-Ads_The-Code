"""Standard queries for sending particular records in the database through a process.

Uses python-sql. A raw query would be written like this:

def sqlByHand():
    return ('select id from contract where doctype = %s', 'T')

"""
from sql import Table
import settings as st

main = Table(st.main_table)
standard_cols = (main.id, main.urx, main.ury)


def standard(doctype, docformat, where=None, limit=None):
    q = main.select(*standard_cols)
    q.where = (main.doctype == doctype) & (
        main.docformat == docformat) & (main.id == where)
    q.limit = limit
    return tuple(q)


def idOnly(doctype, docformat, where=None, limit=None):
    q = main.select(main.id)
    q.where = (main.doctype == doctype) & (
        main.docformat == docformat) & (main.id == where)
    q.limit = limit
    return tuple(q)


