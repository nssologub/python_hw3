#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re
from os import listdir

PUNCTUATION = {'.', ',', '!', '?'}


class MarkovChain(object):
    depth = 2

    def __init__(self, depth, initial_distribution, probability_matrix):
        self.depth = depth
        self.initial_distribution = initial_distribution
        self.probability_matrix = probability_matrix

    def generate_initial(self, history):
        for i in range(0, self.depth):
            probs = self.initial_distribution[i]
            for j in range(0, i):
                probs = probs[history[j]]
            history.append(self.generate_next(probs))

    def generate_next_instance(self, history):
        probs = self.probability_matrix
        for i in range(len(history) - self.depth, len(history)):
            probs = probs[history[i]]
        history.append(self.generate_next(probs))

    def generate_chain(self, count_instances, chain):
        self.generate_initial(chain)
        for i in range(self.depth, count_instances):
            self.generate_next_instance(chain)
        result = ' '.join(chain)
        for p in PUNCTUATION:
            result = result.replace(' ' + p + ' ', p + ' ')
        return result

    @staticmethod
    def generate_next(probabilities):
        r = random.random()
        prob_floor = 0.0
        for key in probabilities:
            if prob_floor <= r <= prob_floor + probabilities[key]:
                return key
            prob_floor += probabilities[key]


class CountStatistics(object):
    text = ''

    def read_text(self, filename):
        re_not_letters = re.compile(r'[A-Z]{2,}|[^A-Za-z!\.,\?\']+')
        self.text = open(filename).read().decode('utf8')
        self.text = self.text.replace('’'.decode('utf8'), '\'')
        for p in PUNCTUATION:
            self.text = self.text.replace(p, ' ' + p + ' ')
        self.text = (re_not_letters.split(self.text))

    def count_stats(self, depth, initial_stats, stats):
        words = self.text
        for i in range(depth, len(words)):
            self.add_sequence_to_stats(words[i - depth: i + 1], stats)
            if words[i - depth] in {'.', '?', '!'}:
                for j in range(0, depth):
                    self.add_sequence_to_stats(words[i - depth + 1:i - depth + j + 2], initial_stats[j])
        return initial_stats, stats

    def normalize_all_stat(self, depth, initial_stats, stats):
        self.normalize_stats(stats, 0, depth)
        for j in range(0, depth):
            self.normalize_stats(initial_stats[j], 0, j)

    @staticmethod
    def add_sequence_to_stats(sequence, probs):
        depth = len(sequence)
        for j in range(0, depth - 1):
            if not sequence[j] in probs:
                probs[sequence[j]] = {}
            probs = probs[sequence[j]]
        if sequence[-1] in probs:
            probs[sequence[-1]] += 1
        else:
            probs[sequence[-1]] = 1

    def normalize_stats(self, probs, curr_depth, depth):
        if curr_depth < depth:
            for word in probs:
                self.normalize_stats(probs[word], curr_depth + 1, depth)
        else:
            sum = 0
            for word in probs:
                sum += probs[word]
            for word in probs:
                probs[word] = float(probs[word]) / sum


def print_stats(probs, initial_distr):
    output = open('statistics.txt', 'w')
    for first in probs:
        for second in probs[first]:
            for thrird in probs[first][second]:
                output.write(first + ' ' + second + ' ' + thrird + ' ' + str(probs[first][second][thrird]) + '\n')
    output.flush()
    output = open('initial_distribution.txt', 'w')
    for first in initial_distr[0]:
        output.write(first + ' ' + str(initial_distr[0][first]) + '\n')
    for first in initial_distr[1]:
        for second in initial_distr[1][first]:
            output.write(first + ' ' + second + ' ' + str(initial_distr[1][first][second]) + '\n')


def read_data_and_count_stats(depth, initial_stat, stat, cs):
    for j in range(0, depth):
        initial_stat.append({})
    for folderpath in listdir('corpus'):
        for filepath in listdir('corpus/' + folderpath):
            cs.read_text('corpus/' + folderpath + '/' + filepath)
            cs.count_stats(depth, initial_stat, stat)
            print filepath


depth = 2
initial_stat = []
stat = {}
cs = CountStatistics()
read_data_and_count_stats(depth, initial_stat, stat, cs)
cs.normalize_all_stat(depth, initial_stat, stat)
print_stats(stat, initial_stat)

mc = MarkovChain(depth, initial_stat, stat)
chain = []
result = mc.generate_chain(10000    , chain)
open('text.txt', 'w').write(result)

