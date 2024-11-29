################################################################
# Date Created: February 2024
# Developer: Brian Clark
# Description: For ETD processing. Run this script using exported
# metadata from IR ETD collection after archiving a new batch.
# Prepares IR metadata for MARC transformation and writes data to
# a tab-delimited text file.
#################################################################

import csv
from operator import itemgetter

marc = open('S://Metadata//ETD//new_batch//marc-etds.txt', 'w', encoding='utf-8')
marc_writer = csv.writer(marc, delimiter='\t', lineterminator='\n')

metadata = input('Enter the filepath of the IR metadata CSV file: ').replace('"', '')
batch_date = input('Enter the date the batch of ETDs was deposited into the IR (yyyy-mm-dd): ')
with open(metadata, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=',')
    tags = next(reader)
    d = dict(enumerate(tags))
    tag_pos = {v: k for k, v in d.items()}
    for row in reader:
        marc_row = []
        date_pos = itemgetter('dc.date.accessioned')(tag_pos)
        date_accessioned = row[date_pos]
        if batch_date in date_accessioned:
            handle = itemgetter('dc.identifier.uri')(tag_pos)
            marc_row.append(f'{row[handle]}$qapplication/pdf$zElectronic item available online. Click here.')
            author = itemgetter('dc.contributor.author')(tag_pos)
            marc_row.append(f'{row[author]},$eauthor')
            title = itemgetter('dc.title[en_US]')(tag_pos)
            marc_row.append(row[title].replace("’", "'").replace('“', '"').replace('—', ' - ').replace('$', '{dollar}').replace(':', ':$b', 1))
            degree = itemgetter('etdms.degree.name')(tag_pos)
            date = itemgetter('dc.date.issued')(tag_pos)
            diss_note = row[degree].replace('“', '"') + '$cUniversity of Alabama$d' + row[date]
            abstract = itemgetter('dc.description.abstract[en_US]')(tag_pos)
            marc_row.append(row[abstract].replace("’", "'").replace('“', '"').replace('—', ' - ').replace('$', '{dollar}'))
            contrib = itemgetter('etdms.degree.department')(tag_pos)
            contrib_rev = row[contrib].replace('University of Alabama. ', 'University of Alabama.$b')
            marc_row.append(contrib_rev)
            marc_row.append('Mode of access: World Wide Web.')
            marc_row.append('All rights reserved by the author unless otherwise indicated.')
            marc_row.append('thesis$2marcgt')
            marc_row.append('Electronic dissertations.')
            marc_row.append('text$btxt$2rdacontent')
            marc_row.append('computer$bc$2rdamedia')
            marc_row.append('online resource$bcr$2rdacarrier')
            marc_row.append('ALM$beng$erda$cALM')
            marc_row.append('1 volume :$bdigital, PDF file')
            marc_row.append('University of Alabama,$edegree granting institution')
            marc_row.append('cr\|n||||||n||')
            marc_row.append(f'[Tuscaloosa, Alabama] :$b[University of Alabama Libraries],$c{row[date]}')
            pq_id = itemgetter('dc.identifier.other')(tag_pos)
            marc_row.append(row[pq_id])
            subjects = itemgetter('dc.subject')(tag_pos)
            marc_row.append(row[subjects])
            marc_writer.writerow(marc_row)
    marc.close()