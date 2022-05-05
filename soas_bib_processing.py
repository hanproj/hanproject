#! C:\Python36\
# -*- encoding: utf-8 -*-

import os

from py3_outlier_utils import readlines_of_utf8_file
from py3_outlier_utils import get_data_from_pos
from py3_outlier_utils import readlines_of_utf8_file
from py3_outlier_utils import append_line_to_utf8_file

def get_hanproject_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code', 'hanproject')

def test_create_article_entry():
    funct_name = 'test_create_article_entry()'
    print('Welcome to ' + funct_name)
    #line_data = 'A|Boucher, D.| 1998.| Gāndhārī and the Early Chinese Buddhist Translations Reconsidered.| J. of the Am. Orient. Soc.|118|: 471-506.'
    #line_data = 'A|van Ess, H.|2003.| An Interpretation of the Shenwu fu of Tomb No. 6, Yinwan.| Monumenta Serica| 51| 605-28.'
    #line_data = 'A|Zacchetti, S.| 2010.| Defining An Shigao\'s 安世高 Translation Corpus.| Hist. & philol. stud. of China\'s west. reg.| 3|:249-270.'
    # proceedings:
    #line_data = 'P|Hewson, J. |1977.| Reconstructing Prehistoric Languages on the Computer.| Proc. of the 4th Int. Conf. on Comput.Linguist.|| 263-73.'
    #line_data = 'A|Gong, X. and Y. Lai.| 2017.| Consonant Clusters.| Sybesma, R. ed., |Encycl. of Chin. Lang. and Linguist.|1|. 665-672.'
    #line_data = 'B|Hayashi, H.| 2015. |漢三国西晉鏡銘集成. |Yokohama: |横浜ユーラシア文化館.'
    line_data_list = ['B|Hill, N.| 2019.| The Historical Phonology of Tibetan, Burmese, and Chinese. |Cambridge:| Cambridge Univ. Press.',
                      'B|Caldwell, E. |2018. |Writing Chinese Laws. |Abingdon: |Routledge',
                      'B|Hunter, M. |2017. |Confucius Beyond the Analects.| Leiden: |Brill',
                      'B|Barbieri-Low, A. J., and R. S. Yates. |2015.| Law, State, and Society in Early Imperial China. |Leiden: |Brill',
                      'B|Lu Q.| 1983. |先秦漢魏晉南北朝詩. |Beijing: |中華書局.']
    for line_data in line_data_list:
        if line_data.split('|')[0] == 'A':
            print('processing article...')
            create_article_entry(line_data)
        elif line_data.split('|')[0] == 'B':
            print('processing book...')
            print(line_data)
            create_book_entry(line_data)

def remove_ending_x_if_there_is_one(line, x):
    retval = ''
    if line and line[len(line)-1] == x:
        retval = line[0:len(line)-1]
    return retval

def create_book_entry(line_data):
    funct_name = 'create_book_entry()'
    #B|Hayashi, H.| 2015. |漢三国西晉鏡銘集成. |Yokohama: |横浜ユーラシア文化館.
    comment = '%' + line_data[1:len(line_data)].replace('|','')
    bk_author_pos = 1
    bk_year_pos = 2
    bk_title_pos = 3
    bk_address_pos = 4
    bk_publisher_pos = 5
    line_data = line_data.split('|')
    author = line_data[bk_author_pos].strip()
    year = remove_ending_x_if_there_is_one(line_data[bk_year_pos].strip(), '.')
    title = remove_ending_x_if_there_is_one(line_data[bk_title_pos].strip(), '.')
    address = remove_ending_x_if_there_is_one(line_data[bk_address_pos].strip(), ':')

    publisher = remove_ending_x_if_there_is_one(line_data[bk_publisher_pos].strip(),'.')
    print('INPUT: \n' + '|'.join(line_data))
    print('OUTPUT: \n\tAuthor = ' + author + ', Year = ' + year + ', Title = ' + title + ', Address = ' + address + ', Pub = ' + publisher)
    #@Book{Frasch1996,
  #author    = {Frasch, Tilman},
  #title     = {Pagan: Stadt und Staat},
  #publisher = {F. Steiner},
  #address   = {Stuttgart},
  #groups    = {Imported Asia.txt},
  #year      = {1996},
  #}
    #
    # create output
    retval = []
    retval.append(comment)
    code = author.split(',')[0] + year

    # %Hayashi, H. 2015. 漢三国西晉鏡銘集成. Yokohama: 横浜ユーラシア文化館.
    #@Article{karashima2009,
    retval.append('@Book{' + code + ',')
    #  author   = {Hayashi, H},
    retval.append('  author   = {' + author + '},')
    #  title    = {漢三国西晉鏡銘集成},
    retval.append('  title    = {' + title + '},')
    #  publisher = {横浜ユーラシア文化館},
    retval.append('  publisher = {' + publisher + '},')
    #  address   = {Yokohama},
    retval.append('  address   = {' + address + '},')
    #  groups     = {},
    retval.append('  groups    = {},')
    #  year      = {2015},
    retval.append('  year      = {' + year + '},')
    retval.append('}')
    print('\n'.join(retval))

def create_article_entry(line_data):
    funct_name = 'create_article_entry()'
    art_author_pos = 1
    art_year_pos = 2
    art_title_pos = 3
    art_journal_pos = 4
    art_vol_pos = 5
    art_pages_pos = 6
    comment = '%' + line_data.replace('|','')[1:len(line_data)]
    line_data = line_data.split('|')
    author = line_data[art_author_pos].strip()
    year = remove_ending_x_if_there_is_one(line_data[art_year_pos].strip(), '.')
    #year = year.replace('.','')
    title = remove_ending_x_if_there_is_one(line_data[art_title_pos].strip(), '.')
    journal = line_data[art_journal_pos].strip()
    volume = line_data[art_vol_pos].strip()
    pages = line_data[art_pages_pos].strip()
    pages = remove_ending_x_if_there_is_one(pages.replace(':', ''), '.').strip()
    print('INPUT: \n' + '|'.join(line_data))
    omsg = 'OUTPUT: \n\tAuthor\t= ' + author + ',\n\tYear =\t' + year + ',\n\tTitle =\t' + title + ',\n\tJournal =\t' + journal
    omsg += '\n\tVol =\t' + volume + ',\n\tPages =\t' + pages
    #print(omsg)
    #
    # create output
    retval = []
    retval.append(comment)
    code = author.split(',')[0] + year
    #% Karashima, S. 2009. 漢譯佛典的語言研究. 佛教漢語研究, 朱庆之 ed. Bejing: 北京商務印書館, pp. 50-51.
    #@Article{karashima2009,
    retval.append('@Article{' + code + ',')
    #  author   = {Karashima, Seishi \zh{辛嶋靜志}},
    retval.append('  author   = {' + author + '},')
    #  title    = {漢譯佛典的語言研究},
    retval.append('  title    = {' + title + '},')
    #  issn     = {},
    retval.append('  issn     = {},')
    #  number   = {},
    retval.append('  number   = {},')
    #  pages    = {50-51},
    retval.append('  pages    = {' + pages + '},')
    #  url      = {},retval
    retval.append('  url      = {},')
    #  volume   = {},
    retval.append('  volume   = {' + volume + '},')
    #  abstract = {},
    retval.append('  abstract = {},')
    #  groups   = {},
    retval.append('  groups   = {},')
    #  journal  = {佛教漢語研究},
    retval.append('  journal  = {' + journal + '},')
    #  year     = {2009},
    retval.append('  year     = {' + year + '},')
    retval.append('}')
    print('\n'.join(retval))

def test_print_comment_lines_only():
    funct_name = 'test_print_comment_lines_only()'
    bib_file = os.path.join(get_hanproject_dir(), 'han.bib')
    #print_comment_lines_only(bib_file)
    print_comment_line_n_related_entry(bib_file)

def print_comment_line_n_related_entry(bib_file):
    funct_name = 'print_comment_line_n_related_entry()'
    if not os.path.isfile(bib_file):
        print(funct_name + ' ERROR: Invalid input file:')
        print('\t' + bib_file)
        print('Skipping.')
        return
    line_data = readlines_of_utf8_file(bib_file)
    start_entry = False
    for ld in line_data:
        ld = ld.strip()
        if ld and ld[0] == '%':
            print(ld)
            start_entry = True
            continue
        if start_entry and ld:
            print(ld)
            if ld == '}':
                print('')
        else:
            start_entry = False
            #print('')


def print_comment_lines_only(bib_file):
    funct_name = 'print_comment_lines_only()'
    if not os.path.isfile(bib_file):
        print(funct_name + ' ERROR: Invalid input file:')
        print('\t' + bib_file)
        print('Skipping.')
        return
    line_data = readlines_of_utf8_file(bib_file)
    for ld in line_data:
        ld = ld.strip()
        if ld and ld[0] == '%':
            print(ld)

test_print_comment_lines_only()
#test_create_article_entry()