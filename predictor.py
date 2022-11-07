import numpy as np
import pandas as pd
from wordfreq import zipf_frequency
from enum import Enum

class Colors(Enum):
    GREEN = 2
    YELLOW = 1
    BLACK = 0

#bit space
class Predictor(object):
    '''
    Class that...
    '''
    def __init__(self):
        
        #numpy array of valid words
        self.all_words = np.loadtxt("valid-wordle-words.txt", dtype = str)
        self.valid = self.all_words.copy() #remaining
        self.invalid_letters = []
        self.valid_letters = []

        #store the guess input and output
        self.guesses = []
        self.rules = []
        self.unknown = [True] * 5
    
    #outputs frequency of all remaining valid words
    def get_frequencies(self):
        list = []
        for i in self.valid:
            list.append(zipf_frequency(i, 'en'))
        return list
    
    #given a new rule, updates list of valid words
    def update_valid(self):
        index = len(self.rules) - 1
        valid_bool = []
        for word in self.valid:
            valid_bool.append(self.check_word(word, index))
        self.valid = self.valid[valid_bool]
    
    #calculate if single word satisfies rule
    def check_word(self, word, index):
        val = True
        for i in range(5):
            if self.unknown[i]:

                if self.rules[index][i] == Colors.GREEN:
                    # self.unknown[i] = False #no longer query for this index
                    if self.guesses[index][i] != word[i]:
                        return False #guess letter in right position

                elif self.rules[index][i] == Colors.BLACK:
                    # self.invalid_letters.append(self.guesses[index][i])
                    if self.guesses[index][i] in word:
                        return False #guess letter not in word

                else: #yellow
                    # self.valid_letters.append(self.guesses[index][i])
                    if self.guesses[index][i] == word[i] or self.guesses[index][i] not in word:
                        return False #guess letter not in this position and in the word

        return val

    #add guess and update valid words
    def add_guess(self, guess, rule):
        self.guesses.append(guess)
        self.rules.append(rule)
        #self.update_valid()

    #returns the "rule" after a guess
    def calculate_rule(self, word, guess):
        rule = []

        for i in range(5):
            if guess[i] == word[i]: #letter matches -> green
                rule.append(Colors.GREEN)
            elif guess[i] in word: #letter contained -> yellow
                rule.append(Colors.YELLOW)
            else: #nothing
                rule.append(Colors.BLACK)
        
        return rule
    
    def simulate(self, guess, rule_list):
        self.guesses.append(guess)
        rule = []
        for i in rule_list:
            rule.append(Colors(i))
        self.rules.append(rule)
