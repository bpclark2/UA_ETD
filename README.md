# UA_ETD
Python scripts and MarcEdit files used by The University of Alabama Libraries for processing ETDs.

Run scripts in the following order:
1. preprocess-etds.py - unzips and moves content to appropriate directories in staging area
2. process-etds.py (etdDict.py must be in the same directory as process-etds.py) - extracts data from PQ XML, calculates embargo lift, matches content files to metadata, and write this data to a CSV in preparation for packaging with dspace-csv-archive-for-etd-master
3. dspace-csv-archive-for-etd-master (see readme in this directory) - modified version of DSpace CSV Archive (https://github.com/lib-uoguelph-ca/dspace-csv-archive) for ETDs.
4. preprocess-marc-etds.py - run this script on CSV of exported metadata from IR ETD collection after depositing batch. Prepares a tab-delimited text file that will then be translated into MARC records with Marc Edit.
5. MarcEdit - directory contains a mapping file used to map metadata fields in the tab-delimited text file created by preprocess-marc.py to MARC fields. The task list is used on the resulting .mrk file for additional cleanup before compiling to .mrc.
