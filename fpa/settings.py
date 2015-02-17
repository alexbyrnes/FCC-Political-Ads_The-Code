"""Settings"""


CONNECTION = "dbname='fcc' user='<user>' host='localhost' password='<pw>'"

YEAR = 2014

accepted_date_formats = ["%m/%d/%Y", "%m/%d/%y"]

main_table = 'polfile'

# Directories
python_bin = ''
raw_data_dir = 'rawdata/'
invalid_data_dir = 'invalid/'
to_validate_dir = 'to_validate/'

# Directory where pdfs and html directories should be located.
basepath = '../'

# Postgres null value in text.
NULL = '''\N'''  

# FCC URL
baseurl = 'https://stations.fcc.gov/'


# Database values
DOCFORMAT_CONTRACT = 'Common Contract'
DOCFORMAT_INVOICE = 'Common Invoice'
DOCFORMAT_ORDER = 'Common Order'

CONTRACT = 'CONTRACT'
INVOICE = 'INVOICE'
ORDER = 'ORDER'

DOCTYPE_TEXT = 'T'
DOCTYPE_NONTEXT = 'N'


# Image processes used by run_extract.py.

extract_params = [
    {'size': 54, 'resolution': 398},
    {'size': 54, 'resolution': 400},
    {'size': 54, 'resolution': 390},
    {'size': 51, 'resolution': 380},
    {'size': 53, 'resolution': 397},
    {'size': 57, 'resolution': 418},
    {'size': 54, 'resolution': 398, 'deskew': 40},
    {'size': 54, 'resolution': 400, 'deskew': 40},
    {'size': 54, 'resolution': 390, 'deskew': 40},
    {'size': 51, 'resolution': 380, 'deskew': 40},
    {'size': 53, 'resolution': 397, 'deskew': 40},
    {'size': 57, 'resolution': 418, 'deskew': 40},
    {'size': 54, 'resolution': 398, 'cuneiform': True},
    {'size': 54, 'resolution': 400, 'cuneiform': True},
    {'size': 54, 'resolution': 390, 'cuneiform': True},
    {'size': 51, 'resolution': 380, 'cuneiform': True},
    {'size': 53, 'resolution': 397, 'cuneiform': True},
    {'size': 57, 'resolution': 418, 'cuneiform': True},
    {'size': 54, 'resolution': 398, 'median': 2},
    {'size': 54, 'resolution': 400, 'median': 2},
    {'size': 54, 'resolution': 390, 'median': 2},
    {'size': 51, 'resolution': 380, 'median': 2},
    {'size': 53, 'resolution': 397, 'median': 2},
    {'size': 57, 'resolution': 418, 'median': 2},
    {'size': 54, 'resolution': 398, 'textcleaner': 0},
    {'size': 54, 'resolution': 398, 'textcleaner': 1},
    {'size': 54, 'resolution': 398, 'textcleaner': 2},
    {'size': 54, 'resolution': 400, 'textcleaner': 0},
    {'size': 54, 'resolution': 400, 'textcleaner': 1},
    {'size': 54, 'resolution': 400, 'textcleaner': 2},
    {'size': 54, 'resolution': 398, 'sharpen': '0x2'},
    {'size': 54, 'resolution': 400, 'sharpen': '0x2'},
    {'size': 54, 'resolution': 390, 'sharpen': '0x2'},
    {'size': 51, 'resolution': 380, 'sharpen': '0x2'},
    {'size': 53, 'resolution': 397, 'sharpen': '0x2'},
    {'size': 57, 'resolution': 418, 'sharpen': '0x2'},
    {'size': 54, 'resolution': 398, 'nudge': '(10,0,0,0)'},
    {'size': 54, 'resolution': 398, 'nudge': '(0,10,0,0)'},
    {'size': 54, 'resolution': 398, 'nudge': '(0,0,10,0)'},
    {'size': 54, 'resolution': 398, 'nudge': '(0,0,0,10)'},
    {'size': 54, 'resolution': 398, 'nudge': '(10,0,10,0)'},
    {'size': 54, 'resolution': 398, 'nudge': '(10,0,0,10)'},
    {'size': 54, 'resolution': 398, 'nudge': '(0,10,10,0)'},
    {'size': 54, 'resolution': 398, 'nudge': '(0,10,0,10)'},
    {'size': 54, 'resolution': 398, 'threshold': True},
    {'size': 54, 'resolution': 400, 'threshold': True},
    {'size': 54, 'resolution': 390, 'threshold': True},
    {'size': 51, 'resolution': 380, 'threshold': True},
    {'size': 53, 'resolution': 397, 'threshold': True},
    {'size': 57, 'resolution': 418, 'threshold': True},
    {'size': 54, 'resolution': 399},
    {'size': 54, 'resolution': 401},
    {'size': 54, 'resolution': 389},
    {'size': 51, 'resolution': 381},
    {'size': 53, 'resolution': 396},
    {'size': 57, 'resolution': 417}
]
