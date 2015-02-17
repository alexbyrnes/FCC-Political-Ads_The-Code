python pq.py printParallelParams --targetfield="invoice" | parallel --colsep='\t' 'pdfinfo {1} | grep Pages: | sed -e s/Pages://g | tr -s " " "\t" | sed -e s/^/{1/.}\\t/g' 
