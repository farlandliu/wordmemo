# -*- coding: utf-8 -*-
import sys
from datetime import datetime, timedelta
from peewee import *
from wordmemo.models import db as database
from wordmemo.models import Word, Deck, Card, DeckLog
from colorama import Fore, Back, Style
from colorama import init   #, AnsiToWin32

init(autoreset=True)
"""
init:
1. create_tables, word()
2. init_deck_card()

"""
def create_tables():
    database.connect()
    database.create_tables([Word, Deck,Card])

def init_deck_cards(deck_name='default'):
    deck = Deck.get_or_create(name=deck_name)
    deck[0].save()
    words = Word.select()
    for wd in words:
        card = Card(
            deck=deck[0],
            word=wd, 
            state=0)
        card.save()

def create_cards():
    deck = Deck.get()
    words = Word.select()
    for wd in words:
        card = Card()
        card.dock = deck
        card.word = wd
        card.save()

def study_loop():
    print(Fore.BLUE + "  ======Studying=======\n")
    action = ""
    while action !="q":
        card = deck_pop()
        if card:
            print(Fore.YELLOW + '   ' +card.word.name )
            print("\n 1=easy,2=general,3=hard, 4=bury, q=quit studying")
            action = input('>>your choice?: ').lower().strip()
            if action != 'q':
                card_update(card,action)
        else:
            print(Fore.RED + "No more words to study!")
            break


def deck_pop():
    deck = Deck.get()
    cards = Card.select().where(Card.deck==deck,Card.state==0)
    if cards:
        return cards[0]

def deck_review():
    pass

def show_deck():
    pass
def deck_log(card):
    deck = Deck.get()
    log = DeckLog()
    log.deck = deck
    log.card = card
    log.card_state_before = card.state
    log.update_when = datetime.now()
    log.save()

def card_update(card,action=None):
    deck_log(card)
    state = card.state
    if action !='4':
        if action == '1':
            st = 4
        elif action == '2':
            st = 2
        elif action == '3':
            st = 1
        card.state = st
        card.due_date = datetime.now() + timedelta(days=st)
    elif action == '4':
        card.state = -1
    card.save()

from collections import OrderedDict

menu = OrderedDict([
    ('s', study_loop), 
    ('r', deck_review),
    ('l', show_deck),

])

def main_menu():
    choice = None
    while choice != 'q':
        print(Fore.BLUE + "  ======Main Menu=======\n")
        print("  (S): study words")
        print("  (R): review the words learned today")
        print("  (L): list words collections")
        print("  (Q): quit")

        # for key, value in menu.items():
        #     print('%s) %s' % (key, value.__doc__))
        choice = input('>>Action: ').lower().strip()

        if choice in menu:
            menu[choice]()
        elif choice == 'q':
            sys.exit(1)


def create_schedule(deck_name='new_list'):
    deck = Deck.get(name=deck_name)
    cards = Card.select().where(Card.dock==deck)
    # initial schedule
    # normal order or random order
    n = 1
    num = cards.count()
    while (n < num):
        cards[n].queue = n
        print(cards[n].word.name)
        cards[n].save()
        n = n + 1


def word():
    words_list = []
    f = open('wds.txt','r')
    words_text = f.readlines()
    for line in words_text:
        # word = fix_words(line)
        if line:
            wd = Word.get_or_create(name=line.replace('\n',''))
            wd[0].save()
    return words_list

"""
1. isalpha() & islower()

"""

def fix_words(line):
    # import pdb; pdb.set_trace() 
    
    if len(line) < 2:
        return ''
    word_piece = line.split()
    # print word_piece
    # print len(word_piece)
    phrase = ''
    for nn in range(0,len(word_piece)):
        if word_piece[nn].islower() and word_piece[nn].isalpha():
            phrase += word_piece[nn] + ' '  
    return phrase

if __name__ == '__main__':
    main_menu()
