# -*- coding: utf-8 -*-
"""
Created in February 2026

@authors: carmen, isabell

Preprocessing script to create compound resource.
Input: .conllu files with annotated compounds in sentence context
Output:
    - one .csv file with individual compounds and all annotation info
    - one .csv file with individual compounds and selected info (for semantic transparency analysis)
    
Procedure:
    - convert all .conllu.txt files to .conllu
    - take all .conllu files
    - extract compounds and annotation from each .conllu file
    - create output .csv files
"""

import glob
import json
from stanza.utils.conll import CoNLL
from stanza.models.common.doc import Document
import csv
import ast
import os
from pathlib import Path

# convert files ending in .conllu.txt to .conllu
for path in Path('.').glob('*.conllu.txt'): # get .conllu.txt files
    new_path = path.with_suffix('') # create new path without .txt suffix
    path.rename(new_path) # rename file

# read all conllu docs
documents = glob.glob('./*.conllu')

# create lists for csv export
long_data_list = [['filename', 'language', 'register', 'sent_id', 'tok_id', 'tok_text', 'tok_lemma', 'deprel', 'misc', 'prev_tok', 'second_prev_tok']]
long_data_list_analysis = [['compound','comp_lemma','const_1_text','const_2_text','const_3_text','const_1_lemma','const_2_lemma','const_3_lemma','gold_branching','language','register']]

comp_analysis_row = ['compound','comp_lemma','const_1_text','const_2_text','const_3_text','const_1_lemma','const_2_lemma','const_3_lemma','gold_branching','language','register']
span_length = 0
comp_collect = []

# get comps from each doc
for doc_ind, doc in enumerate(documents):
    #print(doc)
    entire_doc = CoNLL.conll2doc(doc)
    entire_dict = entire_doc.to_dict()
    print('entire: ', entire_dict)
    filename = doc[2:]
    print(filename)
    
    # get language info from filename
    if any(x in filename for x in ['.eng.', 'anno_sw', 'dd_anno', 'sw_anno', 'sw_dd']):
        language = 'EN'
    elif any(x in filename for x in ['.ger.', 'anno_kg', 'anno_mm']):
        language = 'GER'
    else:
        language = 'NA'
    
    # get register info from filename
    if any(x in filename for x in ['.eng.', '.ger.']):
        register = 'scientific'
    else:
        register = 'general'
        
    #comp_analysis_row[9] = language
    #comp_analysis_row[10] = register
    
    for s_ind, sentence in enumerate(entire_dict):
        for token_ind, entire_tok in enumerate(sentence):
            print(entire_tok)
            print(type(entire_tok['id']))
            # detect compound span by '-' in tok_id and 'compound:nmod' in next tok
            # leave text and lemma, extract general info+append and
            # start building compound entry for analysis file
            if 'id' in entire_tok and entire_tok['id'] != '' and isinstance(entire_tok['id'], tuple) and 'compound:nmod' in sentence[token_ind + 1]['deprel']: # and 'deprel' in entire_tok and entire_tok['deprel'] != '' and 'compound:nmod' not in entire_tok['deprel']  and '-' in entire_tok['id']
                # print(entire_tok['deprel'])
                # get general info
                tok_list = [filename, language, register, s_ind + 1, entire_tok['id'], entire_tok['text'], entire_tok['lemma'] if 'lemma' in entire_tok else '_',
                            entire_tok['deprel'] if 'deprel' in entire_tok else '_', entire_tok['misc'] if 'misc' in entire_tok else '_', sentence[token_ind - 1]['text'] if 'text' in sentence[token_ind - 1] else '_',
                            sentence[token_ind - 2]['text'] if 'text' in sentence[token_ind - 2] else '_']
                long_data_list.append(tok_list)

                # set span_length
                span_id1 = entire_tok['id'][0]
                span_id2 = entire_tok['id'][1]
                span_length = int(span_id2)-int(span_id1)+1
                print('Span length: ', span_length)

                # build whole-compound if span_length is 2 / look for hyphen
                if span_length == 2:
                    # there are hyphens
                    if ('text' in sentence[token_ind +1] and sentence[token_ind +1]['text'] != '' and sentence[token_ind +1]['text'] == '-') or ('text' in sentence[token_ind -1] and sentence[token_ind -1]['text'] != '' and sentence[token_ind -1]['text'] == '-'):
                        # hyphen before (const+hyphen+span)
                        if 'text' in sentence[token_ind - 1] and sentence[token_ind - 1]['text'] != '' and sentence[token_ind - 1]['text'] == '-':
                            whole_comp_text = sentence[token_ind - 4]['text'] + sentence[token_ind - 1]['text'] + entire_tok['text']
                            if 'lemma' in entire_tok:
                                whole_comp_lemma = sentence[token_ind - 4]['lemma'] + sentence[token_ind - 1]['lemma'] + \
                                              entire_tok['lemma']
                            else:
                                whole_comp_lemma = '_'
                                # whole-comp
                            comp_analysis_row[0] = whole_comp_text
                            comp_analysis_row[1] = whole_comp_lemma
                            # const_text
                            comp_analysis_row[2] = sentence[token_ind - 2]['text']
                            comp_analysis_row[3] = sentence[token_ind + 1]['text']
                            comp_analysis_row[4] = sentence[token_ind + 2]['text']
                            # const_lemma
                            comp_analysis_row[5] = sentence[token_ind - 2]['lemma'] if 'lemma' in sentence[token_ind - 2] else '_'
                            comp_analysis_row[6] = sentence[token_ind + 1]['lemma'] if 'lemma' in sentence[token_ind + 1] else '_'
                            comp_analysis_row[7] = sentence[token_ind + 2]['lemma'] if 'lemma' in sentence[token_ind + 2] else '_'
                            # check head-structure considering possible hyphenation to determine branching structure
                            # then store branching-structure in analysis_row
                            if sentence[token_ind - 2]['head'] == sentence[token_ind + 1]['head']:
                                comp_analysis_row[8] = 'BC'
                            elif sentence[token_ind - 2]['head'] != sentence[token_ind + 1]['head']:
                                comp_analysis_row[8] = 'AB'


                        # hyphen after (span+hyphen+const)
                        else:
                            whole_comp_text = entire_tok['text'] + sentence[token_ind +1]['text'] + sentence[token_ind + 2]['text']
                            if 'lemma' in entire_tok:
                                whole_comp_lemma = entire_tok['lemma'] + sentence[token_ind +1]['lemma'] + sentence[token_ind + 2]['lemma']
                            else:
                                whole_comp_lemma = '_'
                            # whole comp
                            comp_analysis_row[0] = whole_comp_text
                            comp_analysis_row[1] = whole_comp_lemma
                            # const_text
                            comp_analysis_row[2] = sentence[token_ind + 1]['text']
                            comp_analysis_row[3] = sentence[token_ind + 2]['text']
                            comp_analysis_row[4] = sentence[token_ind + 4]['text']
                            # const_lemma
                            comp_analysis_row[5] = sentence[token_ind + 1]['lemma'] if 'lemma' in sentence[token_ind + 1] else '_'
                            comp_analysis_row[6] = sentence[token_ind + 2]['lemma'] if 'lemma' in sentence[token_ind + 2] else '_'
                            comp_analysis_row[7] = sentence[token_ind + 4]['lemma'] if 'lemma' in sentence[token_ind + 4] else '_'
                            # check head-structure considering possible hyphenation to determine branching structure
                            # then store branching-structure in analysis_row
                            if sentence[token_ind + 1]['head'] == sentence[token_ind + 2]['head']:
                                comp_analysis_row[8] = 'BC'
                            elif sentence[token_ind + 1]['head'] != sentence[token_ind + 2]['head']:
                                comp_analysis_row[8] = 'AB'

                    # no hyphens
                    else:
                        # span first
                        if 'compound:nmod' in sentence[token_ind +1]['deprel'] and 'compound:nmod' not in sentence[token_ind -1]['deprel']:
                            print('spanfirst span2 no hyphens')
                            whole_comp_text = entire_tok['text'] + ' ' + sentence[token_ind + 3]['text']
                            if 'lemma' in entire_tok:
                                whole_comp_lemma = entire_tok['lemma'] + ' ' + sentence[token_ind + 3]['lemma']
                            else:
                                whole_comp_lemma = '_'
                            # whole comp
                            comp_analysis_row[0] = whole_comp_text
                            comp_analysis_row[1] = whole_comp_lemma
                            comp_analysis_row[2] = sentence[token_ind + 1]['text']
                            comp_analysis_row[3] = sentence[token_ind + 2]['text']
                            comp_analysis_row[4] = sentence[token_ind + 3]['text']
                            # const_lemma
                            comp_analysis_row[5] = sentence[token_ind + 1]['lemma'] if 'lemma' in sentence[token_ind + 1] else '_'
                            comp_analysis_row[6] = sentence[token_ind + 2]['lemma'] if 'lemma' in sentence[token_ind + 2] else '_'
                            comp_analysis_row[7] = sentence[token_ind + 3]['lemma'] if 'lemma' in sentence[token_ind + 3] else '_'
                            # check head-structure considering possible hyphenation to determine branching structure
                            # then store branching-structure in analysis_row
                            if sentence[token_ind + 1]['head'] == sentence[token_ind + 2]['head']:
                                comp_analysis_row[8] = 'BC'
                            elif sentence[token_ind + 1]['head'] != sentence[token_ind + 2]['head']:
                                comp_analysis_row[8] = 'AB'

                        # span second
                        else:
                            print('spansecond span2 no hyphens')
                            whole_comp_text = sentence[token_ind - 1]['text'] + ' ' + entire_tok['text']
                            if 'lemma' in entire_tok:
                                whole_comp_lemma = sentence[token_ind - 1]['lemma'] + ' ' + entire_tok['lemma']
                            else:
                                whole_comp_lemma = '_'
                            # whole comp
                            comp_analysis_row[0] = whole_comp_text
                            comp_analysis_row[1] = whole_comp_lemma
                            # const_text
                            comp_analysis_row[2] = sentence[token_ind - 1]['text']
                            comp_analysis_row[3] = sentence[token_ind + 1]['text']
                            comp_analysis_row[4] = sentence[token_ind + 2]['text']
                            # const_lemma
                            comp_analysis_row[5] = sentence[token_ind - 1]['lemma'] if 'lemma' in sentence[token_ind - 1] else '_'
                            comp_analysis_row[6] = sentence[token_ind + 1]['lemma'] if 'lemma' in sentence[token_ind + 1] else '_'
                            comp_analysis_row[7] = sentence[token_ind + 2]['lemma'] if 'lemma' in sentence[token_ind + 2] else '_'
                            # check head-structure considering possible hyphenation to determine branching structure
                            # then store branching-structure in analysis_row
                            if sentence[token_ind - 1]['head'] == sentence[token_ind + 1]['head']:
                                comp_analysis_row[8] = 'BC'
                            elif sentence[token_ind - 1]['head'] != sentence[token_ind + 1]['head']:
                                comp_analysis_row[8] = 'AB'

                # if span is 3 store text of span-tok in analysis row, then collect constituents (text/lemma)
                elif span_length == 3:
                    # whole comp
                    comp_analysis_row[0] = entire_tok['text']
                    comp_analysis_row[1] = entire_tok['lemma'] if 'lemma' in entire_tok else '_'
                    # const_text
                    comp_analysis_row[2] = sentence[token_ind + 1]['text']
                    comp_analysis_row[3] = sentence[token_ind + 2]['text']
                    comp_analysis_row[4] = sentence[token_ind + 3]['text']
                    # const_lemma
                    comp_analysis_row[5] = sentence[token_ind + 1]['lemma'] if 'lemma' in sentence[token_ind + 1] else '_'
                    comp_analysis_row[6] = sentence[token_ind + 2]['lemma'] if 'lemma' in sentence[token_ind + 2] else '_'
                    comp_analysis_row[7] = sentence[token_ind + 3]['lemma'] if 'lemma' in sentence[token_ind + 3] else '_'
                    # check head-structure considering possible hyphenation to determine branching structure
                    # then store branching-structure in analysis_row
                    if sentence[token_ind + 1]['head'] == sentence[token_ind + 2]['head']:
                        comp_analysis_row[8] = 'BC'
                    elif sentence[token_ind + 1]['head'] != sentence[token_ind + 2]['head']:
                        comp_analysis_row[8] = 'AB'

                # append
                print(comp_analysis_row)
                comp_analysis_row[9] = language
                comp_analysis_row[10] = register
                long_data_list_analysis.append(comp_analysis_row)
                # clear
                comp_analysis_row = ['compound', 'comp_lemma', 'const_1_text', 'const_2_text', 'const_3_text','const_1_lemma', 'const_2_lemma', 'const_3_lemma', 'gold_branching','language','register']
                print('Appended analysis_row in span3')

            # detect first constituent of non-span compound (nmod in this token and in the next, but not in the previous)
            # leave text and lemma, extract general info+append and
            # start building compound entry for analysis file
            elif 'deprel' in entire_tok and entire_tok['deprel'] != '' and 'compound:nmod' in entire_tok['deprel'] and ('compound:nmod' in sentence[token_ind +1]['deprel'] or ('-' in sentence[token_ind +1]['text'] and 'compound:nmod' in sentence[token_ind +2]['deprel'] if 'deprel' in sentence[token_ind +2] else 'compound:nmod' in sentence[token_ind +3]['deprel'])) and (('deprel'in sentence[token_ind -1] and 'compound:nmod' not in sentence[token_ind -1]['deprel']) or 'deprel' not in sentence[token_ind -1]):
                print(entire_tok['deprel'])
                # get general info
                tok_list = [filename, language, register, s_ind + 1, entire_tok['id'], entire_tok['text'],
                            entire_tok['lemma'] if 'lemma' in entire_tok else '_',
                            entire_tok['deprel'] if 'deprel' in entire_tok else '_',
                            entire_tok['misc'] if 'misc' in entire_tok else '_',
                            sentence[token_ind - 1]['text'] if 'text' in sentence[token_ind - 1] else '_',
                            sentence[token_ind - 2]['text'] if 'text' in sentence[token_ind - 2] else '_']
                long_data_list.append(tok_list)
                comp_collect.append(entire_tok)



            # detect non-last-constituent (nmod in this token and in the previous, but not in the next)
            # leave text and lemma, extract general info+append and
            # continue building compound entry for analysis file
            elif 'deprel' in entire_tok and entire_tok['deprel'] != '' and 'compound:nmod' in entire_tok['deprel'] and (('deprel' in sentence[token_ind -1] and'compound:nmod' in sentence[token_ind -1]['deprel']) or '-' in sentence[token_ind -1]['text']) and 'compound:nmod' not in sentence[token_ind +1]['deprel']:
                print(entire_tok['deprel'])
                # get general info
                tok_list = [filename, language, register, s_ind + 1, entire_tok['id'], entire_tok['text'],
                            entire_tok['lemma'] if 'lemma' in entire_tok else '_',
                            entire_tok['deprel'] if 'deprel' in entire_tok else '_',
                            entire_tok['misc'] if 'misc' in entire_tok else '_',
                            sentence[token_ind - 1]['text'] if 'text' in sentence[token_ind - 1] else '_',
                            sentence[token_ind - 2]['text'] if 'text' in sentence[token_ind - 2] else '_']
                long_data_list.append(tok_list)
                comp_collect.append(entire_tok)


            # detect last-constituent (no nmod in this token but in the previous)
            # leave text and lemma, extract general info+append and
            # continue building compound entry for analysis file
            # possible spellings here: 3span-nmod-nmod-const, nmod-nmod-const, nmod-span-nmod-const, 2span-nmod-nmod-const
            elif 'deprel' in entire_tok and entire_tok['deprel'] != '' and 'compound:nmod' not in entire_tok['deprel'] and '-' not in entire_tok['text'] and (('deprel' in sentence[token_ind -1] and 'compound:nmod' in sentence[token_ind -1]['deprel']) or ('-' in sentence[token_ind -1]['text'] and 'compound:nmod' in sentence[token_ind -2]['deprel'])):
                print(entire_tok['deprel'])
                # get general info
                tok_list = [filename, language, register, s_ind + 1, entire_tok['id'], entire_tok['text'],
                            entire_tok['lemma'] if 'lemma' in entire_tok else '_',
                            entire_tok['deprel'] if 'deprel' in entire_tok else '_',
                            entire_tok['misc'] if 'misc' in entire_tok else '_',
                            sentence[token_ind - 1]['text'] if 'text' in sentence[token_ind - 1] else '_',
                            sentence[token_ind - 2]['text'] if 'text' in sentence[token_ind - 2] else '_']
                long_data_list.append(tok_list)
                comp_collect.append(entire_tok)

                # finish building compound entry, append and clear analysis_row, reset span_length
                # distinguish between span-comp and non-span-comp and hyphenated comp for building the whole-comp in analysis_row
                # only build whole compound if span_length is 0, if 2 or 3 it is already build in the span-elif
                print('Span length: ', span_length)
                if span_length == 0:
                    # look for hyphens, collect constituents and hyphens
                    # no hyphen
                    if len(comp_collect) == 3:
                        print('comp_collect: ', comp_collect)
                        # whole comp
                        comp_analysis_row[0] = comp_collect[0]['text'] + ' ' + comp_collect[1]['text'] + ' ' + comp_collect[2]['text']
                        comp_analysis_row[1] = comp_collect[0]['lemma'] + ' ' + comp_collect[1]['lemma'] + ' ' + comp_collect[2]['lemma']
                        # const_text
                        comp_analysis_row[2] = comp_collect[0]['text']
                        comp_analysis_row[3] = comp_collect[1]['text']
                        comp_analysis_row[4] = comp_collect[2]['text']
                        # const_lemma
                        comp_analysis_row[5] = comp_collect[0]['lemma']
                        comp_analysis_row[6] = comp_collect[1]['lemma']
                        comp_analysis_row[7] = comp_collect[2]['lemma']
                        # check head-structure considering possible hyphenation to determine branching structure
                        # then store branching-structure in analysis_row
                        if comp_collect[0]['head'] == comp_collect[1]['head']:
                            comp_analysis_row[8] = 'BC'
                        elif comp_collect[0]['head'] != comp_collect[1]['head']:
                            comp_analysis_row[8] = 'AB'


                    # 1 hyphen
                    if len(comp_collect) == 4:
                        # hyphen after first
                        if comp_collect[1]['text'] == '-':
                            # whole comp
                            comp_analysis_row[0] = comp_collect[0]['text'] + comp_collect[1]['text'] + ' ' + \
                                                   comp_collect[2]['text'] + ' ' + comp_collect[3]['text']
                            comp_analysis_row[1] = comp_collect[0]['lemma'] + comp_collect[1]['lemma'] + ' ' + \
                                                   comp_collect[2]['lemma'] + ' ' + comp_collect[3]['lemma']
                            # const_text / add hyphen to first
                            comp_analysis_row[2] = comp_collect[0]['text'] + comp_collect[1]['text']
                            comp_analysis_row[3] = comp_collect[2]['text']
                            comp_analysis_row[4] = comp_collect[3]['text']
                            # const_lemma / add hyphen to first
                            comp_analysis_row[5] = comp_collect[0]['lemma'] + comp_collect[1]['lemma']
                            comp_analysis_row[6] = comp_collect[2]['lemma']
                            comp_analysis_row[7] = comp_collect[3]['lemma']
                            # check head-structure considering possible hyphenation to determine branching structure
                            # then store branching-structure in analysis_row
                            if comp_collect[0]['head'] == comp_collect[2]['head']:
                                comp_analysis_row[8] = 'BC'
                            elif comp_collect[0]['head'] != comp_collect[2]['head']:
                                comp_analysis_row[8] = 'AB'



                        # hyphen after second
                        elif comp_collect[3]['text'] == '-':
                            # whole comp
                            comp_analysis_row[0] = comp_collect[0]['text'] + ' ' + comp_collect[1]['text'] + \
                                                   comp_collect[2]['text'] + comp_collect[3]['text']
                            comp_analysis_row[1] = comp_collect[0]['lemma'] + ' ' + comp_collect[1]['lemma'] + \
                                                   comp_collect[2]['lemma'] + comp_collect[3]['lemma']
                            # const_text / add hyphen to second
                            comp_analysis_row[2] = comp_collect[0]['text']
                            comp_analysis_row[3] = comp_collect[1]['text'] + comp_collect[2]['text']
                            comp_analysis_row[4] = comp_collect[3]['text']
                            # const_lemma / add hyphen to second
                            comp_analysis_row[5] = comp_collect[0]['lemma']
                            comp_analysis_row[6] = comp_collect[1]['lemma'] + comp_collect[2]['lemma']
                            comp_analysis_row[7] = comp_collect[3]['lemma']
                            # check head-structure considering possible hyphenation to determine branching structure
                            # then store branching-structure in analysis_row
                            if comp_collect[0]['head'] == comp_collect[1]['head']:
                                comp_analysis_row[8] = 'BC'
                            elif comp_collect[0]['head'] != comp_collect[1]['head']:
                                comp_analysis_row[8] = 'AB'


                    # 2 hyphens
                    if len(comp_collect) == 5:
                        # whole comp
                        comp_analysis_row[0] = comp_collect[0]['text'] + comp_collect[1]['text'] + \
                                               comp_collect[2]['text'] + comp_collect[3]['text'] + comp_collect[4]['text']
                        comp_analysis_row[1] = comp_collect[0]['lemma'] + comp_collect[1]['lemma'] + \
                                               comp_collect[2]['lemma'] + comp_collect[3]['lemma'] + comp_collect[3]['text']
                        # const_text / add hyphen to first and second
                        comp_analysis_row[2] = comp_collect[0]['text'] + comp_collect[1]['text']
                        comp_analysis_row[3] = comp_collect[2]['text'] + comp_collect[3]['text']
                        comp_analysis_row[4] = comp_collect[4]['text']
                        # const_lemma / add hyphen to first and second
                        comp_analysis_row[5] = comp_collect[0]['lemma'] + comp_collect[1]['lemma']
                        comp_analysis_row[6] = comp_collect[2]['lemma'] + comp_collect[3]['lemma']
                        comp_analysis_row[7] = comp_collect[4]['lemma']
                        # check head-structure considering possible hyphenation to determine branching structure
                        # then store branching-structure in analysis_row
                        if comp_collect[0]['head'] == comp_collect[2]['head']:
                            comp_analysis_row[8] = 'BC'
                        elif comp_collect[0]['head'] != comp_collect[2]['head']:
                            comp_analysis_row[8] = 'AB'

                # append
                print(comp_analysis_row)
                if comp_analysis_row != ['compound','comp_lemma','const_1_text','const_2_text','const_3_text','const_1_lemma','const_2_lemma','const_3_lemma','gold_branching','language','register']:
                    comp_analysis_row[9] = language
                    comp_analysis_row[10] = register
                    long_data_list_analysis.append(comp_analysis_row)
                print('Appended analysis_row in span0')
                # clear
                comp_analysis_row = ['compound','comp_lemma','const_1_text','const_2_text','const_3_text','const_1_lemma','const_2_lemma','const_3_lemma','gold_branching','language','register']
                span_length = 0
                comp_collect = []

            # catch hyphens
            elif 'text' in entire_tok and entire_tok['text'] != '' and entire_tok['text'] == '-' and ('compound:nmod' in sentence[token_ind +1][
                'deprel'] or 'compound:nmod' in sentence[token_ind - 1]['deprel']):
                print(entire_tok['deprel'])
                # get general info
                tok_list = [filename, s_ind + 1, entire_tok['id'], entire_tok['text'],
                            entire_tok['lemma'] if 'lemma' in entire_tok else '_',
                            entire_tok['deprel'] if 'deprel' in entire_tok else '_',
                            entire_tok['misc'] if 'misc' in entire_tok else '_',
                            sentence[token_ind - 1]['text'] if 'text' in sentence[token_ind - 1] else '_',
                            sentence[token_ind - 2]['text'] if 'text' in sentence[token_ind - 2] else '_']
                long_data_list.append(tok_list)
                comp_collect.append(entire_tok)

            # all other toks replace text and lemma with '_'
            else:
                print('No compound')
                entire_dict[s_ind][token_ind]['text'] = '_'
                entire_dict[s_ind][token_ind]['lemma'] = '_'

    # export modified .conllu
    new_doc = Document(entire_dict)
    CoNLL.write_doc2conll(new_doc, filename[:-7] + "_onlycomp.conllu")

# export general comp info
with open('comp_info_example_all_annotations.csv', 'w', newline='', encoding='utf8') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerows(long_data_list)

# export analysis file for transparency analysis
with open('comp_extraction_for_transparency_example.csv', 'w', newline='', encoding='utf8') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerows(long_data_list_analysis)
