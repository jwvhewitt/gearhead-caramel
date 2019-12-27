"""
Copyright 2010 Joao Henriques <jotaf (no spam) at hotmail dot com>.

Modified by Joseph Hewitt for Dungeon Monkey Eternal.

This file is part of name-gen.

name-gen is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

name-gen is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with name-gen.  If not, see
<http://www.gnu.org/licenses/>.
"""

import itertools
import random
import locale
from . import util

class NameGen:
	"""
	name-gen: Free python name generator module that analyzes sample text and produces
	similar words.
	
	Usage:
		1. Initialize with path to language file (generated using 'namegen_training.py').
		2. Call gen_word() method, returns generated string.
	
	Optional:
		. Change min_syl and max_syl to control number of syllables.
		. Pass the sample file as 2nd parameter at initialization to set it as the list
		  of forbidden words. No words from the sample will be replicated.
		. Pass True as the 1st parameter to name_gen() to add the generated word to the
		  list of forbidden words. The word will not occur again.
	"""
	
	def __init__(self, language_file, forbidden_file = None, min_syl=2, max_syl=4):
		self.min_syl = min_syl
		self.max_syl = max_syl
		
		#load language file
		with open(util.data_dir(language_file), 'r') as f:
			lines = [line.strip() for line in f.readlines()]
			
			self.syllables = lines[0].split(',')  #first line, list of syllables
			
			starts_ids = [int(n) for n in lines[1].split(',')]  #next 2 lines, start syllable indexes and counts
			starts_counts = [int(n) for n in lines[2].split(',')]
			self.starts = list(zip(starts_ids, starts_counts))  #zip into a list of tuples
			
			ends_ids = [int(n) for n in lines[3].split(',')]  #next 2, same for syllable ends
			ends_counts = [int(n) for n in lines[4].split(',')]
			self.ends = list(zip(ends_ids, ends_counts))
			
			#starting with the 6th and 7th lines, each pair of lines holds ids and counts
			#of the "next syllables" for a previous syllable.
			self.combinations = []
			for (ids_str, counts_str) in zip(lines[5:None:2], lines[6:None:2]):
				if len(ids_str) == 0 or len(counts_str) == 0:  #empty lines
					self.combinations.append([])
				else:
					line_ids = [int(n) for n in ids_str.split(',')]
					line_counts = [int(n) for n in counts_str.split(',')]
					self.combinations.append(list(zip(line_ids, line_counts)))
		
		#load forbidden words file if needed
		if forbidden_file is None:
			self.forbidden = ''
		else:
			self.forbidden = _load_sample(forbidden_file)
	
	def gen_word(self, no_repeat = True):
		#random number of syllables, the last one is always appended
		num_syl = random.randint(self.min_syl, self.max_syl - 1)
		
		#turn ends list of tuples into a dictionary
		ends_dict = dict(self.ends)
		
		#we may have to repeat the process if the first "min_syl" syllables were a bad choice
		#and have no possible continuations; or if the word is in the forbidden list.
		word = []; word_str = ''
		while len(word) < self.min_syl or self.forbidden.find(word_str) != -1:
			#start word with the first syllable
			syl = _select_syllable(self.starts, 0)
			word = [self.syllables[syl]]
			
			for i in range(1, num_syl):
				#don't end yet if we don't have the minimum number of syllables
				if i < self.min_syl: end = 0
				else: end = ends_dict.get(syl, 0)  #probability of ending for this syllable
				
				#select next syllable
				syl = _select_syllable(self.combinations[syl], end)
				if syl is None: break  #early end for this word, end syllable was chosen
				
				word.append(self.syllables[syl])
				
			else:  #forcefully add an ending syllable if the loop ended without one
				syl = _select_syllable(self.ends, 0)
				word.append(self.syllables[syl])
			
			word_str = ''.join(word)
		
		#to ensure the word doesn't repeat, add it to the forbidden words
		if no_repeat: self.forbidden = self.forbidden + '\n' + word_str
		
		return word_str.capitalize()

def _select_syllable(counts, end_count):
	if len(counts) == 0: return None  #no elements to choose from
	
	#"counts" holds cumulative counts, so take the last element in the list
	#(and 2nd in that tuple) to get the sum of all counts
	chosen = random.randint(0, counts[-1][1] + end_count)
	
	for (syl, count) in counts:
		if count >= chosen:
			return syl
	return None

def _load_sample(filename):
	#get sample text
	with open(util.data_dir(filename), 'r') as f:
		sample = ''.join(f.readlines()).lower()
	
	#convert accented characters to non-accented characters
	sample = locale.strxfrm(sample)
	
	#remove all characters except letters from A to Z
	a = ord('a')
	z = ord('z')
	sample = ''.join([
		c if (ord(c) >= a and ord(c) <= z) else ' '
			for c in sample])
	
	return sample

def test_names( ng, trials ):
    tot1 = 0
    s1 = set()

    mx1 = 0
    mn1 = 99

    for t in range( trials ):
        n1 = ng.gen_word()
        tot1 += len( n1 )
        mx1 = max( len( n1 ) , mx1 )
        mn1 = min( len( n1 ) , mn1 )
        s1.add( n1 )

    print("  average length: " + str( float( tot1 )/trials ))
    print("  unique names: " + str( len( s1 ) ))
    print("  max/min: " + str( mx1 ) + "/" + str( mn1 ))

#ALL_NAME_GENERATORS = ( DEFAULT, DWARF, DRAGON, ELF, ORC, GREEK, JAPANESE, GNOME, HURTHLING, ELDRITCH )
#
#def random_style_name():
#    ng = random.choice( ALL_NAME_GENERATORS )
#    return ng.gen_word()


