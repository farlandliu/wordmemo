# -*- coding: utf-8 -*-
import sys
from datetime import datetime, timedelta
import click
from colorama import Fore, Back, Style
from colorama import init   #, AnsiToWin32
from wordmemo.models import db as database
from wordmemo.dict import Bing, Collins
from wordmemo.models import Word, Deck, Card, DeckLog

bing = Bing(False)
collins = Collins(False)
init(autoreset=True)
global default_deck
default_deck = Deck.get()
"""
init:
1. create_tables, word()
2. init_deck_card()

"""
# ====init app====

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

# ====main command app====
def study_loop():
    print(Fore.BLUE + "  ======Study=======\n")
    deck_today()
    action = ""
    while action !="q":
        card = deck_pop()
        if card:
            print(Fore.YELLOW + '   ' +card.word.name )
            print("\n 1=easy,2=general,3=hard, 4=bury, q=quit b=Bing c=Collins")
            action = input('>>: ').lower().strip()
            if action == 'b':
                bing.lookup(card.word.name)
                print('*** End of Explaination ***')
            elif action == 'c':
                collins.lookup(card.word.name)
                print('*** End of Explaination ***')
            elif action == 'q':
                return
            else:
                card_update(card,action)

        else:
            print(Fore.RED + "No more words to study!")
            break


def deck_pop():
    global default_deck
    cards = Card.select().where(Card.state==0).join(Deck).where(Deck.name==default_deck.name)
    cards_review_today = Card.select().join(Deck).where(
        Deck.name==default_deck.name,
        Card.due_date <= datetime.now().date())
    if cards_review_today:
        return cards_review_today[0]
    if cards:
        return cards[0]

def deck_today():
    global default_deck
    print('----deck-today: ' + default_deck.name)
    import pdb;pdb.set_trace()
    new_words = Card.select().join(Deck).where(Deck.name==default_deck.name, Card.state==0)
    print('New Words to Learn: ' + str(new_words.count()))
    words_review_today = Card.select().join(Deck).where(
        Deck.name==default_deck.name,
        Card.due_date <= datetime.now().date())
    print('words to Review: ' + str(words_review_today.count()))

def deck_review():
    pass

def deck_select():
    """select default deck or create a new deck """
    global default_deck
    decks = Deck.select()
    id_list = []
    for deck in decks:
        print(str(deck.id) + '. ' + deck.name)
        id_list.append(str(deck.id))
    raw_input = input('select deck id or intput deck name to create new deck:\n >>').lower().strip()
    if raw_input in id_list :
        default_deck = Deck.get(Deck.id==int(raw_input))
        print('default deck is set to : %s'%default_deck.name)
    elif len(raw_input) > 1:
        default_deck = Deck(name=raw_input)
        default_deck.save()
        print('new deck created: %s'%default_deck.name)
        print('default deck is set to : %s'%default_deck.name)


def deck_log(card):
    global default_deck
    log = DeckLog()
    log.deck = default_deck
    log.card = card
    log.card_state_before = card.state
    log.update_when = datetime.now()
    log.save()

def card_update(card,action=None):
    deck_log(card)
    state = card.state
    if action != '4':
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
        card.due_date = None
    card.save()

from collections import OrderedDict

menu = OrderedDict([
    ('d', deck_select),
    ('s', study_loop),
    ('r', deck_review),
    # ('l', show_deck),

])

def main_menu():
    global default_deck
    default_deck = Deck.get()
    print('----deck: ' + default_deck.name)
    choice = None
    while choice != 'q':
        print(Fore.BLUE + "  ======Main Menu=======\n")
        print("  (D): select deck. current deck: %s"%default_deck.name )
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

@click.command(name='add')
@click.argument('word')
def word_add(word):
    pass


def cli():
    global default_deck
    default_deck = Deck.get()
    main_menu()

if __name__ == '__main__':
    cli()
