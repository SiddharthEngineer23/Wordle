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

    def __init__(self): 
        self.valid = np.loadtxt("valid-wordle-words.txt", dtype = str) #valid words
        self.guesses = [] #for storing data
        self.rules = []
        self.letter_counts = [None] * 26

    """
    Count of greens, yellows, and blacks for each letter in the most recent guess/rule
    
    Facts are indexed: [letter, green count, yellow count, black count]
    """
    def get_knowledge(self):
        knowledge = [] #array of facts
        for letter in set(self.guesses[len(self.guesses) - 1]): #each unique letter in guess
                fact = [letter, 0, 0, 0]

                for j in range(5): #looping through guess/rule
                    if self.guesses[len(self.guesses) - 1][j] == letter:
                        rule = self.rules[len(self.rules) - 1][j]
                        fact[rule.value] += 1
                        
                knowledge.append(fact)
        return knowledge
    
    """
    Note that there are no 5 letter words with 4 of the same letter

    Key:
        None = no info on letter
        0 = letter is not in word
        1:3 = letter is exactly 1-3 times in word
        -1 = letter appears 1+ time in word
        -2 = letter appears 2+ times in word

    Returns this number based on "fact"
    """
    def analyze_fact(self, fact):
        if fact[1] == 0 and fact[2] == 0: #letter is only black
            return 0
        elif fact[3] > 0: #given there's a black and other colors
            return fact[1] + fact[2]
        elif (fact[1] + fact[2]) == 3: #max 3 of same letter
            return 3
        else:
            return -(fact[1] + fact[2])
            
    """
    Updates self.letter_counts to the most specific information known about each
        letter's count in the word
    """ 
    def find_letter_counts(self):
        knowledge = self.get_knowledge()

        for fact in knowledge:
            index = ord(fact[0]) - 97
            if self.letter_counts[index] is None or self.letter_counts[index] < 0:
                
                val = self.analyze_fact(fact)
                if self.letter_counts[index] is None or val < self.letter_counts[index]:
                    self.letter_counts[index] = val
        #return changes, to-do
    
    #how many occurences of letter are there in word
    def single_letter_count(self, word, letter):
        count = 0
        for i in word:
            if i == letter:
                count += 1
        return count
    
    #given knowledge of letter counts, checks if test_word satisfies
    def check_letter_counts(self, test_word):
        for letter in set(test_word):
            count = self.single_letter_count(test_word, letter)
            true_count = self.letter_counts[ord(letter) - 97]

            if true_count is not None:
                if true_count == 0: #letter not in solution
                    return False
                elif true_count > 0: #exact count known
                    if count != true_count:
                        return False
                else: #minimum count known
                    if true_count < -count:
                        return False
        return True

    #checks if test_word satisfies our rule at the letter-index level
    def check_letter_indices(self, test_word, guess, rule):
        for i in range(5): #disprove if any letter contradicts
                if rule[i] == Hint.GREEN:
                    if guess[i] != test_word[i]:
                        return False #assert letter in right position
                else:
                    if guess[i] == test_word[i]:
                        return False #assert letter not in this position
        return True

    #given there is new guess/rule, updates list of valid words
    def update_valid(self):
        guess = self.guesses[len(self.guesses) - 1]
        rule = self.rules[len(self.rules) - 1]
        self.find_letter_counts()
        # changes = ...

        #loop through and update self.valid
        valid_bool = []
        for test_word in self.valid:
            satisfies_counts = self.check_letter_counts(test_word)
            satisfies_indices = self.check_letter_indices(test_word, guess, rule)
            valid_bool.append(satisfies_counts and satisfies_indices)
        self.valid = self.valid[valid_bool]

    #add guess and rule, update self.valid; solution is unknown
    def make_guess(self, guess, rule):
        self.guesses.append(guess)
        self.rules.append(rule)
        self.update_valid()
    
    #add guess, calculate rule, and update self.valid; solution is known
    def test_guess(self, guess, solution):
        self.guesses.append(guess)
        self.rules.append(self.calculate_rule(guess, solution))
        self.update_valid()
    
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
    
    def run_game_interface(self):
        print("Welcome to Wordle Solving A.I. Interface.")

        for i in range(6):
            print("Please enter guess:")
            guess = input()
            print("Please input the given rule. Type it in as a 5 letter word (g, y, or b):")
            raw_rule = input()
            rule = self.parse_rule(raw_rule)
            self.make_guess(guess, rule)
            print(pd.DataFrame({"word": self.valid, "frequency": self.get_frequencies()}).sort_values("frequency", ascending=False))

    #returns the rule of a guess given the solution
    def calculate_rule(self, guess, solution):
        rule = [None] * 5
        counts = [self.single_letter_count(solution, i) for i in ALPHABET]
        counts_seen = [0] * 26

        for i in range(5): #loop through greens
            if guess[i] == solution[i]:
                rule[i] = Hint.GREEN
                counts_seen[ord(guess[i]) - 97] += 1
        
        for i in range(5): #loop through rest
            if rule[i] is None:
                index = ord(guess[i]) - 97
                if guess[i] in solution and counts[index] > counts_seen[index]:
                    rule[i] = Hint.YELLOW
                else: #nothing
                    rule[i] = Hint.BLACK
        
        return rule

    #outputs frequency of all remaining valid words
    def get_frequencies(self):
        list = []
        for i in self.valid:
            list.append(zipf_frequency(i, 'en'))
        return list

    #return frequency chart (of chars) based on self.valid
    def _compute_frequency_chart(self):
        return None #to-do