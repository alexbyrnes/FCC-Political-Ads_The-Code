"""Command line application for running processes.

Examples:

    python pq.py parseTextContracts --limit=10
    
    python pq.py printParallelParams --where="KOCO-TV_14043097411984" --resolution="398" --targetfield="invoice"
    # Parallel should be run with run_parallel.py

    python pq.py markCommonFromLocalText
    
"""

from bulkprocesses import bulkProcess, markCommonFromLocalText, parseTextContracts, parseTextInvoices, parseTextOrders, printParallelParams
import settings as st
import formatschemas as fs
import queries


def printParallelParams_cmd(resolution, targetfield, where=None, limit=None):
    """Command that runs process to print parameters needed to extract a PDF with GNU Parallel."""
    if targetfield in ['invoice', 'invoice_uncropped']:
        docformat = st.DOCFORMAT_INVOICE

    tf = fs.targetfields[targetfield]
    query = queries.standard('N', docformat, where, limit)

    process = printParallelParams(resolution, tf)
    bulkProcess(process, query, abortOnError=True)


def markCommonFromLocalText_cmd(where=None, limit=None):
    """Command that runs process to identify common document types and formats from text based PDFs."""
    # TODO set to None

    docformat = st.DOCFORMAT_CONTRACT

    query = queries.idOnly('T', docformat, where, limit)
    process = markCommonFromLocalText()
    bulkProcess(process, query, abortOnError=True)


def parseTextContracts_cmd(where=None, limit=None):
    """Command that runs process to extract data from a text based contract using Poppler."""
    docformat = st.DOCFORMAT_CONTRACT

    query = queries.idOnly('T', docformat, where, limit)
    process = parseTextContracts()
    bulkProcess(process, query, abortOnError=False)


def parseTextInvoices_cmd(where=None, limit=None):
    """Command that runs process to extract data from a text based invoice using Poppler."""
    docformat = st.DOCFORMAT_INVOICE

    query = queries.idOnly('T', docformat, where, limit)
    process = parseTextInvoices()
    bulkProcess(process, query, abortOnError=False)


def parseTextOrders_cmd(where=None, limit=None):
    """Command that runs process to extract data from a text based order using Poppler."""
    docformat = st.DOCFORMAT_ORDER

    query = queries.idOnly('T', docformat, where, limit)
    process = parseTextOrders()
    bulkProcess(process, query, abortOnError=False)


if __name__ == '__main__':
    import clime
    clime.start(white_pattern=clime.CMD_SUFFIX, debug=True)
