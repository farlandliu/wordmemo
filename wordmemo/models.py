
# -*- coding:utf-8 -*-
import os
import peewee
from datetime import datetime

BASE_DIR_NAME = '.wordmemo'
BASE_DIR = os.path.join(os.getenv('HOME'), BASE_DIR_NAME)
DB_NAME = 'word.db'
DB_FILE = os.path.join(BASE_DIR, DB_NAME)
# db = peewee.SqliteDatabase(DB_FILE)
db = peewee.SqliteDatabase(DB_NAME)

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
    provider = peewee.TextField(null=True)

    class Meta:
        #primary_key = peewee.CompositeKey('name', 'provider')
        database = db

class User(peewee.Model):
    id = peewee.PrimaryKeyField()
    name = peewee.TextField(unique=True)

    class Meta:
        database = db

class Deck(peewee.Model):
    id = peewee.PrimaryKeyField()
    name = peewee.TextField()
    user = peewee.ForeignKeyField(User, related_name='deck')
    update_when = peewee.DateField(default=datetime.now())

    class Meta:
        database = db

class Card(peewee.Model):
    """
    Type: 0=new, 1=learning, 2=due, 4=review(when int>30), 5=bury(means finishing)

    lim:
    """
    id = peewee.PrimaryKeyField()
    word = peewee.ForeignKeyField(Word, related_name='from_word')
    dock = peewee.ForeignKeyField(Deck, related_name='from_deck')
    card_type = peewee.IntegerField(default=0)
    limit = peewee.DateField(null=True)
    queue = peewee.IntegerField(null=True) # queue id for the schedule, =-1 if learning
    class Meta:
        database = db

class Record(peewee.Model):
    '''
    # This model schema is from zdict.
    A model for storing the query results into the SQLite db.

    :param word: the vocabulary
    :param content: the query result of the vocabulary.
        It's a json document has the following spec.
        {
            'word': word,
            // storing the querying result.
            'pronounce': [
                ('key', 'value'),
                ...
            ],
            'sound': [
                ('type', 'url'),
                ...
                // type: (mp3|ogg)
            ],
            'explain': [
                ('speech',
                    (
                        'meaning',
                        ('sentence1', 'translation'),
                        ...
                    ),
                    ...
                ),
                ...
            ]
        }
    :param source: source of the content. May be Yahoo!, Google, ... Dict
    '''

    word = peewee.TextField()
    content = peewee.TextField()
    source = peewee.CharField()

    class Meta:
        database = db
        primary_key = peewee.CompositeKey('word', 'source')