import unittest2
import run_parallel as rp
import run_extract
import pq
from mock import patch
from io import BytesIO
import filecmp
import os
import subprocess


run_extract_tmp = 'tests/run_extract_tmp.tsv'
run_extract_expected = 'tests/run_extract.tsv'


def runcmd(command):
    child = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE)
    return child.communicate()[0]
    


class TestPQ(unittest2.TestCase):

    def test_invoice(self):
 
        expectedOut = ['06104114 - 06/23/14', '', 'HIETT 4 CORP COMMISS', '', 'Hiean/Corporation Commi:', '1196633', '105126114 - 06120114', '1196633-1', 'W7196822', '', '', '']

        expectedOut.sort()
        
        params = {'size': 54, 
                'resolution': 398, 
                'targetfield': 'invoice', 
                'where' : "KOCO-TV_14043097411984", 
                'limit' : 1,
                'page': 2, 
                'noinfo': True,
                'crop': True,
                'psm': 7
                }
        with patch('sys.stdout', new=BytesIO()) as cap_stdout:
            rp.run_cmd(**params)
            
            out = cap_stdout.getvalue()
            out_list = out.split('\n')
            out_list.sort()
            out_list = [o.strip() for o in out_list]
            self.assertEquals(out_list, expectedOut)


    def test_invoice_cropped(self):
        expectedOut = ['', '', 'is: Midwest Communications & Media Attention: Accounts Payable 2015 Roundwyck Lane Powell, OH 43065']
        expectedOut.sort()
        
        params = {'size': 54, 
                'resolution': 398, 
                'targetfield': 'invoice_uncropped', 
                'where' : "KOCO-TV_14043097411984", 
                'limit' : 1,
                'page': 2, 
                'noinfo': True,
                'crop': False,
                'psm': 3
                }
        with patch('sys.stdout', new=BytesIO()) as cap_stdout:
            rp.run_cmd(**params)
            
            out = cap_stdout.getvalue()
            out_list = out.split('\n')
            out_list.sort()
            out_list = [o.strip() for o in out_list]
            self.assertEquals(out_list, expectedOut)


    def test_poppler_contract(self):
        expectedOut = ['Balukoff/D/Gov', 'Shepard Ritzen', '\\N', 'EOM/EOC', '570', 'K27DX_14080331353324', '08156869', 'KATZ-Philadelphia', 'Adults 35+', '08/11/14', '', 'KIVI', '\\N', '', 'BALUKOFF/D/GOV', 'Buying Time LLC Attention: Krista Murray 650 Massachusetts Avenue NW Ste #210 Washington, DC 20001-3796', '\\N', '', '5', '', 'Journal Broadcast Group 1866 East Chisholm Drive Nampa, ID 83687 (208)336-0500', '532345 /', '3251', 'Broadcast', '1', '561', 'Cash', '08/25/14']

        params = {
                'where' : "K27DX_14080331353324", 
                'limit' : 1,
                }
        with patch('sys.stdout', new=BytesIO()) as cap_stdout:
            pq.parseTextContracts_cmd(**params)
            
            out = cap_stdout.getvalue()
            out_list = out.split('\t')
            out_list = [o.strip() for o in out_list]
            self.assertEquals(out_list, expectedOut)


    def test_mark_types(self):

        expectedOut = 'K27DX_14080331353324\tCommon Contract\tT\n'
        
        params = {'where' : "K27DX_14080331353324"}
        with patch('sys.stdout', new=BytesIO()) as cap_stdout:
            pq.markCommonFromLocalText_cmd(**params)
            
            out = cap_stdout.getvalue()
            self.assertEquals(out, expectedOut)

    def test_run_extract(self):
        params = {
                'targetfield' : 'invoice',
                'where' : 'KOCO-TV_14043097411984',
                'crop' : True,
                'page' : 2,
                'validfile' : 'tests/run_extract_tmp.tsv',
                }
        with patch('sys.stderr', new=BytesIO()) as cap_stderr:
            run_extract.run_extract_cmd(**params)
            
            out = cap_stderr.getvalue()
            expected_f = open(run_extract_expected, 'r')
            tmp_expected = open(run_extract_tmp, 'r')

            e = sorted(expected_f.readlines())
            t = sorted(tmp_expected.readlines())
            os.remove(run_extract_tmp)
            self.assertEquals(e, t)

    def test_cropbox(self):
        out = runcmd('''cat tests/cropbox.png | python cropbox.py .27 2.27 | tesseract303 - - ''')

        self.assertEquals(out.strip(), 'right')

    def test_merge_clusters(self):
        out = runcmd('''python merge_clusters.py tests/merge_clusters.tsv''')

        self.assertEquals(out.strip(), 'Democratic Gov Assoc\tDemocratic Governors Association\nComm for Employment Oppty OH\tCommittee for Employment Opportunity\nCmte for Empl Oppty FL\tCommittee for Employment Opportunity\nDem Governors Assn\tDemocratic Governors Association')

