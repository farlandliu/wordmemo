# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from peewee import *
from wordmemo.models import db as database
from wordmemo.models import User,Word, Deck, Card

def create_tables():
    database.connect()
    database.create_tables([User, Word, Deck,Card])


def create_cards():
    user =User.get()
    deck = Deck.get()
    words = Word.select()
    for wd in words:
        card = Card()
        card.user = user
        card.dock = deck
        card.word = wd
        card.save()

def deck_pop(deck):
    deck = Deck.get()
    cards = Card.select().where(Card.dock==deck,Card.card_type==0)
    print(cards[0].word.name)
    print("\n e=easy,g=general,h=hard")
    card_update(cards[0],input('your selecttion?: '))

def card_update(card,action=None):
    if action == 'e':
        st = 7
    elif action == 'g':
        st = 4
    elif action == 'h':
        st = 1

    card.state = st
    card.due_limit = card.due_limit + timedelta(days=st)
    card.save()
    print("n) for next word ")
    print("q) quit learning session")
    action = raw_input('Choice? (nq) ').lower().strip()
    if action == 'n':
        deck_pop()
    elif action == 'q':
        main_menu()

from collections import OrderedDict

menu = OrderedDict([
    ('l', deck_pop),
   
])

def menu_loop():
    choice = None
    while choice != 'q':
        for key, value in menu.items():
            print('%s) %s' % (key, value.__doc__))
        choice = raw_input('Action: ').lower().strip()
        if choice in menu:
            menu[choice]()


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
    f = open('wd.txt','r')
    words_text = f.readlines()
    for line in words_text:
        word = fix_words(line)
        if word:
            words_list.append(word)
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
