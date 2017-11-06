#!/usr/bin/env python
"""
2017-11
This code authored by EnterPin
this uses either the Advanced or Basic questions text files included with the Canadian
Ham Radio certification self test program for windows called ExHaminer available
at http://wp.rac.ca/exhaminer-v2-5/ which reportedly works in wine, but since
I'm a terminal jockey I wanted a lighter weight and self spun study aid
"""

import signal
import sys
import random
import re

#this also works with Questions_Advanced
#it's expected that this
RawQuestions = open("Questions_Basic.txt").read()
AllQuestions = {}
AnsweredWrong = set()
AnsweredRight = set()

"""
CapitalizedCamelCase = 'global variables'
lowerCamelCase = 'local variables'
underline_split = 'functions'
"""

def signal_handler(signal, frame):
    print('\n'+'-_'*30)
    print('so far you have gotten %i right and %i wrong.' % (len(AnsweredRight),len(AnsweredWrong)))
    print('-_'*30)
    if len(AnsweredWrong) > 0:
        print('\nYou answered the following questions Wrong.')
        for wrongAnswers in AnsweredWrong:
            print(wrongAnswers)
    sys.exit(0)

def build_questions():
    for i in re.split("\s*(?=[A|B]-[0-9]*-[0-9]*-[0-9]*.*)", RawQuestions):
        if re.search("([A|B]-[0-9]*-[0-9]*-[0-9]*)", i):
            m = re.compile("(?P<ID>[A|B]-[0-9]*-[0-9]*-[0-9]*)( \()(?P<ANSWER>[A-D])(\) )(?P<QUESTION>.*)(\r\n)(A\t)(?P<QA>.*)(\r\n)(B\t)(?P<QB>.*)(\r\n)(C\t)(?P<QC>.*)(\r\n)(D\t)(?P<QD>.*)(\r\n)(>)(?P<KEYWORD>.*)", re.MULTILINE)
            ma = m.match(i)
            if not ma:
                wat.append(i)
                print('Parsing error')
                print(wat)
                continue
            AllQuestions[ma.group('ID')] = {'question':ma.group('QUESTION'),
            'answer':ma.group('ANSWER'),'qa':ma.group('QA'),'qb':ma.group('QB'),
            'qc':ma.group('QC'),'qd':ma.group('QD'),'keyword':ma.group('KEYWORD')}
    re.purge()

def ask_question():
    print('\n'+'-'*30)
    toAsk = random.choice(AllQuestions.keys())
    print("%s\nQuestion: %s\nPossible Answers\nA: %s\nB: %s\nC: %s\nD: %s\n"
    % (str(toAsk),AllQuestions[toAsk]['question'],AllQuestions[toAsk]['qa'],
    AllQuestions[toAsk]['qb'],AllQuestions[toAsk]['qc'],
    AllQuestions[toAsk]['qd']))
    getAnswer = raw_input("Please enter your answer: ")
    print('\n'+'-'*30)
    if str(getAnswer).lower() == str(AllQuestions[toAsk]['answer']).lower():
        print('Correct!\n')
        AnsweredRight.add(toAsk)
    else:
        print('WRONG!\nHere is why you are wrong: %s' %
        AllQuestions[toAsk]['keyword'])
        AnsweredWrong.add(toAsk)
    print('so far you have gotten %i right and %i wrong.' %
    (len(AnsweredRight),len(AnsweredWrong)))


def main():
    build_questions()
    while True:
        signal.signal(signal.SIGINT, signal_handler)
        print('Press Ctrl+C to quit')
        ask_question()

if __name__ == '__main__':
    main()
