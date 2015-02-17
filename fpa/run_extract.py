"""Runs files through a series of filters and other image processing applications.  See settings.extract_params.

Examples:
    
    python run_extract.py --targetfield=invoice --where="KOCO-TV_14043097411984" --crop --page=2
    
    python run_extract.py --targetfield=contract --limit=12 --crop


"""

import osutil
import settings as st
import run_parallel as rp


def run_extract_cmd(targetfield, inputfile=None, crop=False, where='', limit=1, page=1, psm=7, outputpng=False, printcmd=False, outputcrop=False, outputchop=False, whiteThreshold=97, validfile=None):

    cl_params = {}

    cl_params['limit'] = limit
    cl_params['page'] = page
    cl_params['crop'] = crop
    cl_params['psm'] = psm
    cl_params['targetfield'] = targetfield
    cl_params['where'] = where
    cl_params['outputpng'] = outputpng
    cl_params['outputcrop'] = outputcrop
    cl_params['outputchop'] = outputchop
    cl_params['printcmd'] = printcmd
    cl_params['whiteThreshold'] = whiteThreshold
    if validfile is None:
        validfile = "%s%s.tsv" % (st.raw_data_dir, targetfield)
    else:
        validfile = validfile 


    for i, p in enumerate(st.extract_params):

        all_p = dict(p.items() + cl_params.items())

        if i == 0:
            all_p['inputfile'] = inputfile
            #all_p['where'] = "and ep.params='%(b_params)s'" % b_params
        else:
            all_p['inputfile'] = invalidfile

        all_p['outfile'] = "%s%s_%i.tsv" % (st.to_validate_dir, targetfield, i)
        invalidfile = "%s%s_%i.tsv" % (st.invalid_data_dir, targetfield, i)

        if i == len(p) - 1:
            all_p['outputpng'] = True
            all_p['outputcrop'] = True
            all_p['outputchop'] = True

        rp.run_cmd(**all_p)

        osutil.getStdoutFromCmd('''cat %s | python %svalidate.py %s  > %s ''' % (all_p['outfile'], st.python_bin, validfile, invalidfile), shell=True)

if __name__ == '__main__':
    import clime
    clime.start(white_pattern=clime.CMD_SUFFIX, default='run_extract', debug=True)
