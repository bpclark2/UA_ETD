################################################################
# Date Created: February 2024
# Developer: Brian Clark
# Description: For ETD processing. Extracts and modifies selected
# data from PQ metadata records, adds constant data,
# supplementary files, and calculates date of embargo lift.
#################################################################

import csv, re
from xml.etree import ElementTree as ET
from datetime import date
from dateutil.relativedelta import relativedelta
from etdDict import dept_dict, degree_dict
import os

#get date batch was delivered by ProQuest
deposit_date = input('when was this batch delivered? (yyyy-mm-dd): ')
deposit_date_split = deposit_date.split('-')

#create output CSV file and write first row of headers.
with open('S:/Metadata/ETD/content/dc-etds.csv', 'w', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
    headers = ['dc.date.available', 'dc.identifier.other', 'files', 'dc.contributor.author', 'etdms.degree.name', 'etdms.degree.level',
               'etdms.degree.department', 'etdms.degree.grantor',
               'dc.title en_US', 'dc.date.issued', 'dc.contributor.advisor', 'dc.contributor',
               'etdms.degree.discipline', 'dc.description.abstract en_US',
               'dc.relation.ispartof', 'dc.description en_US', 'dc.type', 'dc.language', 'dc.language.iso',
               'dc.format.mimetype', 'dc.rights en_US', 'dc.format.medium',
               'dc.publisher', 'dc.relation.hasversion', 'dc.subject']
    csv_writer.writerow(headers)

    #set directories in staging area
    start_dir = 'S:/Metadata/ETD/new_batch/extracted'
    content_dir = 'S:/Metadata/ETD/content'
    for subdir in os.listdir(start_dir):
        files = [f for f in os.listdir(f'{start_dir}/{subdir}')] #list files in each ETD folder
        for i in files:
            if '_DATA.xml' in i:
                with open(f'{start_dir}/{subdir}/{i}', 'r', encoding='utf-8') as f: #open and parse XML metadata record
                    tree = ET.parse(f)
                    record = tree.getroot()
                    #calculate date of embargo lift
                    embargo_code = record.get('embargo_code')
                    if embargo_code == '0':
                        date_available = ''
                    if embargo_code == '1':
                        date_available = str(date(int(deposit_date_split[0]), int(deposit_date_split[1]), int(deposit_date_split[2])) + relativedelta(months=6))
                    if embargo_code == '2':
                        date_available = str(date(int(deposit_date_split[0]), int(deposit_date_split[1]), int(deposit_date_split[2])) + relativedelta(years=1))
                    if embargo_code == '3':
                        date_available = str(date(int(deposit_date_split[0]), int(deposit_date_split[1]), int(deposit_date_split[2])) + relativedelta(years=3))
                    if embargo_code == '4':
                        date_available = str(date(int(deposit_date_split[0]), int(deposit_date_split[1]), int(deposit_date_split[2])) + relativedelta(years=5))

                    #set empty lists for metadata elements that may have multiple values.
                    committee = []
                    advisors = []
                    abstract = []
                    keywords = []
                    content = []

                    #match content files with metadata on the PQ identifier
                    pq_id = i.replace('_DATA.xml', '')
                    for x in os.listdir(content_dir):
                        if pq_id in x:
                            content.append(x)
                    content_files = '||'.join(content)

                    #format author name
                    for name_node in record.iterfind('.//DISS_author/DISS_name'):
                        surname, fname, middle, suffix = name_node
                        name_str = f'{surname.text.strip().title()}, {fname.text.strip().title()}'
                        name_str_replaced = re.sub('Mc[a-z]', f'{name_str[:2]}{name_str[2].upper()}', name_str)
                        author_name_str_replaced2 = re.sub('Mac[a-z]', f'{name_str_replaced[:3]}{name_str_replaced[3].upper()}', name_str_replaced)
                        if middle.text:
                            author_name_str_replaced2 += f' {middle.text.strip().title()}'
                        if suffix.text:
                            author_name_str_replaced2 += f', {suffix.text.strip().title()}'
                    degree = record.find('.//DISS_degree').text #degree name
                    degree_type = degree_dict[degree] #pass degree name to degree dictionary to get degree level
                    dept = record.find('.//DISS_inst_contact').text #department name
                    dept_heading = dept_dict[dept] #pass department name to department dictionary to get full authorized form
                    #extract title, convert to title case, and replace aconyms and initialisms
                    etd_title = record.find('.//DISS_title').text.strip().title().replace(' The ', ' the ').replace(' A ', ' a ').replace(' An ', ' an ').replace(' On ', ' on ')\
                        .replace(' Of ', ' of ').replace(' For ', ' for ').replace(' In ', ' in ').replace(' To ', ' to ').replace(' By ', ' by ').replace(' Its ', ' its ').replace(' With ', ' with ')\
                        .replace(' Within ', ' within ').replace(' Into ', ' into ').replace(' And ', ' and ').replace('Covid', 'COVID').replace(' Esl ', ' ESL ').replace("'S ", "'s ")\
                        .replace(' Usa ', ' USA ').replace('’', "'").replace('Co2', 'CO2').replace(' From ', ' from ').replace(" Ain'T ", " ain't ").replace('Lgbtqia+', 'LGBTQIA+').replace('Lgbt', 'LGBT')\
                        .replace(' Not ', ' not ').replace(' Is ', ' is ').replace(' Al ', ' AL ').replace('Bce', 'BCE').replace(' Without ', ' without ').replace("'S", "'s")
                    diss_date = record.find('.//DISS_comp_date').text.strip().split('-')[0] #year degree conferred
                    #format advisor name
                    for name_node in record.iterfind('.//DISS_advisor/DISS_name'):
                        surname, fname, middle = name_node
                        name_str = f'{surname.text.strip().title()}, {fname.text.strip().title()}'
                        name_str_replaced = re.sub('Mc[a-z]', f'{name_str[:2]}{name_str[2].upper()}', name_str)
                        name_str_replaced2 = re.sub('Mac[a-z]', f'{name_str_replaced[:3]}{name_str_replaced[3].upper()}', name_str_replaced)
                        if middle.text:
                            name_str_replaced2 += f' {middle.text.strip().title()}'
                        advisors.append(name_str_replaced2)
                    advisors_string = '||'.join(advisors)
                    #format committee names
                    for name_node in record.iterfind('.//DISS_cmte_member/DISS_name'):
                        surname, fname, middle, suffix = name_node
                        name_str = f'{surname.text.strip().title()}, {fname.text.strip().title()}'
                        name_str_replaced = re.sub('Mc[a-z]', f'{name_str[:2]}{name_str[2].upper()}', name_str)
                        name_str_replaced2 = re.sub('Mac[a-z]', f'{name_str_replaced[:3]}{name_str_replaced[3].upper()}', name_str_replaced)
                        if middle.text:
                            name_str_replaced2 += f' {middle.text.strip().title()}'
                        if suffix.text:
                            name_str_replaced2 += f', {suffix.text.strip().title()}'
                        committee.append(name_str_replaced2)
                    committee_string = '||'.join(committee)
                    discipline = record.find('.//DISS_cat_desc').text.replace('&amp;', '&') #value for etdms.degree.discipline
                    #format abstract
                    abstract_paragraphs = record.findall('.//DISS_para')
                    for t in abstract_paragraphs:
                        abstract_para_text = t.text.strip().replace('\t', '').replace('\n', '').replace('\r', '')
                        abstract.append(abstract_para_text)
                    abstract_paras_string = ' '.join(abstract)
                    #create output row, add constant data
                    row = [date_available, pq_id, content_files, author_name_str_replaced2, degree, degree_type, dept_heading, 'The University of Alabama', etd_title,
                           diss_date, advisors_string, committee_string, discipline, abstract_paras_string,
                           'The University of Alabama Electronic Theses and Dissertations||The University of Alabama Libraries Digital Collections',
                           'Electronic Thesis or Dissertation', 'thesis||text', 'English', 'en_US', 'application/pdf',
                           'All rights reserved by the author unless otherwise indicated.', 'electronic', 'University of Alabama Libraries', 'born digital']
                    #format keywords
                    keywords = record.find('DISS_description/DISS_categorization/DISS_keyword').text or ''
                    if keywords != '':
                        keywords_formatted = (keywords.replace(', ', '||'))
                        row.append(keywords_formatted)
                    else:
                        row.append('')
                    #write to output file
                    csv_writer.writerow(row)