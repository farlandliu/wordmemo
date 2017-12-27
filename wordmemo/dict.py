# -*- coding:utf-8 -*- 
import os, sys
import click
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from colorama import init   #, AnsiToWin32
from colorama import Fore, Back, Style
from wordmemo.models import db, WordLib, Card, Word, Deck
init(autoreset=True)

class Dict(object):
    """docstring for Dict"""
    def __init__(self, disable_cache=False):
        super(Dict, self).__init__()
        self.disable_cache = disable_cache
        self.db = db
        self.api = ''
        self.provider = ''
        self.title = ''

    def show(self, db_cache: WordLib):
        content = json.loads(db_cache.content)
        print (Style.DIM + self.title + '.'*3)

        # print word ,pronounce
        print(Fore.RED + content['word'])
        print(content['pronounce'])
        # print explain
        main_explanations = content.get('explain', [])
        
        # explain = ['word forms',[sense1, sense2]]
        # sense = [grammar, sen1 ,sen2]
        print(main_explanations[0])

        for speech in main_explanations[1]:
            # print word forms
            print(Fore.BLUE + speech[0])
            # print sense items
            for meaning in speech[1:]:
                print('  ' + meaning)
            # print()

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
        if not self.disable_cache:
            record = self.query_db_cache(word)
            if record:
                self.show(record)
                return
        try:
            record = self.query(word)

        except :
            print('error')
        else:
            self.save(record, word)
            self.show(record)
            return

class Collins(Dict):
    """Collins online query"""
    def __init__(self,disable_cache):
        super(Collins, self).__init__(disable_cache)
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
                        print( '  ' +Fore.BLUE + sentence)
            # print()

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
                for sen_def in sen_def_list:
                    sen_defs += sen_def.text.replace('\n', '')
                sense_item.append(sen_num + sen_grm + '\n' + sen_defs)
                sen_examples = []
                examples = item.find_all('div', class_='cit type-example')
                if examples:
                    for ex in examples:
                        sen_examples.append(ex.text)
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
    """Bing Dcitionary online query"""
    def __init__(self, disable_cache=False):
        super(Bing, self).__init__(disable_cache)
        self.api = 'https://www.bing.com/dict/search?q={word}'
        self.provider = 'Bing'
        self.title = 'Bing Dictionary'

    def _get_url(self, word) -> str:
        return self.api.format(word=word)

    # def show(self, db_cache: WordLib):
    #     content = json.loads(db_cache.content)

    def query(self, word: str):
        webpage = self._get_raw(word)
        data_root = BeautifulSoup(webpage, "html.parser")
        #['word','pron','explain']
        # explain = ['word forms',[sense1, sense2]]
        # sense = [grammar, example1,examle2]
        content = {}
        # head word
        head_word = data_root.find('div', id='headword')
        if head_word:
            content['word'] = head_word.text
        else:
            raise NotFoundError(word)
        # handle pron hd_p1_1
        pron = data_root.find("div", class_="hd_p1_1")

        if pron:
            content['pronounce'] = pron.text 
        else :
            content['pronounce'] =''

        content['explain'] = [] # thes,[sen1],[sens2]
        thesaurus = data_root.find("div", id="thesaurusesid") #hd_if
        thesaurus = data_root.find("div", class_='hd_if')
        if thesaurus:
            content['explain'].append(thesaurus.text)
        else:
            content['explain'].append('')
        sense_list = []
        sen_parts = data_root.find("div",id="authid").find_all('div',class_='each_seg')
        for sen_item in sen_parts:
            sen = []
            sen.append(sen_item.find('div', class_='pos_lin').text)
            meanings = sen_item.find_all('div', class_='se_lis')
            for meaning in meanings:
                en_tag = meaning.find('span', class_='val')
                t = en_tag.extract()
                sen.append(meaning.text + '\n'+ ' '*4 + t.text)
            sense_list.append(sen)

        content['explain'].append(sense_list)

        result = WordLib(
            word=word,
            content=json.dumps(content),
            source=self.provider,
        )
        return result

dict_choice = ['bing', 'collins']

@click.command()
@click.option('-d', '--disable_cache', is_flag=True, default=False, help='disable cache')
@click.option('-s', '--select_dict', type=click.Choice(dict_choice), help='select dictionary')
@click.option('-a', '--add_to_deck', is_flag=True,  help='add word to deck')
@click.argument('word')
def cli(word,disable_cache, select_dict, add_to_deck):
    default_deck = Deck.get()
    if not select_dict: select_dict = dict_choice[1]
    if word and add_to_deck:
        wd = Word.get_or_create(name=word)[0]
        card = Card()
        card.word = wd
        card.deck = default_deck
        card.due_date = datetime.now() + timedelta(days=2)
        card.save()
        print(word + ' is added to deck: ' + default_deck.name)
        return 
    elif word  and select_dict:
        if select_dict == dict_choice[0]:
            wd=Bing(disable_cache)
    
        elif select_dict == dict_choice[1]:
            wd = Collins(disable_cache)
        wd.lookup(word)
        

if __name__ == '__main__':
    cli()

        