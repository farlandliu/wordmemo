# -*- coding:utf-8 -*- 
import os, sys
import click
import json
import requests
from bs4 import BeautifulSoup
from colorama import init   #, AnsiToWin32
from colorama import Fore, Back, Style
from wordmemo.models import db, WordLib
init(autoreset=True)

class Dict(object):
    """docstring for Dict"""
    def __init__(self, arg):
        super(Dict, self).__init__()
        self.arg = arg
        self.db = db
        self.api = ''
        self.provider = ''
        self.title = ''

    def show(self):
        pass

    def _get_raw(self, word: str) -> str:
        headers = {'user-agent':"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0"}
        
        try:
            res = requests.get(
                self._get_url(word), headers=headers
            )
        except requests.exceptions.ReadTimeout as e:
            raise exceptions.TimeoutError()

        # if res.status_code != 200:
        #     raise exceptions.QueryError(word, res.status_code)
        return res.text

    def query_db_cache(self, word: str) -> WordLib:
        try:
            record = WordLib.get(word=word, source=self.provider)
        except WordLib.DoesNotExist:
            return None
        else:
            return record

    def save(self, query_record: WordLib, word: str):
        db_record = self.query_db_cache(word)

        if db_record is None:
            query_record.save(force_insert=True)
        else:
            db_content = json.loads(db_record.content)
            query_content = json.loads(query_record.content)

            if db_content != query_content:
                db_record.content = query_record.content
                db_record.save()

    def lookup(self, word):
        word = word.lower()

        # if self.args.show_provider:
        #     self.show_provider()

        # if self.args.show_url:
        #     self.show_url(word)

        # if not self.args.disable_db_cache:
        record = self.query_db_cache(word)

        if record:
            self.show(record)
            return

        try:
            record = self.query(word)
        except error as e:
            print(e)
        # except exceptions.TimeoutError as e:
        #     self.color.print(e, 'red')
        #     print()
        # except exceptions.NotFoundError as e:
        #     self.color.print(e, 'yellow')
        #     print()
        else:
            self.save(record, word)
            self.show(record)
            return

class Collins(Dict):
    """Bing  online query"""
    def __init__(self,arg):
        super(Collins, self).__init__(arg)
        self.arg = arg
        self.api = 'https://www.collinsdictionary.com/dictionary/english/{word}'
        self.provider = 'cobu'
        self.title = 'Collins Cobuild Ads Dictionary'


    def _get_url(self, word) -> str:
        return self.api.format(word=word)

    def show(self, db_cache: WordLib):
        content = json.loads(db_cache.content)

        # print word ,pronounce
        print(Fore.RED + content['word']+ content['pronounce'])

        # print explain
        main_explanations = content.get('explain', [])
        #if self.args.verbose:
        #    main_explanations.extend(content.get('verbose', []))

        # explain = ['word forms',[sense1, sense2]]
        # sense = [grammar, example1,examle2]
        print(main_explanations[0])

        for speech in main_explanations[1:]:
            # print word forms
            print(speech[0])
            # print sense items
            for meaning in speech[1:]:
                
                for sentence in meaning[1:]:
                    if sentence:
                        print(' ' * 2, end='')
                        for i, s in enumerate(sentence.split('*')):
                            print(Fore.BLUE + s)
            print()

    def query(self, word: str):
        webpage = self._get_raw(word)
        data_root = BeautifulSoup(webpage, "html.parser")
        data_root = data_root.find('div', class_='dictionary Cob_Adv_Brit')
        # sometimes there are two dict sections, if there are two,
        # we use the 2nd one
        dicts = data_root.find_all('div', 'dictentry')
        if len(dicts) >1 :
            data = dicts[1]
        else:
            data = dicts[0]

        content = {}

        # handle record.word
        try:
            content['word'] = data.find('span', class_='orth').text
        except AttributeError:
            raise NotFoundError(word)

        # handle pronounce
        pronu_value = data.find('span', class_='mini_h2')
        if pronu_value:
            content['pronounce'] = pronu_value.text.replace('\n','')
    
        # handle sound
        # skip
        # Handle explain
        definations = data.find(
            class_='content definitions cobuild br'
        )
        # explain = ['word forms',[sense1, sense2]]
        # sense = [grammar, example1,examle2]
        content['explain'] = []
        
        # handle word forms = content['explain'][0]
        forms = definations.find('span', class_='form inflected_forms type-infl')
        forms_text = forms.text if forms else ' '
        content['explain'].append(forms_text.replace('\n',''))

        #handle defination items
        def_items = definations.find_all('div', 'hom')
        for item in def_items:
            """
            structure:
            [num+ grammar + defs],[ex1],[ex2]

            """
            sense_item = []
            # sen_num = ''
            extra = item.find('span',class_='xr')
            if not extra:
                sen_num = item.find('span', class_='span sensenum')
                sen_num = sen_num.text if sen_num else ''
                sen_grm = item.find('span', class_='gramGrp')
                sen_grm = sen_grm.text if sen_grm else ' '
                sen_def_list = item.find_all('div', class_='def')
                sen_defs = ''   # store the definitaion
                # import pdb;pdb.set_trace()
                for sen_def in sen_def_list:
                    sen_defs += sen_def.text.replace('\n', '')
                sense_item.append(sen_num + sen_grm + '\n' + sen_defs)
                sen_examples = []
                examples = item.find_all('div', class_='cit type-example')
                if examples:
                    for ex in examples:
                        sen_examples.append(ex.text + '\n')
                    sense_item.append(sen_examples)
            else:
                sen_num = item.find('span', class_='span sensenum')
                sen_num = sen_num.text if sen_num else ''
                sense_item.append(sen_num + extra.text)
            content['explain'].append(sense_item)

        # todo: copyright for dictionary     

        result = WordLib(
            word=word,
            content=json.dumps(content),
            source=self.provider,
        )
        return result

class Bing(Dict):
    """Bing  online query"""
    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg
        self.url = 'https://www.collinsdictionary.com/dictionary/english/{word}'
        