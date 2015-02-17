##Code Repository for the FCC Political Ad Archive
 
Code for extracting data from a large number of PDFs, particularly FCC Political Ad documents


Main requirements:
* ImageMagick
* GNU Parallel
* PostgreSQL
* Python
* Tesseract (3.03)
* Ghostscript

(Optional)
* Cuneiform

Python are dependencies in requirements.txt. `pip install -r requirements.txt`

Some python dependencies may be installed with Debian packages:

* python-lxml
* python-numpy
* python-scipy
* python-skimage


#####Create database

    createdb fcc
    psql -d fcc -f schema.sql

#####Edit settings.py
```

CONNECTION = "dbname='fcc' user='<user>' host='localhost' password='<pw>'"

python_bin = '/path/to/scripts/'
raw_data_dir = 'rawdata/'
invalid_data_dir = 'invalid/'
to_validate_dir = 'to_validate/'

# Directory where pdfs and html directories should be located.
basepath = '/path/for/files/'
```


#####Run the tests

    cd fpa
    nosetests

#####Download files

    python station_dloader.py
    

#####Get help for main scripts

    python pq.py --help
    python run_parallel.py --help
    python run_extract.py --help
    # (cropbox.py, merge_clusters.py, standardize.py, threshold.py)

#####Identify text PDFs

    python pq.py markCommonFromLocalText

#####Extract data from text PDFs

    python pq.py parseTextInvoices
    python pq.py parseTextContracts
    python pq.py parseTextOrders


#####Get bounding boxes

    ./get_bboxes.sh

#####Detect document types

    python run_parallel.py --help
    python run_parallel.py -s=35 -r=420 --psm=3 --targetfield=doctype --outfile="doctype.tsv"


#####Extract data from one type

    python run_parallel.py -s=50 -r=400 --targetfield=contract --crop


#####Extract using multiple trials and validation 

    python run_extract.py --help
    python run_extract.py --targetfield=contract --crop


####Other Useful Commands

#####Print all Parallel commands  

This can be used to run extractions on other machines, or without python dependencies.

    python run_parallel.py <parameters> --dryrun

#####Print only initial Parallel command

    python run_parallel.py <parameters> --printcmd

#####Output images from each stage of process

    python run_parallel.py <parameters> --outputpng --outputcrop --outputchop

#####Get the number of pages in the documents

    ./get_pages.sh


###Full List of Scripts and Modules


####bulkprocesses

```
CLASSES
        Polfile
        Process
            markCommonFromLocalText
            parseTextContracts
            parseTextInvoices
            parseTextOrders
            printParallelParams
    
    class Polfile
       Simple representation of a political file with id, paths, and bounding box.

    class Process
       Base class for processes.
       Implementations are ways of processing a row in the database.  Also known as
       a strategy.
    
    class markCommonFromLocalText(Process)
       Process to identify common document types and formats from text based PDFs.

    class parseTextContracts(Process)
       Process to extract data from a text based contract using Poppler.
    
    class parseTextInvoices(Process)
       Process to extract data from a text based invoice using Poppler.

    class parseTextOrders(Process)
       Process to extract data from a text based order using Poppler.
        
    class printParallelParams(Process)
       Process to print parameters needed to extract a PDF with GNU Parallel.
    
FUNCTIONS
    bulkProcess(process, query, download=False, overwrite=True, abortOnError=False)
        Run a process on a set of files in a query.
```

####cropbox.py  

```
DESCRIPTION
    Crop an image around a box in the image closest to the size
    and width/height specified.
    
    example:
        
        Crop around the box that's 50% of the total size and
        with width/height 1.25:
    
            cat img.png | python cropbox.py .5 1.25 > cropped.png
```


####merge_clusters.py


```
DESCRIPTION
    Finds equivalent strings with abbreviations.  Will find the 
    matching string with the highest "score."  Scores should be in 
    the second column of the input file.
    
    
    example: 
        
        python merge_clusters.py clusters.tsv
    
    
    Example input (tab delimited):
    
    Democratic Governors Association        25
    Democratic Gov Assoc    2
    Comm for Employment Oppty OH    62
    Cmte for Empl Oppty FL  6
    Committee for Employment Opportunity    85
    Dem Governors Assn      8
    
    Output:
        
    Democratic Gov Assoc    Democratic Governors Association
    Comm for Employment Oppty OH    Committee for Employment Opportunity
    Cmte for Empl Oppty FL  Committee for Employment Opportunity
    Dem Governors Assn      Democratic Governors Association

FUNCTIONS
    canBePacked(s, target)
    canSkip(s, abbrs, skip_words)
    getCommon(a, b)
    hasCommon(a, b)
    highestMatch(fixes, counts)
    
```


####osutil

Operating system utilities.  Running commands, printing to stderr etc.

```
FUNCTIONS
    getExitStatusFromCmd(command, shell=False, stderr=False)
        Execute command and capture exit status.
    
    getStdoutFromCmd(command, shell=False, stderr=False)
        Execute command and capture stderr or stdout.
    
    print_stderr(*objs)
        Print to standard error.
```


####pq.py

Command line application for running processes.


```
DESCRIPTION
    Examples:
    
        python pq.py parseTextContracts --limit=10
        
        python pq.py printParallelParams --where="<doc id>" -r 398 -s 54 --targetfield="invoice"
        # Parallel should be run with run_parallel.py
    
        python pq.py markCommonFromLocalText

FUNCTIONS
    markCommonFromLocalText_cmd(where=None, limit=None)
        Command that runs process to identify common document types and formats from text based PDFs.
    
    parseTextContracts_cmd(where=None, limit=None)
        Command that runs process to extract data from a text based contract using Poppler.
    
    parseTextInvoices_cmd(where=None, limit=None)
        Command that runs process to extract data from a text based invoice using Poppler.
    
    parseTextOrders_cmd(where=None, limit=None)
        Command that runs process to extract data from a text based order using Poppler.
    
    printParallelParams_cmd(resolution, targetfield, where=None, limit=None)
        Command that runs process to print parameters needed to extract a PDF with GNU Parallel.
```

####run_extract.py

Runs files through a series of filters and other image processing applications.  See settings.extract_params.


```
DESCRIPTION
    Examples:
        
        python run_extract.py --targetfield=invoice --where="KOCO-TV_14043097411984" --crop --page=2
        
        python run_extract.py --targetfield=contract --limit=12 --crop
```


####run_parallel.py

Run GNU Parallel on a set of files, converting, cropping, OCR etc.


```
DESCRIPTION
    options:
    
        --resolution, -r  Image resolution for conversion of PDF to PNG.  Minimum for good 
                          results is 300, but higher values with reduction (see size) will 
                          produce better results especially for large font size and poor 
                          quality input.
    
        --size, -s  Percent to resize images.
        
        --targetfield  Document format to extract. These are in formatschemas.py.
        
        --inputfile  File to use instead of output from the database.
        
        --outfile  Output file for extracted text.
        
        --crop  Crop the images. Only works for fields that are enclosed in a box on the 
                page.
        
        --where  ID of record to extract.
        
        --limit  Number of documents to extract if there are more than this number in the 
                 database.
        
        --page  Page to extract.  
        
        --psm  Page segmentation method. For tesseract.  3 for text on multiple lines, 7 for 
               text on a single line.
        
        --rotation  Rotate the images before OCR.  -90 = rotate counter-clockwise 90 degrees.
        
        --language  Language for tesseract.  Default is English.
        
        --outputpng  Output PNG files without any filters to /tmp.
        
        --outputcrop  Output PNG files after cropping with cropbox.py to /tmp.
        
        --outputchop  Output PNG files after chopping the header and margin from sides and 
                      bottom.
        
        --maxprocs  Maximum number of processors for parallel to use.  Default is 8.
        
        --printcmd  Do not run the command.  Print it to the console.
        
        --limitIMthreads  Limit number of threads ImageMagick can use.
        
        --median  Apply median filter with a certain radius.  Values over 2 will likely reduce 
                  image quality for small fonts.
        
        --sharpen  ImageMagick sharpen: 0x2, 0x3 ... 
        
        --textcleaner  Parameter set for textcleaner.  
            0 = Trim, sharpen
            1 = Trim, enhance normalize
            2 = Trim, sharpen, enhance normalize
        
        --nudge  Move the area extracted from the PDF by a certain number of points 
                 "(Left, Right, Down, Up)."  --nudge=(10, 0, 10, 0) is nudge 10 points left and
                 10 down.
        
        --bbox  Get HOCR coordinates from tesseract output.  Only works for tesseract config 
                file "hocr."
        
        --targettext  Text to search for (with --bbox).
        
        --threshold  Threshold the image before OCR.  Uses gaussian threshold with 40 pixel 
                     block size.
        
        --deskew  Correct small rotation of the text with ImageMagick.  40 is recommended.
        
        --cuneiform  Use cuneiform instead of tesseract for OCR.
        
        --whiteThreshold  Threshold at which to turn gray pixels white. 97 is a safe value for 
                          scanned paper documents.
        
        --noinfo  Don't append info to output like id, parameters used etc.
    
        --dryrun  Print all parallel commands without running.  Useful for debugging, or 
                  running without python.
        
    
    examples:
    
        Run single invoice with fields on page 2, resolution 400 dpi, resize to 50%.
        
            python run_parallel.py -s=50 -r=400 --targetfield=invoice --limit=1 --page=2 --crop
    
        Run all contracts in the database.
        
            python run_parallel.py -s=50 -r=400 --targetfield=contract --crop
    
        Run invoice_addresses (addresses don't need to be cropped and have multiple lines).
            
            python run_parallel.py -s=50 -r=400 --targetfield=contract
```



####standardize.py

```
DESCRIPTION
    Standardize data.  Make addresses and titlecase consistent
    for string clustering.
    
    example:
        python standardize.py inputfile.tsv validate_address -c 3
    
    options:
        -c <int>, --column=<int>  Column in the file with the data to be standardized.
        -m <str>, --method=<str>  Which standardization to use: standardize_address, 
                                  validate_address (with geocode), titlecase.
        --header  Input file has a header line.
```



####threshold

Threshold an image.

```
DESCRIPTION
    Usage:
        
        python threshold.py gaussian | median | mean | otsu | yen | iso [blocksize]
    
    Example:
        
        cat input.png | python threshold.py gaussian 40 > output.png
        
        cat input.png | python threshold.py otsu > output.png

FUNCTIONS
    run_cmd(method, block_size=40)
```



####util

Utilities


```
FUNCTIONS
    checkDates(dates)
        Validate a list of dates.
    
    checkInts(ints)
        Validate a list of integers.
    
    dataAtHocrBboxes(bboxes, htmlpath, returnFirstWord=False)
        Get text from HOCR within a list of bounding boxes.
    
    downloadBinary(url, filename)
        Download a file.
    
    fuzzySplit(s, d)
        Split on a delimiter that may be in the wrong place.
    
    hocrWordCoordsMultiple(words, hocr)
        Get any of a list of words from HOCR with bounding box.
    
    inside(bbox, word, page)
        Check to see if a word is inside a bounding box (lxml style bounding boxes).
    
    pdfToText(filename)
        Convert a text-based PDF to HTML.
```


