
# -*- coding:utf-8 -*-
import os,sys
import peewee
from datetime import datetime



BASE_DIR_NAME = 'wordmemo'
HOME_DIR = os.getenv('HOME')
#BASE_DIR = os.path.split(os.path.realpath(__file__))[0]
DB_NAME = '.word.db'
DB_FILE = os.path.join(HOME_DIR, DB_NAME)
db = peewee.SqliteDatabase(DB_FILE)
# db = peewee.SqliteDatabase(DB_NAME)

"""
interval= 1,2,4,7,15,30,60
d1: 10 new words
d2: 10 new words, plus words need be reviewed
d3: 10 new words, plus words need be reviewed

queue_today = word_state_new + word_state_learning + word_state_review
when learning , queue_id = 0

"""
class Word(peewee.Model):
    id = peewee.PrimaryKeyField()
    name = peewee.TextField(index=True, unique=True)
    content =peewee.TextField(null=True)
    source = peewee.TextField(null=True)

    class Meta:
        #primary_key = peewee.CompositeKey('name', 'provider')
        database = db

# class User(peewee.Model):
#     id = peewee.PrimaryKeyField()
#     name = peewee.TextField(unique=True)

#     class Meta:
#         database = db

class Deck(peewee.Model):
    id = peewee.PrimaryKeyField()
    name = peewee.TextField()
    update_when = peewee.DateField(default=datetime.now())
    status = peewee.TextField(null=True)

    class Meta:
        database = db

    def pop(self):
        pass

class Card(peewee.Model):
    """
    Type: 0=new, 1=learning, 2=due, 4=review(when int>30), 5=bury(means finishing)

    lim:
    """
    id = peewee.PrimaryKeyField()
    word = peewee.ForeignKeyField(Word, related_name='from_word')
    deck = peewee.ForeignKeyField(Deck, related_name='from_deck')
    state = peewee.IntegerField(default=0)
    due_date = peewee.DateField(null=True)
    queue = peewee.IntegerField(null=True) # queue id for the schedule, =-1 if learning
    class Meta:
        database = db

class DeckLog(peewee.Model):
    id = peewee.PrimaryKeyField()
    deck = peewee.ForeignKeyField(Deck)
    card = peewee.ForeignKeyField(Card)
    card_state_before = peewee.IntegerField()
    update_when = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db

class WordLib(peewee.Model):
    """
    store vocabularies queried online
    """
    word = peewee.TextField()
    content = peewee.TextField()
    source = peewee.CharField()
    update_when = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db
        primary_key = peewee.CompositeKey('word', 'source')


