################################################################
# Date Created: February 2024
# Developer: Brian Clark
# Description: For ETD processing. Run this script after moving
# a new batch of ETDs to the staging area. Unzips and moves
# content to appropriate directory.
#################################################################

import os
import zipfile
import shutil

#set directory locations in the staging area
rootdir = 'S:/Metadata/ETD/new_batch'
extracted_dir = f'{rootdir}/extracted'
content_dir = 'S:/Metadata/ETD/content'

#unzip ETDs and save in S:/Metadata/ETD/new_batch/extracted
for subdir in os.listdir(rootdir):
    with zipfile.ZipFile(f'{rootdir}/{subdir}', 'r') as zip_ref:
        zip_ref.extractall(f'{extracted_dir}/{subdir}'.replace('etdadmin_upload_', '').replace('.zip', ''))

for subdir in os.listdir(f'{extracted_dir}'):
    files = [f for f in os.listdir(f'{extracted_dir}/{subdir}')] #list files in the unzipped ETD folder
    if any('.pdf' in l for l in files) is False: #check for PDF
        print(f'{subdir} missing PDF!')
    if any('_DATA.xml' in l for l in files) is False: #check for XML
        print(f'{subdir} missing metadata file!')
    
    #rename XML metadata files with the ProQuest identifier
    #rename ETD PDFs and supplementary files and folders with the ProQuest identifier and move to the content directory
    x=1
    for i in files:
        if '_DATA.xml' in i:
            filename = os.rename(f'{extracted_dir}/{subdir}/{i}', f'{extracted_dir}/{subdir}/{subdir}_DATA.xml')
        elif '.pdf' in i:
            filename = os.rename(f'{extracted_dir}/{subdir}/{i}', f'{extracted_dir}/{subdir}/{subdir}.pdf')
            shutil.copyfile(f'{extracted_dir}/{subdir}/{subdir}.pdf', f'{content_dir}/{subdir}.pdf')
        elif '.' in i:
            extension = i.split('.')[1]
            filename = os.rename(f'{extracted_dir}/{subdir}/{i}', f'{extracted_dir}/{subdir}/{subdir}_{x}.{extension}')
            if os.path.isfile(f'{extracted_dir}/{subdir}/{subdir}_{x}.{extension}') is True:
                shutil.copyfile(f'{extracted_dir}/{subdir}/{subdir}_{x}.{extension}', f'{content_dir}/{subdir}_{x}.{extension}')
            elif os.path.isdir(f'{extracted_dir}/{subdir}/{subdir}_{x}.{extension}') is True:
                zipped = shutil.make_archive(f'{extracted_dir}/{subdir}/{subdir}_{x}.{extension}', 'zip', f'{content_dir}/{subdir}_{x}.{extension}')
                shutil.move(zipped, content_dir)
            x+=1
        else:
            filename = os.rename(f'{extracted_dir}/{subdir}/{i}', f'{extracted_dir}/{subdir}/{subdir}_{x}')
            if os.path.isfile(f'{extracted_dir}/{subdir}/{subdir}_{x}') is True:
                shutil.copyfile(f'{extracted_dir}/{subdir}/{subdir}_{x}', f'{content_dir}/{subdir}{subdir}_{x}')
            elif os.path.isdir(f'{extracted_dir}/{subdir}/{subdir}_{x}') is True:
                zipped = shutil.make_archive(f'{extracted_dir}/{subdir}/{subdir}_{x}', 'zip', f'{extracted_dir}/{subdir}/{subdir}_{x}')
                shutil.move(zipped, content_dir)
            x+=1