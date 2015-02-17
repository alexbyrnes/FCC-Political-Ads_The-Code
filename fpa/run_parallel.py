"""Run GNU Parallel on a set of files, converting, cropping, OCR etc.

options:

    --resolution (r)  Image resolution for conversion of PDF to PNG.  Minimum for good results is 300, but higher values with reduction (see size) will produce better results especially for large font size and poor quality input.

    --size (s)  Percent to resize images.
    
    --targetfield  Document format to extract. These are in formatschemas.py.
    
    --inputfile  File to use instead of output from the database.
    
    --outfile  Output file for extracted text.
    
    --crop  Crop the images. Only works for fields that are enclosed in a box on the page.
    
    --where  ID of record to extract.
    
    --limit  Number of documents to extract if there are more than this number in the database.
    
    --page  Page to extract.  
    
    --psm  Page segmentation method. For tesseract.  3 for text on multiple lines, 7 for text on a single line.
    
    --rotation  Rotate the images before OCR.  -90 = rotate counter-clockwise 90 degrees.
    
    --language  Language for tesseract.  Default is English.
    
    --outputpng  Output PNG files without any filters to /tmp.
    
    --outputcrop  Output PNG files after cropping with cropbox.py to /tmp.
    
    --outputchop  Output PNG files after chopping the header and margin from sides and bottom.
    
    --maxprocs  Maximum number of processors for parallel to use.  Default is 8.
    
    --printcmd  Do not run the command.  Print it to the console.
    
    --limitIMthreads  Limit number of threads ImageMagick can use.
    
    --median  Apply median filter with a certain radius.  Values over 2 will likely reduce image quality for small fonts.
    
    --sharpen  ImageMagick sharpen: 0x2, 0x3 ... 
    
    --textcleaner  Parameter set for textcleaner.  
        0 = Trim, sharpen
        1 = Trim, enhance normalize
        2 = Trim, sharpen, enhance normalize
    
    --nudge  Move the area extracted from the PDF by a certain number of points "(Left, Right, Down, Up)."  --nudge=(10, 0, 10, 0) is nudge 10 points left and 10 down.
    
    --bbox  Get HOCR coordinates from tesseract output.  Only works for tesseract config file "hocr."
    
    --targettext  Text to search for (with --bbox).
    
    --threshold  Threshold the image before OCR.  Uses gaussian threshold with 40 pixel block size.
    
    --deskew  Correct small rotation of the text with ImageMagick.  40 is recommended.
    
    --cuneiform  Use cuneiform instead of tesseract for OCR.
    
    --whiteThreshold  Threshold at which to turn gray pixels white. 97 is a safe value for scanned paper documents.
    
    --noinfo  Don't append info to output like id, parameters used etc.

    --dryrun  Print all parallel commands without running.  Useful for debugging, or running without python.
    

examples:

    Run single invoice with fields on page 2, resolution 400 dpi, resize to 50%.
    
        python run_parallel.py -s=50 -r=400 --targetfield=invoice --where="KOCO-TV_14043097411984" --page=2 --crop --noinfo

    Run all contracts in the database.
    
        python run_parallel.py -s=50 -r=400 --targetfield=contract --crop

    Run invoice_addresses (addresses don't need to be cropped and have multiple lines of text per image).
        
        python run_parallel.py -s=50 -r=400 --targetfield=contract


"""

import settings as st
import osutil
import os
import glob


def run_cmd(resolution, targetfield, size=100, inputfile=None, outfile=None, crop=False, where='', limit=1, page=1, psm=7, rotation=None, language='engarial', outputpng=False, maxprocs=8, printcmd=False, limitIMthreads=True, median=None, sharpen=None, textcleaner=None, nudge=None, bbox=False, targettext=None, outputcrop=False, outputchop=False, threshold=False, deskew=None, cuneiform=False, whiteThreshold=None, noinfo=False, dryrun=None):
    '''Extract fields from a PDF using GNU Parallel
    -o <str>, --outfile=<str>
    -s <int>, --size=<int> 
    -r <int>, --resolution=<int>

    '''

    python_bin = st.python_bin
    raw_data_dir = st.raw_data_dir

    chop_top = 50
    chop_bottom = 20
    chop_right = 1
    chop_left = 0

    (l, r, d, u) = (0, 0, 0, 0)

    limitIM = ''
    resize_arg = ''
    median_arg = ''
    sharpen_arg = ''
    rotation_arg = ''
    deskew_arg = ''
    whiteThreshold_arg = ''
    cropbox = ''
    convert_crop = ''
    textcleaner_arg = ''
    threshold_arg = ''
    output_file = ''
    dryrun_arg = ''

    extract_params = 'resolution %(resolution)s  size %(size)s  median %(median)s  sharpen %(sharpen)s  textcleaner %(textcleaner)s  nudge %(nudge)s  deskew %(deskew)s  threshold %(threshold)s  cuneiform %(cuneiform)s' % locals()

    if limitIMthreads:
        limitIM = '-limit thread 1'

    if size != 100:
        resize_arg = '-resize %i%%' % size

    if median is not None:
        median_arg = '-median %d' % median

    if sharpen is not None:
        sharpen_arg = '-sharpen %s' % sharpen

    if rotation is not None:
        rotation_arg = '-rotation %i' % rotation

    if deskew is not None:
        deskew_arg = '-deskew %i' % deskew

    if whiteThreshold is not None:
        whiteThreshold_arg = '-white-threshold %i%%' % whiteThreshold

    if nudge is not None:
        nudgestrs = nudge.strip()[1:-1].split(',')
        (l, r, d, u) = map(int, nudgestrs)

    if dryrun is not None:
        dryrun_arg = '--dryrun' 

    ghostscript = ''''gs -q -dSAFER -sDEVICE=png16m -dFirstPage=%(page)i -dLastPage=%(page)i -g{2}x{3} -r%(resolution)s -o - -c "<</Install {-$((%(r)i-%(l)i+{4})) -$((%(u)i-%(d)i+{5})) translate}>> setpagedevice" -f "{1}" ''' % locals()

    if inputfile is None:
        pdfpaths = '''python %(python_bin)spq.py printParallelParams --where="%(where)s" --limit="%(limit)s" --resolution="%(resolution)s" --targetfield="%(targetfield)s"''' % locals()
    else:
        pdfpaths = '''cat %(inputfile)s''' % locals()

    parallel = '''| parallel %(dryrun_arg)s --no-run-if-empty --colsep '\\t' --max-procs=%(maxprocs)i --ungroup''' % locals()

    convert_resize = '''| convert %(limitIM)s %(median_arg)s %(sharpen_arg)s %(rotation_arg)s %(resize_arg)s - - ''' % locals()

    if outputpng:
        convert_resize += ''' | tee /tmp/{1/.}_{8}.png'''

    if crop:
        cropbox = '''| python -u %(python_bin)scropbox.py {6} {7}''' % locals()

        convert_crop = '''| convert %(limitIM)s -gravity North -chop 0x%(chop_top)s%% -gravity East -chop %(chop_right)ix0%% -gravity West -chop %(chop_left)ix0%% -gravity South -chop 0x%(chop_bottom)s%% -bordercolor white -border 4x4 %(deskew_arg)s %(whiteThreshold_arg)s - -''' % locals()

        if outputcrop:
            cropbox += ''' | tee /tmp/{1/.}_crop_{8}.png'''

        if outputchop:
            convert_crop += ''' | tee /tmp/{1/.}_chop_{8}.png'''

    if textcleaner is not None:
        if textcleaner == 0:
            textcleaner_arg = '| textcleaner -T -s 1 png:- png:-'
        elif textcleaner == 1:
            textcleaner_arg = '| textcleaner -T -e normalize png:- png:-'
        elif textcleaner == 2:
            textcleaner_arg = '| textcleaner -T -s 1 -e normalize png:- png:-'

    if threshold:
        threshold_arg = '| python threshold.py gaussian 40'

    if not cuneiform:
        ocr = '''| tesseract303 - - -psm %(psm)s -lang=%(language)s {8} 2> /dev/null | python %(python_bin)snoinput.py''' % locals()
    else:
        ocr = '''| cuneiform --singlecolumn - -o /tmp/{1/.}_cuneiform.txt > /dev/null 2> /dev/null || touch /tmp/{1/.}_cuneiform.txt && cat /tmp/{1/.}_cuneiform.txt | python %(python_bin)snoinput.py''' % locals()

    remove_nl = ''' | tr -s "\\n" " " | sed "s/$/\\n/g" '''

    if bbox:
        ocr += '''| python hocrCoords.py %(targettext)s''' % locals()

    addinfo = ''
    if not noinfo:
        addinfo = ''' | sed -e "s|\(.\+\)$|\\1\\t{8}\\t%(page)i\\t%(extract_params)s\\t{1}\\t{2}\\t{3}\\t{4}\\t{5}\\t{6}\\t{7}\\t{8}|g" ''' % locals()

    addinfo += '\''  # quote for end of parallel section

    if outfile is not None:
        output_file = '''> %(outfile)s ''' % locals()

    cmd = ' '.join([pdfpaths, parallel, ghostscript, convert_resize, cropbox,
                    convert_crop, textcleaner_arg, threshold_arg, ocr, remove_nl, addinfo, output_file])

    if printcmd:
        print(cmd)
    else:
        cmdout = osutil.getStdoutFromCmd(cmd, shell=True)
        if cmdout.strip() != '':
            print cmdout


    # remove cuneiform output files
    filelist = glob.glob("/tmp/*cuneiform.txt")
    for f in filelist:
        os.remove(f)


if __name__ == '__main__':
    import clime
    clime.start(white_pattern=clime.CMD_SUFFIX, doc=__doc__, default='run', debug=False)
