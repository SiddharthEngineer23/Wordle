import numpy as np
import pandas as pd
from wordfreq import zipf_frequency
from enum import Enum

class Hint(Enum):
    GREEN = 1
    YELLOW = -1
    BLACK = 0

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

#bit space
class Predictor(object):
    '''
    Class that assists in getting the wordle.
    '''
    def __init__(self): 
        self.valid = np.loadtxt("valid-wordle-words.txt", dtype = str) #valid words
        self.guesses = [] #for storing data
        self.rules = []
        
        #for using letter_counts
        self.letter_counts = [None] * 26
    
    def get_knowledge(self, guess, rule):
        knowledge = [] #array of letters in guess
        for i in range(26):
            if ALPHABET[i] in guess:
                fact = [i]
                for j in range(5):
                    if guess[j] == ALPHABET[i]:
                        fact.append(rule[j])
                knowledge.append(knowledge)
        return knowledge

    """
    * Note that there are no 5 letter words with 4 of the same letter *

    Key:
        None = no info on letter
        0 = letter is not in word
        1:3 = letter is exactly 1-3 times in word
        -1 = letter appears 1+ time in word
        -2 = letter appears 2+ times in word
    """ 
    def find_letter_counts(self, guess, rule):
        knowledge = self.get_knowledge(guess, rule)
        changes = [i[0] for i in knowledge]
        #return changes, to-do
    
    #to-do
    #given word and knowledge of letter counts, checks if test_word satisfies
    def check_letter_counts(self, test_word):
        return None
    
    #check if test_word satisfies our rule at the letter-index level
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
        guess = self.guesses[len(self.guess) - 1]
        rule = self.rules[len(self.rules) - 1]
        changes = self.find_letter_counts(guess, rule)

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

    #add guess, calculate rule, and updates self.valid; solution is known
    def test_guess(self, guess, solution):
        self.guesses.append(guess)
        self.rules.append(self.calculate_rule(guess, solution))
        self.update_valid()

    #returns the rule of a guess given the solution
    def calculate_rule(self, guess, solution):
        rule = []

        for i in range(5):
            if guess[i] == solution[i]: #letter matches -> green
                rule.append(Hint.GREEN)
            elif guess[i] in solution: #letter contained -> yellow
                rule.append(Hint.YELLOW)
            else: #nothing
                rule.append(Hint.BLACK)
        
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

    """
    Everything below omit
    """

    #given there is a new guess/rule, update self.solution_space
    def _update_solution_space(self):
        guess = self.guesses[len(self.guess) - 1]
        rule = self.rules[len(self.rules) - 1]
        yellow_tally = [0] * 26 #0 means no info, -1 means not in word
        #-> can't figure out how to configure

        for i in range(5): #iterate through letters
            if rule[i] == Hint.GREEN:
                self.solution_space[i] = {guess[i]}

            elif rule[i] == Hint.YELLOW:
                yellow_tally[ord(guess[i])-97] += 1
                if guess[i] in self.solution_space[i]:
                    self.solution_space[i].remove(guess[i])
        
        for i in range(5):
            if rule[i] == Hint.BLACK :
                self.solution_space[i].remove(guess[i])
                if self.letters_counts[ord(guess[i])-97] == 0:
                    self.letters_counts[ord(guess[i])-97] = -1
                    #also remove from all others
    
    #probably not needed
    def single_letter_count(self, word, letter):
        count = 0
        for i in word:
            if i == letter:
                count += 1
        return count