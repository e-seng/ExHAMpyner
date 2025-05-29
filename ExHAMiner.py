#!/usr/bin/env python
"""
2017-11
This code authored by EnterPin
this uses either the Advanced or Basic questions text files included with the Canadian
Ham Radio certification self test program for windows called ExHaminer available
at http://wp.rac.ca/exhaminer-v2-5/ which reportedly works in wine, but since
I'm a terminal jockey I wanted a lighter weight and self spun study aid
"""

import sys
import random
import itertools
import re
import textwrap
import traceback
import argparse

#this also works with Questions_Advanced
#it's expected that this
AllQuestions = {}
AnsweredWrong = set()
AnsweredRight = set()
Categories = []

"""
CapitalizedCamelCase = 'global variables'
lowerCamelCase = 'local variables'
underline_split = 'functions'
"""

class Question:
    def __init__(self,
                 qID: str,
                 qCategory: str,
                 qQuestion: str,
                 qCorrect: str,
                 qAnswers: dict[str, str],
                 qKeyWord: str,):
        self.qID = qID
        self.qCategory = qCategory
        self.qQuestion = qQuestion
        self.qCorrect = qCorrect
        self.qAnswers = qAnswers
        self.qKeyWord = qKeyWord

    def get_answers(self):
        out = "\n"
        for k, v in self.qAnswers.items():
            out += f"  | {k}: {textwrap.fill(v).replace('\n', '\n  |    ')}\n"

        return out


def build_questions(bank_path: str) -> dict[str, Question]:
    """
    Parse the question bank as specified by the bank path

    params
    ------
    - bank_path (str) a path to the question bank

    returns a question bank, keys being the question ID and values being details
    about the question
    """
    allQuestions = {}
    rawCategories = []
    with open(bank_path, "r") as f:
        # categorize each question
        rawCategories = f.read().split("} ")[1:]

    for rawQuestions in rawCategories:
        category = rawQuestions.split('\n')[0]
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
                                                    category,
                                                    ma.group('QUESTION'),
                                                    ma.group('ANSWER'),
                                                    {"A": ma.group('QA'),
                                                     "B": ma.group('QB'),
                                                     "C": ma.group('QC'),
                                                     "D": ma.group('QD')},
                                                    ma.group('KEYWORD'))
        re.purge()

        Categories.append(category)

    return allQuestions


def display_question(question,):
    print(f"""Q: {question.qID} - {textwrap.fill(question.qQuestion, 70)}
{question.get_answers()}""")
    print('\n'+'-'*30)
    print(f'so far you have gotten {len(AnsweredRight)} right and {len(AnsweredWrong)} wrong.')

    getAnswer = input("Please enter your answer: ")
    print('\n'+'-'*30)
    if str(getAnswer).lower() == str(question.qCorrect).lower():
        print('Correct!\n')
        AnsweredRight.add(question.qID)
    else:
        print(f"""WRONG! The answer was {question.qCorrect}

Here is why you are wrong:
{textwrap.fill(question.qKeyWord, 80)}""")
        AnsweredWrong.add(question.qID)
        input('Press enter to continue...')


def create_parser():
    parser = argparse.ArgumentParser(description="""
                                                 A quick tool to parse the
                                                 question bank in place of
                                                 ExHAMiner
                                                 """)
    parser.add_argument("bank_path",
                        type=str,
                        help="""<./path/to/question/bank.txt>, where the
                        question bank can be downloaded at
                        https://www.rac.ca/exhaminer-v2-5/""",
                        )

    parser.add_argument("--no-tui", "-nt",
                        action="store_false",
                        help="""Disable screen clearing""",
                        )

    parser.add_argument("--random", "-r",
                        action="store_true",
                        help="""Simply select random questions instead of
                        generating a test with a number of questions. This will
                        have replacements for each chosen question""",
                        )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    q_bank = build_questions(args.bank_path)
    try:
        if(args.random):
            while True:
                if(args.no_tui): print("\033[100A\033[J", end="")
                # randomly choose from the entire set of questions
                question = q_bank[random.choice(list(q_bank.keys()))]
                display_question(question)
        else:
            # generate a randomly-ordered, 100-question test
            qTest = list(q_bank.keys())
            random.shuffle(qTest)
            for index, qId in enumerate(qTest[:100]):
                if(args.no_tui): print("\033[100A\033[J", end="")
                print('[' + '=' * (index // 2) + '-' * ((100-index) // 2) + f" ({index+1}/100)" + ']')
                display_question(q_bank[qId])
    except(KeyboardInterrupt, EOFError) as e:
        pass
    except Exception as e:
        print("broke with exception:")
        traceback.print_exception(e)
        exit(0)
    print('\n'+'-_'*30)
    print('so far you have gotten %i right and %i wrong.' % (len(AnsweredRight),len(AnsweredWrong)))
    print('-_'*30)
    if len(AnsweredWrong) > 0:
        print('\nYou answered the following questions Wrong.')
        for wrongAnswers in AnsweredWrong:
            print(wrongAnswers)


if __name__ == '__main__':
    main()
