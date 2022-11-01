#! C:\Python36\
# -*- encoding: utf-8 -*-

import os
import codecs
import re
from pyvis.network import Network
from pyvis.options import EdgeOptions
from hanproj_filename_depot import filename_depot

filename_storage = filename_depot()
exception_chars = ['之', '兮', '乎', '也', '矣', '焉']
punctuation = ['》', '！', '？', '?', '”', '］', '＝', '『', '』', '，', '、', '×', '＊', '○', '々', '/', ' ', '…', '※',
               '（', '】']
#if '，' in marker or '、' in marker or '＊' in marker or '×' in marker or '？' in marker:
#zi == '》' or zi == '！' or zi == '？':
#IMPORTANT
# IMPORTANT when adding new initials:
# -> put normal letters after marked ones!
#    Ex. Put 'dz' AFTER 'dẓ', 'dẓ', 'dź'
lhan_initials = ['dẓ', 'dẓ', 'dź','dz', 'tś', 'tṣ', 'tṣ', 'ts', 'ḍ', 'ḍ', 'd',
                 'g', 'ɡ', 'h', 'j', 'k', 'Ɣ', 'ɣ', 'm', 'ń', 'ṇ', 'ṇ', 'n',
                 'ŋ', 'b', 'p', 'r', 'ṣ', 'ś', 's', 'ṭ', 'ṭ', 't', 'x','ź',
                 'z', 'l', 'ʔ', 'Ɂ']
aspiration = 'ʰ'
zero_initial = '∅'
post_codas = ['s', 'h', 'ʔ', 'Ɂ', 'ᶜ', 'ᴮ']
tones = ['ᵃ','ᴮ','ᶜ','ᵈ']
utf8_bom_b = b'\xef\xbb\xbf'

lh_main_vowels = ['i', 'ɨ', 'y', 'u', 'e', 'o', 'ɑ', 'a', 'ə', 'ɛ', 'ɔ']
lh_medials = ['i', 'ɨ', 'y', 'u', 'w']


#def get_combo_data_community_detection_results_file():
#
# Data format:
# 321	1	0.010677134257491647	明
# Where:
#   321 - original node number
#   1 - group number
#   0.010677134257491647 - node weight
#   明 - label
#def get_com_det_group_descriptions_for_combo_data():
#    return os.path.join(get_hanproj_dir(), 'hanproject', 'com_detection_combined_data_output.txt')

schuessler = ''
def load_schuessler_data():
    global schuessler
    if schuessler:
        return
    schuessler = sch_glyph2phonology()

def get_schuessler_late_han_for_glyph(glyph):
    load_schuessler_data()
    return schuessler.get_late_han(glyph)

def get_late_han_rhyme_for_glyph(glyph):
    lhan = get_schuessler_late_han_for_glyph(glyph)
    retval = []
    if ' ' in lhan:
        lhan.split(' ')
    else:
        lhan = [lhan]
        for lh in lhan:
            #initial, medial, rhyme, pcoda = parse_schuessler_late_han_syllable(lh)
            rhyme = parse_schuessler_late_han_syllable(lh)
            if rhyme not in retval:
                retval.append(rhyme)
    return retval

def is_this_the_initial(pinitial, reco):
    return pinitial == reco[0:len(pinitial)]

def get_rhyme_from_late_han(lhan): # takes single fayin input as string
    if lhan == 'N':
        return ''
    #initial, medial, retval, pcoda = parse_schuessler_late_han_syllable(lhan)
    retval = get_rhyme_from_schuessler_late_han_syllable(lhan)
    return retval

def parse_schuessler_ocm_syllable(reco): # takes string as input
    funct_name = 'parse_schuessler_ocm_syllable()'
    initial = ''
    if not reco.strip():
        return '', '', '', ''
    if aspiration in reco:
        initial = reco.split(aspiration)[0] + aspiration
    else:
        for pi in lhan_initials:
            if is_this_the_initial(pi, reco):
                initial = pi
                break
    if not initial.strip():
        if reco[0] == 'w' or reco[0] == 'a':
            initial = zero_initial
        else:
            initial = 'X'
    final = reco[len(initial):len(reco)]
    # if there is a medial, remove it from the final
    medial = ''
    try:
        x = final[0]
    except IndexError as ie:
        x = 1
    try:
        x = final[0]
    except IndexError as ie:
        x = 1
    if final[0] in lh_medials:
        try:
            if final[1] in lh_main_vowels:
                medial = final[0]
                final = final[1:len(final)]
        except:
            x = 1
    pcoda = ''
    if final[len(final)-1] in post_codas:
        pcoda = final[len(final)-1]
        final = final[0:len(final)-1]
        x = 1
         # if final[0] is in the medials AND
        #  final[1] is in the main vowels, then final[0] IS a medial
    return initial, medial, final, pcoda

def get_soas_code_dir():
    return os.path.join('D:' + os.sep + 'Ash', 'SOAS', 'code')

def get_phonological_data_dir():
    return os.path.join(filename_storage.get_hanproj_dir(), 'phonological_data')

def if_file_exists(filename, funct_name):
    retval = False
    if os.path.isfile(filename):
        retval = True
    else:
        print(funct_name + ' ERROR: Invalid input file:  ' + filename)
    return retval

def get_hanproj_dir():
    return filename_storage.get_hanproj_dir()

def readin_most_complete_schuessler_data():
    funct_name = 'readin_most_complete_schuessler_data()'
    input_file = os.path.join(filename_storage.get_phonological_data_dir(), 'most_complete_schuessler_late_han_data.txt')
    if not if_file_exists(input_file, funct_name):
        return []
    data = readlines_of_utf8_file(input_file)
    retval = {}
    for d in data:
        d = d.split('\t')
        if d[0] not in retval:
            retval[d[0]] = []
        retval[d[0]].append(d[1])
    return retval

def readlines_of_utf8_file(filename):
    funct_name = 'readlines_of_utf8_file()'
    retval = []
    if not os.path.isfile(filename):
        print(funct_name + u' ERROR: filename INVALID: ' + filename)
        return retval
    with open(filename, 'rb') as f:
        line_list = f.readlines()
    line_list[0] = line_list[0].replace(utf8_bom_b, b'')
    for line in line_list:
        line = line.decode('utf8')
        line = line.replace('\r\n', '')
        line = line.replace('\n', '')
        retval.append(line)
    return retval

def cleanup_ocm_ipa(ocm):
    if ' ~ ' in ocm:
        ocm = ocm.replace(' ~ ', ' ')  # just treat each one as a possibility
    if ' ?' in ocm:
        ocm = ocm.replace(' ?','')
    if '?' in ocm:
        ocm = ocm.replace('?', '')
    #if '(' not in ocm and ' or ' in ocm:
    #    ocm = ocm.replace(' or ', ' ')
    if ' (or ' in ocm:
        ocm = ocm.replace(' (or ', ' ')
        ocm = ocm.replace(')','')
    if ' or ' in ocm:
        ocm = ocm.replace(' or ', ' ')
    if ' (etc.)' in ocm:
        ocm = ocm.replace(' (etc.)','')
    if ' < ' in ocm:
        ocm = ocm.replace(' < ',' ')
    if ' (< ' in ocm:
        ocm = ocm.replace(' (< ', ' ')
    if ' >) ' in ocm:
        ocm = ocm.replace(' >) ', ' ')
        ocm = ocm.replace('(','')
    if ' > ' in ocm:
        ocm = ocm.replace(' > ', ' ')
    if ',' in ocm:
        ocm = ocm.replace(',', ' ')
    if '(prob. ' in ocm:
        ocm = ocm.replace('(prob. ', '')
        ocm = ocm.replace(')','')
    if '(i.e. ' in ocm:
        ocm = ocm.replace('(i.e. ', '')
        ocm = ocm.replace(')', '')
    if ' (= ' in ocm:
        ocm = ocm.replace(' (= ',' ')
        ocm = ocm.replace(')','')
    if '瞑' in ocm:
        x = 1
    if ' (瞑)' in ocm:
        ocm = ocm.replace(' (瞑)', '')
        #handle_x_slash_y((Ɂ/h))
    ocm = handle_short_parens(ocm)
    return ocm

def distance_between_tags(start_tag, stop_tag, line):
    spos = line.find(start_tag)
    epos = line.find(stop_tag)
    retval = 0
    if not line.strip():
        return retval
    if spos > 1 and epos > 1:
        retval = epos - spos + 1
    return retval

def handle_short_parens(data):
    start_tag = '('
    stop_tag = ')'
    retval = []
    if start_tag in data and stop_tag in data:
        data = data.split(' ')
        for d in data:
            if distance_between_tags(start_tag, stop_tag, d) == 3:
                begin_syl = d.split(start_tag)[0]
                middle = d.split(start_tag)[1]
                middle = middle.split(stop_tag)[0]
                end_syl = d.split(stop_tag)[1]
                retval.append(begin_syl+end_syl)
                retval.append(begin_syl+middle+end_syl)
            else:
                retval.append(d)
        retval = list(set(retval))
    else:
        retval.append(data)
    return ' '.join(retval)

def test_find_southern_late_han_readings():
    funct_name = 'test_find_southern_late_han_readings()'
    is_verbose = True
    find_southern_late_han_readings(is_verbose)

# this function should actually be called "parse_" rather than "get_"
def find_southern_late_han_readings(is_verbose=False):
    funct_name = 'find_southern_late_han_readings()'
    addendum = readin_most_complete_schuessler_data()
    #input_file = os.path.join(get_schuesslerhanchinese_dir(), 'raw', 'SchuesslerTharsen.tsv')
    input_file = os.path.join(filename_storage.get_hanproj_dir(), 'phonological_data', 'raw', 'SchuesslerTharsen.tsv')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: INVALID input file:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    if is_verbose:
        print('LABELS:')
        print('\t' + line_list[0])
    label_list = line_list[0]
    label_list = label_list.split('\t')
    line_list = line_list[1:len(line_list)] # remove labels
    if is_verbose:
        print('FORMAT: ')
        print('\t' + line_list[0])
    format_list = line_list[0]
    ids2skip = ['553', '579', '2054', '3922']
    line_list = line_list[1:len(line_list)] # remove format
    delim = '\t'
    #southern_lhan_marker_l = [',S ', '/ S ', ', S ', '/S']
    for l in line_list:
        l = l.split(delim)
        len_l = len(l)
        ID = l[label_list.index('ID')]
        if ID in ids2skip:
            continue
        zh_ipa = l[label_list.index('pinyin_index')]
        glyph = l[label_list.index('graph')]
        if glyph == '○':
            continue
        lh_ipa = l[label_list.index('LH_IPA')] # this is a string
        if 'S' in lh_ipa:
            print(glyph + ': ' + lh_ipa)



# this function should actually be called "parse_" rather than "get_"
def get_schuessler_late_han_data(is_verbose=False):
    funct_name = 'get_schuessler_late_han_data()'
    addendum = readin_most_complete_schuessler_data()
    #input_file = os.path.join(get_schuesslerhanchinese_dir(), 'raw', 'SchuesslerTharsen.tsv')
    input_file = os.path.join(filename_storage.get_hanproj_dir(), 'phonological_data', 'raw', 'SchuesslerTharsen.tsv')
    if not os.path.isfile(input_file):
        print(funct_name + ' ERROR: INVALID input file:')
        print('\t' + input_file)
        return
    line_list = readlines_of_utf8_file(input_file)
    if is_verbose:
        print('LABELS:')
        print('\t' + line_list[0])
    label_list = line_list[0]
    label_list = label_list.split('\t')
    line_list = line_list[1:len(line_list)] # remove labels
    if is_verbose:
        print('FORMAT: ')
        print('\t' + line_list[0])
    format_list = line_list[0]
    line_list = line_list[1:len(line_list)] # remove format
    # ID=1298	wf_pinyin={	wf_graph={	wf_relationship={	pinyin_index=gǔ1	graph=古	QY_IPA=kuoᴮ	LH	LH_IPA=kɑᴮ	OCM	OCM_IPA=*kâɁ
    num_labels = len(label_list)
    delim = '\t'
    retval = {}
    exceptions = ['箄 and other characters', '琥珀 < 虎魄', '姮娥 ~ 恆娥', '顥[Lü],昊', '艎 / 艕', '艕,艎', '嚅唲,儒兒',
                  '娥 (in héng-é)姮娥', '梃,鋌', '於兔,於瑙', '阤,陊 (duò) (Mand. tuó), 陊 (Mand. duò)', '杝,扡', '射油']
    except_dict = {'箄 and other characters':'箄', '琥珀 < 虎魄':'琥珀,虎魄', '姮娥 ~ 恆娥':'姮娥,恆娥', '顥[Lü],昊':'顥,昊',
                   '艎 / 艕':'', '娥 (in héng-é)姮娥':'', '阤,陊 (duò) (Mand. tuó), 陊 (Mand. duò)':'阤,陊','射油':'油'}
    #data = glyph + delim + zh_ipa + delim + qy_ipa + delim + lh_ipa + delim + ocm_ipa
    #
    # these line are exceptions in the data; just handle them directly hear and skip them in the normal processing
    lines2add = {'慚':'cuō3' + delim + 'tsʰâ,dzâ' + delim + delim,
                 '貸':'dài2'+ delim + delim + delim,
                 '潏':'jué10' + delim + delim + delim,
                 '蔚':'wèi11' + delim + delim + delim}
    #
    # LHan exceptions:
    lhan_exceptions = {'痣':'tśəᶜ kiəᶜ', '躓':'ṭis', '質':'tśit', '蛭':'tet tśit ṭit', '紙':'tśiɑiɁ kiɑiɁ',
                       '植':'dźik ḍəᶜ', '培':'bə bəuᴮ', '癠':'dzei dzeiᴮ dzeiᶜ', '讙':'xyɑn xion xuɑn', '檢':'kiɑmᴮ kiamᴮ',
                       '仔':'tsiə tsiəᴮ', '洚':'goŋ gouŋ g/kɔŋᶜ', '殺':'ṣat sɛt', '謾':'mian mɑn mɑnᶜ man manᶜ',
                       '院瑗':'wanᶜ wenᶜ', '抓':'tṣauᴮ tṣauᶜ', '綴':'ṭot ṭos ṭuas ṭuat', '翠':'tsʰus tsʰuis',
                       '率':'ṣuis ṣuit luit', '潏':'kuet juit jut', '鳳':'puəmᶜ buŋᶜ mie me ŋe', '青':'tsieŋ tseŋ tsʰeŋ',
                       '蒩':'tsiɑ tsɑ tsʰiɑ', '論':'luən lun luənᶜ', '芒':'muɑŋ mɑŋ huɑŋ', '麑':'ŋe mie me',
                       '能':'nə nəŋ', '聳':'sioŋᴮ tsʰioŋᶜ tsʰoŋᶜ','竦':'sioŋᴮ tsʰioŋᶜ tsʰoŋᶜ', '醒':'seŋ seŋᴮ seŋᶜ',
                       '蹂':'ńu ńuᴮ ńuᶜ', '來':'lə mɛk','繂':'luit', '繘':'kuit wit', '澗':'nuan nuanᶜ','汏':'dɑs',
                       '鬌':'tuɑiᴮ toiᴮ tuɑᴮ','揭':'gɨat kʰias', '皎':'keiauᴮ keuᴮ', '皦':'keiauᴮ keuᴮ', '匱':'gwis',
                       '餽':'gwih gwis', '饋':'gwih gwis', '潸':'ṣanᴮ ṣɛn ṣan', '焉':'Ɂɑn Ɂiɑn', '燕':'Ɂenᶜ Ɂenᴮ',
                       '毒': 'douk douh', '剬': 'tuɑn tśuanᴮ duɑn don tśuan tśion', '差':'tṣʰɑi tṣʰɛ tṣʰai',
                       '皇': 'guɑŋ Ɣuɑŋ', '煌': 'guɑŋ Ɣuɑŋ', '牛': 'ŋiu ŋu', '葚': 'dźimᴮ źimᴮ', '實': 'dźit źit',
                       '饁': 'wɑp jɑp', '適':'tśek śek', '夫':'buɑ puɑ', '棧':'dẓanᴮ dẓɛnᶜ dẓɛnᴮ'}
    ocm_exceptions = {'九':'*kuɁ kwəɁ', '啄':'*trôk *tôs *tôh *troh', '咮':'*tôks *tôs *tôh *troh', '凡':'*bom *bam',
                      '飯':'*bans *bons *ban', '肺':'*phots *phats', '胐':'*phəiɁ *phə̂t *phuiɁ *phut',
                      '補': '*mpaɁ *mpâɁ *pâɁ', '晨': '*m-dən *dən', '荒': '*hmâŋ *hmlaŋ *hmâŋ', '利': '*rih', '遐': '*gâ',
                      '望': '*maŋᴬ', '磏': '*ram *riam', '鎌':'*ram *riam', '鋁':'*raɁ', '坻':'*dri'}

    #data = zh_ipa.strip() + delim + qy_ipa.strip() + delim + lh_ipa.strip() + delim + ocm_ipa.strip()
    left_outs2add = {'鵠':'hú gǔ' + delim + 'ɣuok kuok' + delim + 'gouk kouk' + delim + 'gûk kûk',
                     '飾':'shì' + delim + 'śjək' + delim + 'śɨk' + delim + 'lhək',
                     '葵':'kuí' + delim + 'gwi' + delim + 'gwi' + delim + 'gwi',
                     '羹':'gēng' + delim + 'kɐŋ' + delim + 'kaŋ' + delim + 'krâŋ',
                     '歇':'xiē' + delim + 'xjɐt' + delim + 'hɨɑt' + delim + 'hat',
                     '葩':'pā' + delim + 'pʰa' + delim + 'pʰa' + delim + '',
                     '桂':'guì' + delim + 'kiweiᶜ' + delim + 'kueᶜ' + delim + 'kwêh',
                     '鴦':'yāng' + delim + 'ʔjaŋ' + delim + 'ʔɨɑŋ' + delim + 'ʔɑŋ',
                     '絕':'jué' + delim + 'dzjwät' + delim + 'dzyat' + delim + 'dzot',
                     '芝':'zhī' + delim + 'tśɨ' + delim + 'tśɨ tśə' + delim + 'tə',
                     '兮':'xī' + delim + 'ɣiei' + delim + 'ɣei' + delim + 'gî',
                     '大':'dà dài' + delim + 'dâiᶜ' + delim + 'dɑs dɑh' + delim + 'dâs',
                     '返':'fǎn' + delim + 'pjwɐnᴮ' + delim + 'puɑnᴮ' + delim + 'panʔ',
                     '晚': 'wǎn' + delim + 'mjwɐnᴮ' + delim + 'muɑnᴮ' + delim + 'manʔ',
                     '憙':'xǐ' + delim + 'xjɨᴮ' + delim + 'hɨəᴮ hɨᴮ' + delim + 'həʔ',
                     '俙':'xī' + delim + 'xjei' + delim + 'hɨi' + delim + 'həi'}
    # '':'' + delim + '' + delim + '' + delim + ''
    # upside-down a - ɐ
    # funky i       - ɨ
    # phat a        - ɑ
    # umlauted a    - ä
    # tone a        - ᴬ
    # tone b        - ᴮ
    # tone c        - ᶜ
    # aspiration h  - ʰ
    # ng            - ŋ
    # glottal stop  - ʔ
    # schwa         - ə

    for k in left_outs2add:
        retval[k] = []
        retval[k].append(left_outs2add[k])
    #, '抓':''}#棧: dẓanᴮ or dẓɛnᴮ/ᶜ; 仔: tsiə(ᴮ);院: wanᶜ/wenᶜ;瑗: wanᶜ/wenᶜ; 禜: waŋ(ᶜ)
                                      #遺: wi wih wis?; 翳: Ɂei(h); 燕: Ɂenᶜ Ɂenᶜ ~ Ɂenᴮ; 剡: jamᴮ jamᴮ
    # 炫: Ɣ(u)enᶜ; 休: x(ɨ)u; 星: seŋ / S tsʰeŋ dzieŋ; 信: sinᶜ  sinᶜ; 笑: siauᶜ / S tsʰiauᶜ
    # 繘: kiut kuit ju(it -> LH	kiut (kuit),ju(i)t
    # 爰: wɑn wɑn
    #
    # process normal data
    #
    # TO DO (2022-04-14):
    #  - finish cleaning up Schuessler's Late Han data (starting with "S /":
    #     笑: tsʰiauᶜ S / siauᶜ;
    #     癬: tsʰiɑnᴮ sianᴮ S /
    #     涎: lanᴮ janᶜ zian S)
    #  - then: 望: muɑŋᴬ/ᶜ muɑŋ
    #  - 覃: dəm  jamᴮ (double space)
    #  - 說: śos śuɑs  śuat śot śos śuas (double space)
    #  - 蹂: ńu()ᴮ ńu()ᶜ; 醒: seŋ()ᴮ seŋ()ᶜ
    #  - 鉛: jyan / jon

    for k in lines2add:
        if k not in retval:
            retval[k] = []
        retval[k].append(lines2add[k])
    ids2skip = ['553', '579', '2054', '3922']
    for l in line_list:
        l = l.split(delim)
        len_l = len(l)
        ID = l[label_list.index('ID')]
        if ID in ids2skip:
            continue
        zh_ipa = l[label_list.index('pinyin_index')]
        glyph = l[label_list.index('graph')]
        if glyph == '○':
            continue

        if ',' in zh_ipa:
            zh_ipa = zh_ipa.replace(',', ' ')
            x = 1
        if '-' in zh_ipa and len(glyph) > 1:
            continue # this is a word with more than one syllable

        if is_verbose:
            print('ID=' + ID + ', glyph=' + glyph)
        if len(glyph) > 1:
            if glyph in except_dict: # these entries are handled above
                glyph = except_dict[glyph]
                if not glyph.strip():
                    zh_ipa = ''
                    continue
        qy_ipa = l[label_list.index('QY_IPA')]
        lh_ipa = l[label_list.index('LH_IPA')] # this is a string
        if not lh_ipa.strip():
            if glyph in addendum:
                lh_ipa = addendum[glyph]
                x = 1
        #if glyph == '繘' or '繂' in glyph:
        #    x = 1
        lh_ipa = cleanup_late_han_ipa(lh_ipa)
        ocm_ipa = l[label_list.index('OCM_IPA')]
        ocm_ipa = cleanup_ocm_ipa(ocm_ipa)
        if ',' in glyph:
            for g in glyph.split(','):
                if g in lhan_exceptions:
                    lh_ipa = lhan_exceptions[g]
                if g in ocm_exceptions:
                    ocm_ipa = ocm_exceptions[g]
                if '  ' in lh_ipa:
                    lh_ipa = lh_ipa.replace('  ',' ')
                if g == '坐':
                    x = 1
                data = zh_ipa.strip() + delim + qy_ipa.strip() + delim + lh_ipa.strip() + delim + ocm_ipa.strip()
                if g not in retval:
                    retval[g] = []
                if g == '片':
                    y = retval[g]
                    x = 1
                if data not in retval[g]:
                    if '  ' in data: # debug only
                        x = 1# debug only
                    retval[g].append(data)
        else:
            glyph = list(glyph)
            for g in glyph:
                if g in lhan_exceptions:
                    lh_ipa = lhan_exceptions[g]
                if g in ocm_exceptions:
                    ocm_ipa = ocm_exceptions[g]

                if '  ' in lh_ipa:
                    lh_ipa = lh_ipa.replace('  ',' ')
                if g == '坐':
                    x = 1
                data = zh_ipa.strip() + delim + qy_ipa.strip() + delim + lh_ipa.strip() + delim + ocm_ipa.strip()
                if is_verbose:
                    print('glyph=' + g)
                if g not in retval:
                    retval[g] = []
                if g == '片':
                    y = retval[g]
                    x = 1 # '率' made it here, 4x
                if data not in retval[g]:
                    if '  ' in data: # debug
                        x = 1 # debug
                    retval[g].append(data)
    # correct exceptions
    if '摳' in retval:
        retval['摳'] = 'kʰo kʰuo'
    if '揗' in retval:
        retval['揗'] = 'źuinᴮ źuinᶜ'
    if '燁' in retval:
        retval['燁'] = 'wap jəp'
    if '晨' in retval:
        retval['晨'] = 'dźin źin'
    return retval

def remove_dupes(data):
    try:
        data = data.split(' ')
    except AttributeError:
        x = 1 # if this error happpens, then 'data' is a list
    if len(data) > 1:
        x = 1
    data = list(set(data))
    retval = ' '.join(data)
    return retval

def handle_x_slash_y(line, x, y):
    line = line.split(' ')
    retval = ''
    for e in line:
        if x + '/' + y in e:
            base = e.replace(x + '/' + y, '')
            retval += base + x + ' ' + base + y + ' '
        else:
            retval += e + ' '
    return retval.strip()

#'donᴮ/ᶜ duɑnᴮ/ᶜᴬ'
def handle_a_slash_c(line):
    return handle_x_slash_y(line, 'ᴬ', 'ᶜ')
def handle_b_slash_c(line):
    return handle_x_slash_y(line,'ᴮ', 'ᶜ')

def handle_paren_b(line):
    return handle_paren_x(line, '(ᴮ)')

def handle_paren_c(line):
    return handle_paren_x(line, '(ᶜ)')

def handle_paren_x(line, x):
    line = line.split(' ')
    retval = ''
    for e in line:
        if x in e:
            base = e.replace(x, '')
            xp = x.replace('(','')
            xp = xp.replace(')', '')
            retval += base + ' ' + base + xp + ' '
        else:
            retval += e + ''
    return retval.strip()

def cleanup_late_han_ipa(lh_ipa):
    #if str(type(lh_ipa)) == 'str':
    #    lh_ipa = [lh_ipa]
    #for lh_ipa_e in lh_ipa:
    if 'or' in lh_ipa:
        if ' or ' in lh_ipa:
            lh_ipa = lh_ipa.replace(' or ', ' ')
        if 'or ' == lh_ipa[0:2+1]:
            lh_ipa = lh_ipa[2+1:len(lh_ipa)]
        if ' or' == lh_ipa[len(lh_ipa) - 3:len(lh_ipa)]:
            lh_ipa = lh_ipa[0:len(lh_ipa) - 3]
    if '?' in lh_ipa:
        lh_ipa = lh_ipa.replace('?', '')
    if ' ~ ' in lh_ipa:
        lh_ipa = lh_ipa.replace(' ~ ', ' ')  # just treat each one as a possibility
    if ',' in lh_ipa:
        lh_ipa = lh_ipa.replace(',', ' ')
    if ' < ' in lh_ipa:
        lh_ipa = lh_ipa.replace(' < ', ' ')  # just treat each one as a possibility
    if ' (> ' in lh_ipa:
        lh_ipa = lh_ipa.replace(' (> ', ' ')
        lh_ipa = lh_ipa.replace(')', '')
        lh_ipa = lh_ipa.replace('  ', '')
    if ' > ' in lh_ipa:
        lh_ipa = lh_ipa.replace(' > ', ' ')  # just treat each one as a possibility
    if '> ' in lh_ipa:
        if '> ' == lh_ipa[0:2]:
            lh_ipa = lh_ipa[2:len(lh_ipa)]
    if ' ?' in lh_ipa:
        lh_ipa = lh_ipa.replace(' ?', '')
    if ' (' in lh_ipa:
        lh_ipa = lh_ipa.replace(' (', ' ')
        lh_ipa = lh_ipa.replace(')', '')
    if ' MHan' in lh_ipa:
        lh_ipa = lh_ipa.replace(' MHan', '')
    if '/S ' in lh_ipa:
        lh_ipa = lh_ipa.replace('/S ', ' ')
        lh_ipa = lh_ipa.replace('  ', ' ')
    if 'S ' in lh_ipa:
        lh_ipa = lh_ipa.replace('S ', ' ')
        lh_ipa = lh_ipa.replace('  ', ' ')
    lh_ipa = remove_dupes(lh_ipa)
    # piaŋᴮ/ᶜ
    if 'ᴮ/ᶜ' in lh_ipa:
        lh_ipa = handle_b_slash_c(lh_ipa)
    if 'ᴬ/ᶜ' in lh_ipa:
        lh_ipa = handle_a_slash_c(lh_ipa)
    if '(ᶜ)' in lh_ipa:  # need one for (ᴮ) as well
        lh_ipa = handle_paren_c(lh_ipa)
    if '(ᴮ)' in lh_ipa:
        lh_ipa = handle_paren_b(lh_ipa)
    if '(Ɂ)' in lh_ipa:
        lh_ipa = handle_paren_x(lh_ipa, '(Ɂ)')
    if '(h)' in lh_ipa:
        lh_ipa = handle_paren_x(lh_ipa, '(h)')
    if '/' in lh_ipa:
        x = 1
        lh_ipa = lh_ipa.replace(' / ', ' ')
        lh_ipa = lh_ipa.replace('  ', ' ')
        if '/ ' == lh_ipa[0:2]:
            lh_ipa = lh_ipa[2:len(lh_ipa)]
        if '/ ' == lh_ipa[len(lh_ipa) - 2:len(lh_ipa)] or ' /' == lh_ipa[len(lh_ipa) - 2:len(lh_ipa)]:
            lh_ipa = lh_ipa[0:len(lh_ipa) - 2]
    return lh_ipa

# def get_schuessler_item_given_label(line, label, label_list):
class sch_glyph2phonology:
    def __init__(self):
        self.glyph2data = get_schuessler_late_han_data()
        # data = zh_ipa + delim + qy_ipa + delim + lh_ipa + delim + ocm_ipa
        self.mandarin_pos = 0
        self.qieyun_pos = 1
        self.late_han_pos = 2
        self.min_oc_pos = 3

    def print_all_data(self):
        for k in self.glyph2data:
            print('glyph2data[' + k + '] = ' + '\n'.join(self.glyph2data[k]))

    def print_all_mandarin(self):
        for k in self.glyph2data:
            print(k + ': ' + self.get_mandarin(k))

    def print_all_qieyun(self):
        for k in self.glyph2data:
            print(k + ': ' + self.get_qieyun(k))

    def print_all_late_han(self):
        inc = 0
        for k in self.glyph2data:
            x = self.get_late_han(k)
            late_han = self.get_late_han(k)
            if late_han:
                late_han = late_han.split(' ')
            if len(late_han) >= 1:
                print(k + ': ' + ' '.join(late_han))
            if self.get_late_han(k).strip():
                inc += 1
        print(str(inc) + ' entries have LHan data.')

    def print_all_ocm(self):
        inc = 0
        for k in self.glyph2data:
            ocm = self.get_ocm(k)
            print(k + ': ' + ocm)

    def get_late_han(self, glyph):
        retval = self.get_data_from_pos(glyph, self.late_han_pos)
        retval = list(set(retval.split(' ')))
        return ' '.join(retval)

    def get_ocm(self, glyph):
        return self.get_data_from_pos(glyph, self.min_oc_pos)

    def get_qieyun(self, glyph):
        return self.get_data_from_pos(glyph, self.qieyun_pos)

    def get_mandarin(self, glyph):
        return self.get_data_from_pos(glyph, self.mandarin_pos)
        # retval = []
        # try:
        #    for line in self.glyph2data[glyph]:#.split('\t')[self.mandarin_pos]
        #        retval.append(line.split('\t')[self.mandarin_pos])
        # except:
        #    x = 1
        # return ' '.join(retval)

    def get_data_from_pos(self, glyph, pos):
        retval = []
        # if glyph == '片':
        #    x = 1
        try:
            for line in self.glyph2data[glyph]:
                data = line.split('\t')[pos]
                if data not in retval:
                    if data.strip():
                        retval.append(data)
        except:
            x = 1
        return ' '.join(retval).strip()

# NOTE: add data with .add_rhyme_word()
#  only AFTER all data has been added, access other functions
class rhyme_color_tracker:
    def __init__(self):
        self.reset()
    def reset(self):
        self.rw_list = []
        self.rw2rhyme_dict = {}
        self.rhyme2rw_list = {}
        self.rhyme2color_dict = {}
        self.default_color = '#80B8F0'

    def add_rhyme_word(self, rhyme_word):
        if not rhyme_word.strip():
            return
        if rhyme_word not in self.rw_list:
            self.rw_list.append(rhyme_word)
        #get_schuessler_late_han_for_glyph()
        rhyme_list = get_late_han_rhyme_for_glyph(rhyme_word)
        if rhyme_word not in self.rw2rhyme_dict:
            self.rw2rhyme_dict[rhyme_word] = []
        self.rw2rhyme_dict[rhyme_word] = rhyme_list
        for r in rhyme_list:
            if r not in self.rhyme2rw_list:
                self.rhyme2rw_list[r] = []
            if rhyme_word not in self.rhyme2rw_list[r]:
                self.rhyme2rw_list[r].append(rhyme_word)

    def get_color_given_rhyme(self, rhyme):
        self.set_up_rhyme2color_dict()
        retval = self.default_color
        if rhyme in self.rhyme2color_dict:
            retval = self.rhyme2color_dict[rhyme]
        return retval

    # each rhyme needs a unique marker
    # the top five largest rhyme groups need a unique color
    #IMPORTANT: call this ONLY after all data has been added
    def set_up_rhyme2color_dict(self):
        if self.rhyme2color_dict:
            return
        rw_list_len2rhyme_dict = {}
        for r in self.rhyme2rw_list:
            rlen = len(self.rhyme2rw_list[r])
            if rlen not in rw_list_len2rhyme_dict:
                rw_list_len2rhyme_dict[rlen] = []
                rw_list_len2rhyme_dict[rlen].append(r)
        rw_list_lens = list(rw_list_len2rhyme_dict.keys())
        rw_list_lens.sort(reverse=True)

        color_list = ['#D7D9D7', '#C9C5CB', '#BAACBD', '#B48EAE', '#646E68']
        #marker2color_dict = {}
        c_inc = 0
        for list_len in rw_list_lens:
            l_list = rw_list_len2rhyme_dict[list_len]
            for l in l_list:
                if l not in self.rhyme2color_dict:
                    if c_inc <= len(color_list) - 1:
                        self.rhyme2color_dict[l] = color_list[c_inc]
                        c_inc += 1


def test_readin_community_detection_group_descriptions():
    funct_name = 'test_readin_community_detection_group_descriptions()'
    #input_file = os.path.join(get_hanproj_dir(), 'hanproject','com_detection_lu1983_received_shi_data_output.txt')
    input_file = os.path.join(filename_storage.get_hanproj_dir(), 'hanproject', 'com_detection_kyomeishusei2015_mirror_data_output.txt')
    desired_groups = []
    rw2group_dict, group2rw_list = readin_community_detection_group_descriptions(input_file, desired_groups)
    for g in group2rw_list:
        rw_list = group2rw_list[g]
        print('Group ' + str(g) + ': ' + ''.join(rw_list))

def readin_community_detection_group_descriptions(filename, desired_groups=[]):
    funct_name = 'readin_community_detection_group_descriptions()'
    if not if_file_exists(filename, funct_name):
        print(funct_name + ' ERROR: Invalid input file: ' + filename)
        return {}, {}
    line_list = readlines_of_utf8_file(filename)
    rw2group_dict = {}
    group2rw_list = {}
    for ll in line_list:
        ll = ll.split('\t')
        orig_node_id = ll[0]
        group_id = ll[1]
        if desired_groups:
            if int(group_id) not in desired_groups:
                continue
        node_weight = ll[2]
        rhyme_word = ll[3]
        if rhyme_word not in rw2group_dict:
            rw2group_dict[rhyme_word] = []
        rw2group_dict[rhyme_word].append((group_id, node_weight, orig_node_id))

        if group_id not in group2rw_list:
            group2rw_list[group_id] = []
        group2rw_list[group_id].append(rhyme_word)
    return rw2group_dict, group2rw_list


color_list = ['#03045E', '#0077B6', '#00B4D8', '#90E0EF', '#CAF0F8']
color_list = ['#D7D9D7', '#C9C5CB', '#BAACBD', '#B48EAE', '#646E68']

class group2color:
    def __init__(self):
        x = 1
        self.g2c_dict = {}
        self.default_color = '#80B8F0'
        yellow = '#ffff31'
        red = '#ff0000'
        orange = '#fea92a'
        light_red = '#f89bab'
        dark_green = '#008a34'
        light_green = '#59e900'
        dark_blue = '#0900c9'
        light_blue = '#52c3ff'
        purple = '#a306fe'
        light_grey = '#e9e9e9'
        #1 = '#0A2F51'
        #4 = '#BFE1B0'
        #6 = '#56B870'
        #14 = '#188977' # was '#646E68'

        prefabs = ['#0A2F51', red, orange, '#BFE1B0', dark_green, '#56B870', dark_blue, light_blue, purple]
        self.color_list = prefabs
        self.color_list += ['#D7D9D7', '#C9C5CB', '#BAACBD', '#B48EAE', '#188977', '#03045E', '#0077B6', '#00B4D8',
                           '#90E0EF', '#CAF0F8', '#104F55', '#32746D', '#9EC5AB', '#01200F', '#011502', '#C6D8FF',
                           '#71A9F7', '#6B5CA5', '#72195A', '#4C1036']
        self.assign_colors()

    def assign_colors(self):
        for inc in range(1, len(self.color_list)+1, 1):
            self.g2c_dict[inc] = self.color_list[inc-1]

    def given_group_num_get_color(self, group_num):
        retval = self.default_color
        group_num = int(group_num)
        if group_num in self.g2c_dict:
            retval = self.g2c_dict[group_num]
        return retval

class rhyme2color:
    def __init__(self):
        self.r2c_dict = {}
        self.color_inc = 0
        self.default_color = '#80B8F0'
        self.color_list = ['#D7D9D7', '#C9C5CB', '#BAACBD', '#B48EAE', '#646E68', '#03045E', '#0077B6', '#00B4D8',
                           '#90E0EF', '#CAF0F8', '#104F55', '#32746D', '#9EC5AB', '#01200F', '#011502', '#C6D8FF',
                           '#71A9F7', '#6B5CA5', '#72195A', '#4C1036']
    def add_rhyme(self, rhyme):
        if rhyme not in self.r2c_dict:
            if self.color_inc <= len(self.color_list) - 1:
                self.r2c_dict[rhyme] = self.color_list[self.color_inc]
                self.color_inc += 1
            else:
                self.r2c_dict[rhyme] = self.default_color
    def given_rhyme_get_color(self, rhyme):
        retval = self.default_color
        if rhyme in self.r2c_dict:
            retval = self.r2c_dict[rhyme]
        return retval

def pyvis_test():
    pyvis_net1 = Network('1000px', '1000px', heading='Schuessler Late Han1', font_color='white')
    options = 'var options = {  "edges": {    "color": {      "inherit": "to"    },    "smooth": false  },  "physics": {    "minVelocity": 0.75  }}'
    pyvis_net1.set_options(options)
    pyvis_net2 = Network('1000px', '1000px', heading='Schuessler Late Han2', font_color='white')
    pyvis_net2.set_options(options)
    nodes = ['a', 'b', 'c', 'd', 'e', 'f']
    edges = [('a','b'), ('a', 'c'), ('a', 'd')]
    for n in nodes:
        pyvis_net1.add_node(n, label=n, shape='circle')
    for e in edges:
        pyvis_net1.add_edge(e[0], e[1])
    #pyvis_net1.show('pyvis_test.html')
    n1_nodes = pyvis_net1.get_nodes()
    n1_edges = pyvis_net1.get_edges()
    for n in n1_nodes:
        pyvis_net2.add_node(n, label=n.upper(), shape='circle')
    for e in n1_edges:
        pyvis_net2.add_edge(e['from'], e['to'])
    #pyvis_net2.add_edges(n1_edges)
    pyvis_net2.show('pyvis2_test.html')

def append_line_to_output_file(filename, line, is_verbose=False):
    funct_name = 'append_line_to_output_file()'
    new_line = '\n'
    if line[len(line) - len(new_line): len(line)] == new_line:
        line = line[0:len(line) - len(new_line)]
    if os.path.exists(filename):
        append_write = 'a+'  # append if already exists
    else:
        append_write = 'w+'  # make a new file if not
    if is_verbose:
        print(u'trying to write to ' + filename)
    with codecs.open(filename, append_write, 'utf8') as f:
        f.write(line + new_line)

def test_group2color():
    g2c = group2color()
    g2c.assign_colors()

def is_hanzi(test_ord):
    retval = False
    #if 'str' in str(type(test_ord)):
    #    test_ord = ord(test_ord)
    if '\u4e00' <= test_ord <= '\u9fff':
        return True
        #    U+20000..U+2A6D6 : CJK Unified Ideographs Extension B
    elif test_ord >= '\U00020000' and test_ord <= '\U0002a6d6':
        retval = True
    # U+2A700–U+2B73F : CJK Unified Ideographs Extension C
    elif test_ord >= '\U0002a700' and test_ord <= '\U0002b73f':
        retval = True
    # U+2F800..U+2FA1D : CJK Compatibility Supplement
    elif test_ord >= '\U0002f800' and test_ord <= '\U0002fa1d':
        retval = True
        #  the cjk radicals supplement  0x2e80 - 0x2eff
    elif test_ord >= '\u2e80' and test_ord <= '\u2eff':
        retval = True
        # kangxi rads 0x2f00 - 0x2fdf
    elif test_ord >= '\u2f00' and test_ord <= '\u2fdf':
        retval = True
        # DON'T NEED THIS: description characters  0x2ff0 - 0x2fff
        # DON'T NEED THIS: cjk xymbols and punctuation: 0x3000 - 0x303f
        # cjk strokes: 0x31c0 - 0x31ef
    elif test_ord >= '\u31c0' and test_ord <= '\u31ef':
        retval = True
        # DON'T NEED THIS: enclosed cjk letters and months: 0x3200 - 0x32ff
        # CJK compatibility: 0x3300 - 0x33ff
    elif test_ord >= '\u3300' and test_ord <= '\u33ff':
        retval = True
        # 3400 — 4DBF 	CJK Unified Ideographs Extension A
    elif test_ord >= '\u3400' and test_ord <= '\u4dbf':
        retval = True
        # CJK compatibility ideographs: 0xf900 - 0xfaff
    elif test_ord >= '\uf900' and test_ord <= '\ufaff':
        retval = True
        # CJK compatibiltiy forms; 0xfe30 - 0xfe4f
    elif test_ord >= '\ufe30' and test_ord <= '\ufe4f':
        retval = True
        # enclosed ideographic supplement:  0x1f200 - 0x1f2ff
    elif test_ord >= '\U0001f200' and test_ord <= '\U0001f2ff':
        retval = True
    return retval

def test_get_rhyme_groups_from_annotated_poem():
    funct_name = 'test_get_rhyme_groups_from_annotated_poem()'
    poem = ['Lu1983.008.1.1： 諸呂用事兮劉氏微。', 'Lu1983.008.1.2： 迫脅王侯兮彊授我a妃。', 'Lu1983.008.1.3： 我妃既妒兮誣我以惡。',
            'Lu1983.008.1.4： 讒女亂國兮上曾不a寤。', 'Lu1983.008.1.5： 我無忠臣兮何故棄國。', 'Lu1983.008.1.6： 自快中野兮蒼天與b直。',
            'Lu1983.008.1.7： 于嗟不可悔兮寧早自賊。', 'Lu1983.008.1.8： 為王餓死兮誰者b憐之。', 'Lu1983.008.1.9： 呂氏絕理兮托天報仇。']
    poem = ['Lu1983.008.1.1： 諸呂用事兮劉氏微。', 'Lu1983.008.1.2： 迫脅王侯兮彊授我a(i)妃。', 'Lu1983.008.1.3： 我妃既妒兮誣我以惡。',
            'Lu1983.008.1.4： 讒女亂國兮上曾不b(ɑ)寤。', 'Lu1983.008.1.5： 我無忠臣兮何故棄國。', 'Lu1983.008.1.6： 自快中野兮蒼天與c(ik)直。',
            'Lu1983.008.1.7： 于嗟不可悔兮寧早自賊。', 'Lu1983.008.1.8： 為王餓死兮誰者d(en)憐之。', 'Lu1983.008.1.9： 呂氏絕理兮托天報仇。']
    m2rw_list = get_rhyme_groups_from_annotated_poem('\n'.join(poem))
    for m in m2rw_list:
        print(m + ': [' + ''.join(m2rw_list[m]) + ']')

def strip_poem_id_from_line(line):
    if '： ' in line:
        line = line.split('： ')[1]
    return line

def remove_punctuation_from_end_of_line(line):
    if not line:
        return line
    last_char = line[len(line)-1]
    punctuation = ['，', '。', '、']
    if any(punctuation_char in last_char for punctuation_char in punctuation):
        line = line[0:len(line)-1]
    return line

# ASSUMPTION:
#  only one rhyme word per line, that appears at the end of the line (except for special words like 之、也, etc.)
def get_rhyme_word_and_marker_from_line_of_poem(line):
    rhyme_word = ''
    marker = ''
    if '中夜奄喪，□□□' in line:
        x = 1
    if '･' in line:
        x = 1

    orig_line = line # debug only
    line = strip_poem_id_from_line(line)
    #exception_chars = ['之', '兮', '乎', '也', '矣', '焉']
    line = remove_punctuation_from_end_of_line(line)
    if not line or len(line) == 1:
        return (rhyme_word, marker)

    rw_pos = len(line)-1
    rhyme_word = line[rw_pos]
    if rhyme_word == '」' or rhyme_word == '』':
        rw_pos -= 1
        rhyme_word = line[rw_pos]

    if rhyme_word == '□' or rhyme_word == '…' or rhyme_word == '･' or rhyme_word == '，' or marker == '･':
        return ('', '')
    #
    # Handle Schuessler's LHan, i.e., by pass the '({pronunciation})'.
    if line[rw_pos-1] == ')': # if schuessler
        m_pos = line.rfind('(') - 1
        marker = line[m_pos]
        if not is_hanzi(line[m_pos-1]) and line[m_pos-1].isalpha():
            marker = line[m_pos-1] + marker
        marker.replace('□', '')
        marker.replace('々', '')
        return (rhyme_word, marker.replace('ゝ',''))

    #
    # Handle the case where the marker is at the beginning of the line
    first_char = line[0]
    first_char_is_hanzi = is_hanzi(first_char)
    if not is_hanzi(line[0]) and line[0] != '□' and line[0].isalpha(): # see if marker is at the beginning of the line
        marker = line[0]
        if marker.isalpha():
            #try:
            sec_char = line[1]
            #except IndexError as ie:
            #    print('line=' + line)
            #    x = 1
            if not is_hanzi(sec_char) and sec_char.isalpha(): # some markers are two letters long
                if line[1].isalpha():
                    marker += line[1]
            marker.replace('々', '')
            marker.replace('□', '')
            return (rhyme_word, marker.replace('ゝ',''))
    if rhyme_word in exception_chars:
        rhyme_word = line[len(line)-2]# the rhyme word is the character in front of the exception character
    rw_pos = line.rfind(rhyme_word)
    left = line[:rw_pos] # cut the string in two at the rhyme word
#    if is_hanzi(left[len(left)-1]): # if there is a chinese character to the left of the rhyme word, then there's no rhyme word
#        return ('', marker)
#    else:
    #
    # Handle everything else
    dont_quit = True

    while dont_quit:
        if not left.strip():
            dont_quit = False
            rhyme_word = ''
            marker = ''
            continue
        try:
            tmp_left = left[len(left) - 1]
        except IndexError as ie:
            print('line=' + line)
            x = 1
        if tmp_left.isalpha() and not is_hanzi(tmp_left):
            try:
                if not is_hanzi(tmp_left):
                    if not is_hanzi(left[len(left)-2]) and left[len(left)-2].isalpha():
                        marker = left[len(left)-2] + tmp_left
                    else:
                        marker = tmp_left
            except IndexError as ie:
                marker = ''
                rhyme_word = ''
            if any(punk in marker for punk in punctuation):
                rhyme_word = ''
                marker == ''
            if not is_hanzi(rhyme_word):
                rhyme_word = ''
                marker == ''
            marker.replace('々', '')
            marker.replace('□', '')
            return (rhyme_word, marker.replace('ゝ',''))
        if is_hanzi(tmp_left) or tmp_left == '□': # if last char in 'left' is chinese char...
            if not marker:
                rhyme_word = ''
            dont_quit = False
        else:
            #try:
            marker = left[len(left)-1] + marker #
            #except IndexError as ie:
            #    x = 1
            left = left[0:len(left)-1] # decrement
    if any(punk in marker for punk in punctuation):
        rhyme_word = ''
        marker == ''
    if not is_hanzi(rhyme_word):
        rhyme_word = ''
        marker == ''
    marker.replace('々', '')
    marker.replace('□', '')
    return (rhyme_word, marker.replace('ゝ',''))

# returns dictionary where:
#    key = rhyme group marker
#  value = list of rhyme words
def get_rhyme_groups_from_annotated_poem(poem):
    funct_name = 'get_rhyme_groups_from_annotated_poem()'
    poem = poem.split('\n')
    retval = {}
    for p in poem:
        rw, m = get_rhyme_word_and_marker_from_line_of_poem(p)
        if rw:
            if m not in retval:
                retval[m] = []
            retval[m].append(rw)
        #print('Rhyme: ' + rw + ', Marker: ' + m + ', line: ' + p)
    return retval
#test_get_rhyme_groups_from_annotated_poem()

def test_strip_poem_id_from_line():
    funct_name = 'test_strip_poem_id_from_line()'
    line = 'Lu1983.020.2.3交情通體心和諧。'
    after = strip_poem_id_from_line(line)
    print('BEFORE: ' + line + '\n\tAFTER: ' + after)

def strip_poem_id_from_line(line):
    retval = strip_poem_id_from_line_with_colon(line)
    if not retval:
        retval = strip_poem_id_from_line_without_colon(line)
    return retval

def strip_poem_id_from_line_with_colon(line):
    split_char = ''
    if '：' in line:
        split_char = '：'
    elif ':' in line:
        split_char = ':'
    if split_char:
        line = line.split(split_char)[1]
    else:
        line = ''
    return line

def strip_poem_id_from_line_without_colon(line):
    if '.' in line:
        line = line.split('.')
        line = line[len(line)-1] # grab the most right section
        line = remove_numbers_from_beginning_of_string(line)
    return line

def remove_numbers_from_beginning_of_string(line):
    dont_quit = True
    while dont_quit:
        if line[0].isdecimal():
            line = line[1:len(line)]
        else:
            dont_quit = False
    return line

def test_get_raw_marker():
    test_strs = ['交情通體心和諧。', '交情通體心和az諧。']
    for ts in test_strs:
        marker, rhyme_word = get_raw_marker_and_rhyme_word(ts)
        if marker.strip():
            print('For ' + ts + ', marker = ' + marker + ', rhyme_word = ' + rhyme_word)
        else:
            print('For ' + ts + ', there is NO marker or rhyme word!')
# NOTE:
#  this code assumes that there's only one, contingent marker
def get_raw_marker_and_rhyme_word(line):
    retval = ''
    rhyme_word = ''
    marker_started = False
    for inc in range(0, len(line)-1, 1):
        if not is_hanzi(line[inc]):
            retval += line[inc]
            marker_started = True
        else:
            if marker_started:
                rhyme_word = line[inc]
                break
    return retval, rhyme_word

def create_latex_table_for_poem(poem):
    funct_name = 'create_latex_table_for_poem()'
    #獨處室兮廓無依。 & - & - & 獨處室兮廓無依。\\
    #思佳人兮情傷悲。 & 悲 & a & 思佳人兮情傷[a]悲。\\
    retval = []
    for line in poem:
        marker, rhyme_word = get_raw_marker_and_rhyme_word(line)
        if marker.strip():
            output = line.replace(marker,'') + ' & ' + rhyme_word + ' & ' + marker + ' & ' + line.replace(marker, '[' + marker + ']') + '\\\\'
        else:
            output = line + ' & - & - & ' + line + '\\\\'
        retval.append(output)
    return retval


# this won't work if downloaded from GitHub (the directory structure doesn't work)
def test_strip_poem_id_from_lines_of_poem():
    funct_name = 'test_strip_poem_id_from_lines_of_poem()'
    filename = os.path.join(get_soas_code_dir(), 'utils', 'poem_data.txt')
    stripped = strip_poem_id_from_lines_of_poem(filename)
    latex = create_latex_table_for_poem(stripped)
    header = ['\\begin{table}[h!]', '\\begin{tabular}{ c c c l }', '\hline',
              '\\textbf{Poem} & \\textbf{Rhyme Word} & \\textbf{Rhyme Group} & \\textbf{Annotated Poem}\\\\',
              '\hline']
    footer = ['\hline', '\end{tabular}', '\end{table}']

    for h in header:
        print(h)
    for line in latex:
        print(line)
    for f in footer:
        print(f)

def strip_poem_id_from_lines_of_poem(filename):
    poem_data = readlines_of_utf8_file(filename)
    retval = []
    for pd in poem_data:
        retval.append(strip_poem_id_from_line(pd))
        #print(strip_poem_id_from_line(pd))
    return retval
s_lhan_h_v = ['i', 'ɨ', 'y', 'u'] # LHan high vowels (H)
s_lhan_l_v = ['e', 'ė', 'ə', 'ɑ', 'o'] # LHan non-high vowels (L)
s_lhan_ed_v = ['ɛ', 'a', 'ɔ'] # 二等 vowels (R)
s_lhan_simp_v = s_lhan_h_v + s_lhan_l_v + s_lhan_ed_v
# i e ə ɑ o u
# NOTE: Since 's_lhan_diphs' is used for searching, all longer vowels must come before shorter vowels (long, short = number
#       of letters)
s_lhan_diphs = ['uai', 'uɑi', 'uɛi', 'uəi', 'iau', 'iai', 'ɨai', 'ɨɑi', 'ɨɑu', 'iɑu', 'ie', 'iə', 'iɑ', 'io', 'iɔ', \
                'iu', 'ii', 'ei', 'eu', 'ɛi', 'əi', 'ɨi', 'ɨə', 'ɨɑ', 'ɑi', 'ɑu', 'ou', 'uɨ', 'ui', 'uɑ', 'uo', \
                'uɔ', 'ɔu', 'aɨ', 'ai', 'au', 'ɨo', 'ɨu', 'oi']# not in warping paper: 'ɔu', 'iau', 'au'
velar_initials = ['k', 'h', 'kʰ', 'ŋ', 'g']
s_lhan_pcodas = ['s', 'ʔ', 'h']
s_lhan_tones = ['ᵃ', 'ᴮ', 'ᶜ', 'ᵈ']
#test_strip_poem_id_from_lines_of_poem()ɑ

def test_load_late_han_data():
    funct_name = 'test_load_late_han_data()'
    data = load_late_han_data()
    for d in data:
        print(d + ': ' + data[d])
    print(str(len(data)) + ' entries.')

def load_late_han_data():
    funct_name = 'load_late_han_data()'
    #most_complete_schuessler_late_han_data.txt
    retval = {}
    input_file = os.path.join(filename_storage.get_phonological_data_dir(), 'most_complete_schuessler_late_han_data.txt')
    if not if_file_exists(input_file, funct_name):
        return retval
    input_lines = readlines_of_utf8_file(input_file)
    for il in input_lines:
        il = il.split('\t')
        if il[0] not in retval:
            retval[il[0]] = ''
        retval[il[0]] = il[1]
    return retval

skip_these = ['ut', 'uŋ', 'um', 'un', 'uk', 'up', 'u']
def test_parse_late_han_syllable2():
    funct_name = 'test_parse_late_han_syllable()'
    zi2lhan_dict = load_late_han_data()
    pinc = 0
    finals_involved = []
    for zi in zi2lhan_dict:
        lhan = zi2lhan_dict[zi].strip()
        if 'u' not in lhan: # DEBUG ONLY!! REMOVE!
            continue# DEBUG ONLY!! REMOVE!
        #if any()
        #if any(unw in rhyme_word for unw in self.unwanted):
        if any(diphthong in lhan for diphthong in s_lhan_diphs):# DEBUG ONLY!! REMOVE!
            continue# DEBUG ONLY!! REMOVE!
        lhan = lhan.split(' ')
        for lh in lhan:
            initial, medial, final, pcoda = parse_late_han_syllable2(lh)
            msg = lh + ': '
            if initial:
                if not any(velar == initial for velar in velar_initials):# DEBUG ONLY!! REMOVE!
                    continue# DEBUG ONLY!! REMOVE!
                msg += initial + ' + '
            if medial:
                msg += medial + ' + '
            if final:
                msg += final + ' + '
            if any(yunmu == final for yunmu in skip_these):# DEBUG ONLY!! REMOVE!
                #print('skipping ' + zi + ': ' + lh)# DEBUG ONLY!! REMOVE!
                continue# DEBUG ONLY!! REMOVE!

            if pcoda and pcoda not in tones:
                msg += pcoda
            if msg[len(msg)-len(' + '):len(msg)] == ' + ': # remove ' + ' if it's at the end of the string
                msg = msg[:len(msg)-len(' + ')]
            if 'u' in msg:# DEBUG ONLY!! REMOVE!
                pinc += 1
                if final not in finals_involved:
                    finals_involved.append(final)
                print(zi + ' ' + msg)# DEBUG ONLY!! REMOVE!
    print(str(pinc) + ' entries.')
    print('Finals involved:')
    print(', '.join(finals_involved))

def test_parse_late_han_syllable2a():
    funct_name = 'test_parse_late_han_syllable2a()'
    zi2lhan_dict = load_late_han_data()
    pinc = 0
    finals_involved = []
    for zi in zi2lhan_dict:
        lhan = zi2lhan_dict[zi].strip()
        if 'uɑ' not in lhan: # DEBUG ONLY!! REMOVE!
            continue# DEBUG ONLY!! REMOVE!
        lhan = lhan.split(' ')
        for lh in lhan:
            if '官' in zi:
                x = 1
            if 'uɑ' in lh:
                x = 1
            initial, medial, final, pcoda = parse_late_han_syllable2(lh)
            msg = lh + ': '
            if initial:
                msg += initial + ' + '
            if medial:
                msg += medial + ' + '
            if final:
                msg += final + ' + '

            if pcoda and pcoda not in tones:
                msg += pcoda
            if msg[len(msg)-len(' + '):len(msg)] == ' + ': # remove ' + ' if it's at the end of the string
                msg = msg[:len(msg)-len(' + ')]
            if 'u' in msg:# DEBUG ONLY!! REMOVE!
                pinc += 1
                if final not in finals_involved:
                    finals_involved.append(final)
                print(zi + ' ' + msg)# DEBUG ONLY!! REMOVE!
    print(str(pinc) + ' entries.')
    print('Finals involved:')
    print(', '.join(finals_involved))

def test_get_rhyme_from_schuessler_late_han_syllable():
    funct_name = 'test_parse_late_han_syllable2a()'
    zi2lhan_dict = load_late_han_data()
    pinc = 0
    finals_involved = []
    for zi in zi2lhan_dict:
        lhan = zi2lhan_dict[zi].strip()
        lhan = lhan.split(' ')
        for lh in lhan:
            if 'uɑ' in lh:
                x = 1
            final = get_rhyme_from_schuessler_late_han_syllable(lh)
            msg = lh
            if final:
                msg += ' (' + final + ')'
            else:
                msg += ' (MISSING)'
            print(msg)
    print(str(pinc) + ' entries.')
    #print('Finals involved:')
    #print(', '.join(finals_involved))

def parse_schuessler_late_han_syllable(reco):
    funct_name = 'parse_schuessler_late_han_syllable()'
    initial = ''
    if not reco.strip():
        return '', '', '', ''
    if aspiration in reco:
        initial = reco.split(aspiration)[0] + aspiration
    else:
        for pi in lhan_initials:
            if is_this_the_initial(pi, reco):
                initial = pi
                break
    if not initial.strip():
        if reco[0] == 'w' or reco[0] == 'a':
            initial = zero_initial # make sure this handles 'wɑ' => 'uɑ'
        else:
            initial = 'X'
    final = reco[len(initial):len(reco)]
    #velar_initials
    # in Schuessler's Late Han,
    #   for velar initial + 'uɑ', the 'u' is part of the initial (the two are a single phoneme)
    #   for labial or acute initial + 'uɑ', the 'uɑ' is a diphthong
    if 'uɑ' in final:
        if initial in velar_initials:
            initial = initial + 'u'
            final = final.replace('uɑ', 'ɑ')
    medial = ''
    pcoda = ''
    try:
        end_of_final = final[len(final)-1]
    except IndexError as ie:
        x = 1
    if end_of_final in post_codas:
        pcoda = final[len(final)-1]
        final = final[0:len(final)-1]
    return initial, medial, final, pcoda

#
# We only need the rhyme and we need this function to be computationally efficient as possible
# s_lhan_simp_v
# s_lhan_diphs
def get_rhyme_from_schuessler_late_han_syllable(reco):
    funct_name = 'get_rhyme_from_schuessler_late_han_syllable()'
    #
    # see if vowel is diphthong
    rhyme = ''
    # first check for a diphthong:
    main_vowel = [diphth for diphth in s_lhan_diphs if (diphth in reco)]
    if not main_vowel:# if no diphthong, check for a simple vowel:
        main_vowel = [simp_vowel for simp_vowel in s_lhan_simp_v if (simp_vowel in reco)]
    if not main_vowel: # something is amiss
        print('could not find vowel in ' + reco)
        print('diphthongs: ' + ', '.join(s_lhan_diphs))
        print('simple vowels: ' + ', '.join(s_lhan_simp_v))
        return rhyme
    main_vowel = main_vowel[0]
    reco = reco.split(main_vowel)
    rhyme = main_vowel + reco[1]
    # remove tone marking if there is one
    tone_mark = [tm for tm in s_lhan_tones if (tm in rhyme)]
    pcoda = [pc for pc in s_lhan_pcodas if (pc in rhyme)]
    if tone_mark or pcoda:
        rhyme = rhyme[0:len(rhyme)-1]
    initial = reco[0]
    if 'w' in initial:
        if 'u' not in rhyme:
            rhyme = 'u' + rhyme
    if 'uɑ' in rhyme: # check for schuessler's exception
        velar = [v for v in velar_initials if (v in initial)]
        if velar:
            if 'ŋ' in rhyme:
                rhyme = rhyme.replace('uɑŋ', 'ɑŋ')
    if rhyme[0] == 'y':
        rhyme = 'i' + rhyme[1:len(rhyme)]
    return rhyme


def if_file_exists(filename, funct_name):
    retval = False
    if os.path.isfile(filename):
        retval = True
    else:
        print(funct_name + ' ERROR: Invalid input file:  ' + filename)
    return retval

def readin_most_complete_schuessler_data():
    funct_name = 'readin_most_complete_schuessler_data()'
    input_file = os.path.join(filename_storage.get_phonological_data_dir(), 'most_complete_schuessler_late_han_data.txt')
    retval = {}
    if not if_file_exists(input_file, funct_name):
        return retval
    data = readlines_of_utf8_file(input_file)
    glyph_pos = 0
    late_han_pos = 1
    for d in data:
        d = d.split('\t')
        if d[glyph_pos] not in retval:
            retval[d[glyph_pos]] = []
        lhan = d[late_han_pos]
        lhan = lhan.split(' ')
        for lh in lhan:
            retval[d[glyph_pos]].append(lh) #append(d[late_han_pos])
    return retval

def myfunct():
    print('yup. myfunct()')

#def main():
#    m = myfunct
#    m()

#test_get_rhyme_from_schuessler_late_han_syllable()
#main()
#test_parse_late_han_syllable2a()
#test_load_late_han_data()
#test_find_southern_late_han_readings()