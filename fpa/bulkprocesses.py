import os
import psycopg2 as pg
import settings as st
import formatschemas as fs
import util
import osutil


class Process(object):
    """Base class for processes.
    
    Implementations are ways of processing a row in the database.  Also known as a strategy.
    """
    def __init__(self, resolution=None, target_field=None):
        self.resolution = resolution
        self.target_field = target_field

    def __str__(self):
        return self.name

    def method():
        pass


class Polfile(object):
    """Simple representation of a political file with id, paths, and bounding box."""
    def __init__(self, row):
        self.docid = row[0]
        self.pdfpath = '%spdfs/%s.pdf' % (st.basepath, self.docid)
        self.htmlpath = '%shtml/%s.html' % (st.basepath, self.docid)

        if len(row) > 1:
            self.bbox = {'urx': row[1], 'ury': row[2]}

    def __str__(self):
        return self.docid




class printParallelParams(Process):
    """Process to print parameters needed to extract a PDF with GNU Parallel."""
    def method(self, polfile, conn, cur, abortOnError=True):

        stand_w = 612
        stand_h = 792

        buff = 12

        pt_px = self.resolution / 72.0

        buff_px = 2.0 * buff * pt_px

        for targetfield, f in self.target_field.iteritems():

            urx = polfile.bbox['urx']
            ury = polfile.bbox['ury']

            w = (f['x2'] - f['x1']) * pt_px
            h = (f['y2'] - f['y1']) * pt_px
            crop_left = f['x1'] - ((stand_w - urx) / 2)
            crop_bottom = (ury - f['y2'])

            # percent of the cropped area taken up
            # by the field, for cropbox.py
            percentOfWindow = w * h / ((w + buff_px) * (h + buff_px))

            # ratio of h/w for cropbox.py
            aspectRatio = h / w

            # buffer
            w += buff_px
            h += buff_px

            w = int(round(w))
            h = int(round(h))

            crop_left -= buff
            crop_bottom -= buff

            if crop_left < 0:
                crop_left = 0
            if crop_bottom < 0:
                crop_bottom = 0

            params = [polfile.pdfpath, w, h, crop_left, crop_bottom,
                      percentOfWindow, aspectRatio, targetfield]
            params = map(str, params)

            print('\t'.join(params))


class parseTextInvoices(Process):
    """Process to extract data from a text based invoice using Poppler."""
    def method(self, polfile, conn, cur):
        values = util.dataAtHocrBboxes(
            fs.common_invoice, st.basepath + 'html/' + polfile.docid + '.html')
        columns_raw = [f['field'] for f in fs.common_invoice]
        data = dict(zip(columns_raw, values))
        data['id'] = polfile.docid

        del data['header']

        # munging
        try:

            (data['invoice_from'], data['invoice_to']) = util.checkDates(
                util.fuzzySplit(data['invoice_period'], '-'))
            del data['invoice_period']

            (data['flight_from'], data['flight_to']) = util.checkDates(
                util.fuzzySplit(data['flight_dates'], '-'))
            del data['flight_dates']

            (data['page'], data['total_pages']) = util.checkInts(
                util.fuzzySplit(data['page_of'].replace('Page', ''), 'of'))
            del data['page_of']

            data['invoice_date'] = util.checkDates([data['invoice_date']])[0]

            if data['estimate_no'] == '':
                data['estimate_no'] = st.NULL

        except Exception, e:
            osutil.print_stderr(e)
            osutil.print_stderr(data)
            return

        datavalues = [d.replace('\t', ' ').replace('\n', ' ').replace(
            '  ', ' ').strip() for d in data.values()]
        datastr = '\t'.join(datavalues)

        try:
            print datastr
        except Exception, e:
            osutil.print_stderr(polfile.docid)
            osutil.print_stderr(e)


class parseTextOrders(Process):
    """Process to extract data from a text based order using Poppler."""
    
    def method(self, polfile, conn, cur):
        values = util.dataAtHocrBboxes(
            fs.common_order, st.basepath + 'html/' + polfile.docid + '.html')
        columns_raw = [f['field'] for f in fs.common_order]
        data = dict(zip(columns_raw, values))

        data['id'] = polfile.docid.replace('_', ':')

        del data['header']

        # munging

        try:

            (data['original_date'], data['revision_date']) = util.checkDates(
                util.fuzzySplit(data['original_date_revision'], ' / '))
            del data['original_date_revision']

            (data['flight_from'], data['flight_to']) = util.checkDates(
                util.fuzzySplit(data['flight_dates'], '-'))
            del data['flight_dates']

            (data['page'], data['total_pages']) = util.checkInts(
                util.fuzzySplit(data['page_of'].replace('Page', ''), 'of'))
            del data['page_of']

        except Exception, e:
            osutil.print_stderr(e)
            osutil.print_stderr(data)
            return

        datavalues = [d.replace('\t', ' ').replace('\n', ' ').replace(
            '  ', ' ').strip() for d in data.values()]
        datastr = '\t'.join(datavalues)

        try:
            print datastr
        except Exception, e:
            osutil.print_stderr(polfile.docid)
            osutil.print_stderr(e)


class parseTextContracts(Process):
    """Process to extract data from a text based contract using Poppler."""

    def method(self, polfile, conn, cur, abortOnError=True):
        values = util.dataAtHocrBboxes(
            fs.common_contract, st.basepath + 'html/' + polfile.docid + '.html')

        columns_raw = [f['field'] for f in fs.common_contract]
        data = dict(zip(columns_raw, values))

        data['id'] = polfile.docid

        del data['header']

        # munging

        try:
            (data['contract_from'], data['contract_to']) = util.checkDates(
                util.fuzzySplit(data['contract_dates'], ' - '))
            del data['contract_dates']

            (data['original_date'], data['revision_date']) = util.checkDates(
                util.fuzzySplit(data['original_date_revision'], ' / '))
            del data['original_date_revision']

            data['print_date'] = util.checkDates([data['print_date']])[0]

            (data['page'], data['total_pages']) = util.checkInts(
                util.fuzzySplit(data['page_from_to'].replace('Page', ''), 'of'))
            del data['page_from_to']

            if data['estimate_no'] == '':
                data['estimate_no'] = st.NULL
        except Exception, e:
            osutil.print_stderr(e)
            osutil.print_stderr(data)
            return

        datavalues = [d.replace('\t', ' ').replace('\n', ' ').replace(
            '  ', ' ').strip() for d in data.values()]

        datastr = '\t'.join(datavalues)

        try:
            print datastr
        except Exception, e:
            osutil.print_stderr(polfile.docid)
            osutil.print_stderr(e)


class markCommonFromLocalText(Process):
    """Process to identify common document types and formats from text based PDFs."""
    def method(self, polfile, conn, cur):
        try:
            doctype = util.dataAtHocrBboxes(fs.doctype, polfile.htmlpath)
            docformat_sql = None

            # Don't check for text if text already
            # found in doctype.
            if len(doctype[0]) > 0:
                anytext = ['text found']
            else:
                anytext = util.dataAtHocrBboxes(
                    fs.fullpage, polfile.htmlpath, returnFirstWord=True)
        except Exception, e:
            raise e
            # print polfile.outfile
            return

        if len(anytext[0]) == 0:
            doctype_sql = st.DOCTYPE_NONTEXT
        else:
            doctype_sql = st.DOCTYPE_TEXT

        if len(doctype[0]) > 0:
            dtype = doctype[0].strip()
            if dtype == st.CONTRACT:
                docformat_sql = st.DOCFORMAT_CONTRACT
            elif dtype == st.INVOICE:
                docformat_sql = st.DOCFORMAT_INVOICE
            elif dtype == st.ORDER:
                docformat_sql = st.DOCFORMAT_ORDER

        print '%s\t%s\t%s' % (polfile.docid, docformat_sql, doctype_sql)


def connect():
    conn = pg.connect(st.CONNECTION)
    cur = conn.cursor()
    return (conn, cur)


def disconnect(conn):
    conn.close()


def bulkProcess(process, query, download=False, overwrite=True, abortOnError=False):
    """Run a process on a set of files in a query."""
    (conn, cur) = connect()
    cur.execute(*query)

    rows = cur.fetchall()

    for row in rows:
        polfile = Polfile(row)

        if download and not os.path.exists(pdfpath):
            try:
                util.downloadBinary(polfile.url, polfile.pdfpath)
            except Exception, e:
                osutil.print_stderr(e)

        if overwrite or not os.path.exists(tifpath):

            if abortOnError:
                process.method(polfile, conn, cur)
            else:
                try:
                    process.method(polfile, conn, cur)
                except Exception, e:
                    osutil.print_stderr(e)

    disconnect(conn)
