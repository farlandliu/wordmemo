# -*- coding: utf-8 -*-
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



count = 0
while (count < 9):
    print ('The count is:', count)
    count = count + 1
 
print "Good bye"


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
