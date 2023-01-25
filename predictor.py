import numpy as np
import pandas as pd
from wordfreq import zipf_frequency
from enum import Enum

"""
Class for defining type of hint.
"""
class Hint(Enum):
    GREEN = 1
    YELLOW = 2
    BLACK = 3

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

"""
Class that assists in getting the wordle.
"""
class Predictor(object):

    def __init__(self, preload_rv = True): 
        
        #list of all 5-letter words
        self.available = np.loadtxt("input/valid-wordle-words.txt", dtype = str) #fixed
        self.valid = self.available.copy() #list which gets updated

    #how many occurences of letter are there in a word
    def single_letter_count(self, word, letter):
        count = 0
        for i in word:
            if i == letter:
                count += 1
        return count
    
    #convert string of five letters (g, y, or b) into a rule for ease of input
    def parse_rule(self, raw_rule):
        rule = []
        for i in raw_rule:
            if i == "g":
                rule.append(Hint.GREEN)
            elif i == "y":
                rule.append(Hint.YELLOW)
            elif i == "b":
                rule.append(Hint.BLACK)
            else:
                raise Exception("Invalid input.")
        return rule

    #returns the rule of a guess given the solution
    def calculate_rule(self, guess, solution):
        rule = [None] * 5
        counts_true = [self.single_letter_count(solution, i) for i in ALPHABET]
        counts_seen = [0] * 26

        for i in range(5): #loop through greens
            if guess[i] == solution[i]:
                rule[i] = Hint.GREEN
                counts_seen[ord(guess[i]) - 97] += 1
        
        for i in range(5): #loop through rest
            if rule[i] is None:
                index = ord(guess[i]) - 97
                if guess[i] in solution and counts_true[index] > counts_seen[index]:
                    rule[i] = Hint.YELLOW
                    counts_seen[index] += 1
                else: #nothing
                    rule[i] = Hint.BLACK
        
        return rule
    
    #shortens self.valid by comparing each hypothetical rule with actual rule
    #assumes that if we know the solution then we know the rule
    def update_valid(self, guess, rule):
        valid_bool = []
        for test_word in self.valid:
            test_rule = self.calculate_rule(guess, test_word)
            valid_bool.append(test_rule == rule)
        self.valid = self.valid[valid_bool]

    #outputs frequency of all remaining valid words
    def get_frequencies(self):
        list = []
        for i in self.valid:
            list.append(zipf_frequency(i, 'en'))
        return pd.DataFrame({"word": self.valid, "frequency": list}).sort_values("frequency", ascending=False)
    
    #randomly picks n values in self.valid and omits the rest
    def reduce_size(self, n):
        bool = np.array([True] * n + [False] * (len(self.valid) - n))
        np.random.shuffle(bool)
        return self.valid[bool]
    
    #organizes 3^5 possible rules with a fixed number (0-242), 1-1 mappings
    def index_from_rule(self, rule):
        index = 0
        for i in range(5):
            index += pow(3, i) * (rule[i].value - 1)
        return index

    #generates rule from index above
    def rule_from_index(self, index):
        rule = []
        for i in range(5):
            remainder = index % 3
            index //= 3
            rule.append(Hint(remainder + 1))
        return rule
    
    #used to find mean size of non-zero bins in an array
    def mean_size(self, bins):
        sum = 0
        count = 0
        for i in bins:
            if i > 0:
                sum += i
                count += 1
        return sum / count

    #find the expected size of self.valid after making each guess
    def expected_valid_size(self, valid = True, word_freq = False):
        means = []
        valids = []

        column_name = "E[ w( |v| ) ]" if word_freq else "E( |v| )"
        if valid:
            guesses = self.valid
        else:
            guesses = [i for i in self.available if i not in self.valid]

        for potential_guess in guesses:

            rule_set = [0] * 243

            for potential_solution in self.valid:
                rule = self.calculate_rule(potential_guess, potential_solution)
                index = self.index_from_rule(rule)

                if word_freq:
                    rule_set[index] += zipf_frequency(potential_solution, 'en')
                else:
                    rule_set[index] += 1

            means.append(self.mean_size(rule_set))
            valids.append(potential_guess in self.valid)
        
        return pd.DataFrame({"word": guesses, column_name: means}).sort_values(column_name, ascending=True)
