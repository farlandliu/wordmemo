#!/usr/bin/env python
# -*- coding:utf-8 -*- 
import os, sys
import urllib2, urllib
import click
from bs4 import BeautifulSoup
from colorama import init   #, AnsiToWin32
from colorama import Fore, Back, Style

"""
Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
Style: DIM, NORMAL, BRIGHT, RESET_ALL
"""
init(autoreset=True)

def wd(word):
    wd_dict ={
    'word':'',
    'cob': '',
    }
    headers = {'user-agent':"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0"}   
    url = 'https://www.collinsdictionary.com/dictionary/english/' + word
    try:
            res = requests.get(
                url, timeout=10, headers=headers
            )
        except requests.exceptions.ReadTimeout as e:
            raise exceptions.TimeoutError()
   
    content = res.text  
    root = BeautifulSoup(content,  "html.parser")

    dicts = root.find("div", class_="dictionary")
    cob_root = dicts.find("div", class_="dictionary Cob_Adv_Brit")
    ame = dicts.find("div", class_="content-box content-box-definition american")
    # collins
    ced = dicts.find("div", class_="content-box content-box-definition ced") 
    
    # cobuild dic
    cob ={
    'word': "",
    'pro': "",
    'content': "",
    'copyright':""
    }
    cob['word'] += cob_root.h2.get_text()
    # import pdb;pdb.set_trace() 
    pro = cob_root.find("span", class_="mini_h2")
    cob['pro'] += cob_root.find("span", class_="mini_h2").text.replace('\n', '') +'\n'
    cob['content'] += cob_root.find("span", class_="form inflected_forms type-infl").text.replace('\n', '') + '\n\n' 
    sensenum = cob_root.find_all("div", class_="hom")
    for sen in sensenum:
    	cob['content'] += sen.get_text() 
    cob['copyright'] += cob_root.find("div", "div copyright").text
    print Fore.RED + cob['word']  
    print Fore.GREEN + cob['pro']  
    print  cob['content']  
    print Style.DIM + cob['copyright']  


@click.command()
@click.argument('word')
def cli(word):
    print Style.DIM + "Collins Dictionary ..."
    wd(word)

if __name__ == '__main__':
    cli()
