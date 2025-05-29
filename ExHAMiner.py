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
import textwrap

#this also works with Questions_Advanced
#it's expected that this
AllQuestions = {}
AnsweredWrong = set()
AnsweredRight = set()

"""
CapitalizedCamelCase = 'global variables'
lowerCamelCase = 'local variables'
underline_split = 'functions'
"""

class Question:
    def __init__(self,
                 qID: str,
                 qQuestion: str,
                 qCorrect: str,
                 qAnswers: dict[str, str],
                 qKeyWord: str,):
        self.qID = qID
        self.qQuestion = qQuestion
        self.qCorrect = qCorrect
        self.qAnswers = qAnswers
        self.qKeyWord = qKeyWord

    def get_answers(self):
        out = "\n"
        for k, v in self.qAnswers.items():
            out += f"  | {k}: {textwrap.fill(v).replace('\n', '\n  |    ')}\n"

        return out

def signal_handler(signal, frame):
    print('\n'+'-_'*30)
    print('so far you have gotten %i right and %i wrong.' % (len(AnsweredRight),len(AnsweredWrong)))
    print('-_'*30)
    if len(AnsweredWrong) > 0:
        print('\nYou answered the following questions Wrong.')
        for wrongAnswers in AnsweredWrong:
            print(wrongAnswers)
    sys.exit(0)

def build_questions(bank_path: str) -> dict[str, Question]:
    """
    Parse the question bank as specified by the bank path

    params
    ------
    - bank_path (str) a path to the question bank

    returns a question bank, keys being the question ID and values being details
    about the question
    """
    rawQuestions = None
    allQuestions = {}
    with open(bank_path, "r") as f:
        rawQuestions = f.read()

    for i in re.split("(?=[A|B]-[0-9]*-[0-9]*-[0-9]*.*)", rawQuestions):
        if not re.search("([A|B]-[0-9]*-[0-9]*-[0-9]*)", i): continue
        ma = re.match("(?P<ID>[A|B]-[0-9]*-[0-9]*-[0-9]*)( \()(?P<ANSWER>[A-D])(\) )(?P<QUESTION>.*)(\r?\n)(A\t)(?P<QA>.*)(\r?\n)(B\t)(?P<QB>.*)(\r?\n)(C\t)(?P<QC>.*)(\r?\n)(D\t)(?P<QD>.*)(\r?\n)(> )(?P<KEYWORD>.*)",
                       i,
                       re.MULTILINE)
        if not ma:
            wat = bytes(i, "ascii")
            print('Parsing error')
            print(wat)
            continue
        allQuestions[ma.group('ID')] = Question(ma.group('ID'),
                                                ma.group('QUESTION'),
                                                ma.group('ANSWER'),
                                                {"A": ma.group('QA'),
                                                 "B": ma.group('QB'),
                                                 "C": ma.group('QC'),
                                                 "D": ma.group('QD')},
                                                ma.group('KEYWORD'))
    re.purge()

    return allQuestions

def random_question(allQuestions: dict[str, Question],
                    tuiMode=True):
    print("\033[100A\033[J", end="")
    toAsk = random.choice(list(allQuestions.keys()))
    print(f"""Q: {toAsk} - {textwrap.fill(allQuestions[toAsk].qQuestion, 70)}
{allQuestions[toAsk].get_answers()}""")
    print('\n'+'-'*30)
    print(f'so far you have gotten {len(AnsweredRight)} right and {len(AnsweredWrong)} wrong.')

    getAnswer = input("Please enter your answer: ")
    print('\n'+'-'*30)
    if str(getAnswer).lower() == str(allQuestions[toAsk].qCorrect).lower():
        print('Correct!\n')
        AnsweredRight.add(toAsk)
    else:
        print(f"""WRONG! the answer was {allQuestions[toAsk].qCorrect}

Here is why you are wrong:
{textwrap.fill(allQuestions[toAsk].qKeyWord, 80)}""")
        AnsweredWrong.add(toAsk)
        input('Press enter to continue...')


def main():
    if(len(sys.argv) < 2):
        print(f"[-] usage: {sys.argv[0]} <./path/to/question/bank>")
        exit(1)
    bank_path = sys.argv[1]
    q_bank = build_questions(bank_path)
    while True:
        signal.signal(signal.SIGINT, signal_handler)
        print('Press Ctrl+C to quit')
        random_question(q_bank)

if __name__ == '__main__':
    main()
