"""
Jeremie Simon
N16247912
from POSTagger import *
t = HMMTagger()
t.doTag('test1.txt')

TODO: 
punctuation issue
"""

import copy
import string

class HMMTagger(object): 
	"""
	"""
	
	def __init__ (self): 
		
		#parse file: 
		f = open("Homework4_corpus/POSData/development.pos").read().split('\n')
		f = [line.split('\t') for line in f]
		
		self.numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, '-']
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',\
		 'November', 'December']
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		
		self.tags = set(['', 'PRP$', 'VBG', 'VBD', '``', 'VBN', "''", 'VBP', 'WDT', 'HYPH', 'JJ', 'WP', 'VBZ', 'DT', 'RP', \
		'NN', ')', '(', 'POS', '.', 'TO', 'COMMA', 'PRP', 'RB', ':', 'NNS', 'NNP', 'VB', 'WRB', 'CC', 'PDT', 'RBS', 'RBR', \
		'CD', 'EX', 'IN', 'WP$', 'MD', 'NNPS', 'JJS', 'JJR', 'UH', '$', 'sigma', 'start'])
		pos = {}
		for tag in self.tags: pos[tag] = 0.0

		#1.0 init observationTable
		self.observationTable = {}
		self.observationTable['__endswithing__'] = {'sigma':0.0}
		self.observationTable['__endswithed__'] = {'sigma':0.0}
		self.observationTable['__endswithic__'] = {'sigma':0.0}
		self.observationTable['__endswithian__'] = {'sigma':0.0}
		self.observationTable['__endswithians__'] = {'sigma':0.0}
		
		def helper(ender): 
			if not self.observationTable['__endswith'+ender+'__'].has_key(line[1].split('\r')[0]): 
				self.observationTable['__endswith'+ender+'__'][line[1].split('\r')[0]]=1.0
			else: 
				self.observationTable['__endswith'+ender+'__'][line[1].split('\r')[0]]+=1.0
			self.observationTable['__endswith'+ender+'__']['sigma']+=1
		
		isEndOfSentence = [False,False]
		
		#1.1 build the observation table from the data
		for i, line in enumerate(f): 
			if len(line) > 1: 
				if line[0] == "" or i == 0: isEndOfSentence[i%2] = True 
				else: isEndOfSentence[i%2] = False
		
				if not self.observationTable.has_key(line[0].lower()): #word is not known		
					#1. check if word is a number
					if True in (True for num in self.numbers if line[0].startswith(str(num))): 
						try: 
							number = int(line[0]) #if the word can be converted to a number
							if not self.observationTable.has_key('__numeric__'): #if no number was observed
								self.observationTable['__numeric__'] = {'sigma': 0.0}
								self.observationTable['__numeric__'][line[1].split('\r')[0]] = 1
								self.observationTable['__numeric__']['sigma']+=1
							else: #if some numbers were already observed
								if not self.observationTable['__numeric__'].has_key(line[1].split('\r')[0]): 
									self.observationTable['__numeric__'][line[1].split('\r')[0]]=1.0
								else: 
									self.observationTable['__numeric__'][line[1].split('\r')[0]]+=1.0
								self.observationTable['__numeric__']['sigma']+=1
															
						except ValueError:
							self.observationTable[line[0].lower()] = {'sigma': 0.0}
							self.observationTable[line[0].lower()][line[1].split('\r')[0]] = 1
							self.observationTable[line[0].lower()]['sigma']+=1
						#End of number checking
				
					#2. check if it is a proper noun: 
					elif not True in isEndOfSentence and line[0][0] in string.uppercase and line[1].split('\r')[0] == "NNP":
						print 'proper noun', line[0]
						self.observationTable['__propernoun__'] = {'sigma':1.0}
						self.observationTable['__propernoun__']['NNP'] = 1
					
					#3. neither proper noun or numbers. regular case
					else:						
						self.observationTable[line[0].lower()] = {'sigma': 0.0}
						self.observationTable[line[0].lower()][line[1].split('\r')[0]] = 1
						self.observationTable[line[0].lower()]['sigma']+=1
				#word is known
				else: 
					if line[0].lower().endswith('ed'): helper('ed')
					if line[0].lower().endswith('ing'): helper('ing')
					if line[0].lower().endswith('ic'): helper('ic')
					if line[0].lower().endswith('ian'): helper('ian')
					if line[0].lower().endswith('ians'): helper('ians')
					
						
					if not self.observationTable[line[0].lower()].has_key(line[1].split('\r')[0]): 
						self.observationTable[line[0].lower()][line[1].split('\r')[0]]=1.0
					else: 
						self.observationTable[line[0].lower()][line[1].split('\r')[0]]+=1.0
					self.observationTable[line[0].lower()]['sigma']+=1
		

		
		#1.2 Add special cases (Month + Days) to observation list:
		for day in days: 
			if not self.observationTable.has_key(day.lower()): 
				self.observationTable[day.lower()] = {'sigma':1.0}
				self.observationTable[day.lower()]['NNP'] = 1.0
		for month in months: 
			if not self.observationTable.has_key(month.lower()): 
				self.observationTable[month.lower()] = {'sigma':1.0}
				self.observationTable[month.lower()]['NNP'] = 1.0
		
		#1.3 compute the probabilities in the in the observation table: 
		for words in self.observationTable.itervalues(): 
			for tags in words.iterkeys():
				if tags != 'sigma':  
					words[tags] = words[tags] / words['sigma']
			del(words['sigma']) #sigma is no longer needed
		
		#2.0 Create transition table
		self.transitionTable = {}

		#2.1 init transitionTable
		for tag in pos: 
			if tag != 'sigma' and tag != 'start': 
				self.transitionTable[tag] = copy.deepcopy(pos)

		#2.2 build transitionTable
		for i, line in enumerate(f): 
			if len(line)> 1:
				if i == 0: #start case: 
					self.transitionTable[line[1].split('\r')[0]]['start'] +=1
					self.transitionTable[line[1].split('\r')[0]]['sigma'] +=1
				else: 
					tag = f[i-1][1].split('\r')[0]
					#tag is empty: 
					if tag == "": 
						self.transitionTable[line[1].split('\r')[0]]['start']+=1
					else: 
						self.transitionTable[line[1].split('\r')[0]][tag]+=1
					self.transitionTable[line[1].split('\r')[0]]['sigma'] +=1

		#2.3 transform to probabilities
		for tags in self.transitionTable.itervalues(): 
			for key in tags.iterkeys(): 
				if key != 'sigma':
					try: 
						tags[key] = tags[key] / tags['sigma']
					except ZeroDivisionError: pass	
			del(tags['sigma']) #sigma is no longer needed
		
		#3. search word with lowest NNS and VBZ: 
		self.observationTable['__propernouns__'] = {'NNPS': 1.0}
		self.observationTable['__ionnoun__'] = {'NN':1.0}
		self.observationTable['__itynoun__'] = {'NN':1.0}		
		self.observationTable['__ionnouns__'] = {'NNS':1.0}
		self.observationTable['__iesnouns__'] = {'NNS':1.0}		
	
		self.wordEndsWithS = ""
		mini = 10
		for key in self.observationTable.iterkeys(): 
			if self.observationTable[key].has_key('NNS') and self.observationTable[key].has_key('VBZ'): 
				if  (self.observationTable[key]['NNS'] + self.observationTable[key]['VBZ']) <= mini: 
					mini = self.observationTable[key]['NNS'] + self.observationTable[key]['VBZ'] 
					self.wordEndsWithS = key
		
		self.wordUnknown = ""
		mini = 10
		for key in self.observationTable.iterkeys(): 
			if self.observationTable[key].has_key('NN') and self.observationTable[key].has_key('JJ'): 
				if  self.observationTable[key]['NN'] + self.observationTable[key]['JJ'] <= mini: 
					mini = self.observationTable[key]['NN'] + self.observationTable[key]['JJ'] 
					self.wordUnknown = key
		
		self.fakeAdverb = "__fakeadverb__"
		self.observationTable[self.fakeAdverb] = copy.deepcopy(self.observationTable[self.wordUnknown])
		for key in self.observationTable[self.fakeAdverb].iterkeys(): 
			if key != 'RB': self.observationTable[self.fakeAdverb][key] /= 10
		self.observationTable[self.fakeAdverb]['RB'] = 0.90

	def tag(self, sentence):
		"""
		tag given a sentence
		"""
		#sentence = sentence.split('\n')
		posTags = ["" for i in range(len(sentence))]
		isEndOfSentence = [False, False]
		prevWord = ""
		
		for i, word in enumerate(sentence): 
			pMax, tagMax = 0.0, ""
			if word == "" or i == 0: isEndOfSentence[i%2] = True 
			else: isEndOfSentence[i%2] = False
			
			print isEndOfSentence
			
			#EXCEPTION CASES
			#1. identify if it is a number: 
			if True in (True for num in self.numbers if word.startswith(str(num))): 
				try: 
					number = int(word)
					word = '__numeric__'
				except ValueError: pass
		
			#2. word is a proper noun
			if not self.observationTable.has_key(word.lower()) and not True in isEndOfSentence\
			and word[0] in string.uppercase: 
				if word.endswith('s'): word = '__propernouns__'
				else: word = '__propernoun__'
			
			#3. word is not known 
			if not self.observationTable.has_key(word.lower()): 
				if word.lower().endswith('ions') or word.lower().endswith('ies'): word = '__ionnouns__'
				elif word.lower().endswith('ing'): word = '__endswithing__'
				elif word.lower().endswith('ed'): word = '__endswithed__'
				elif word.lower().endswith('ic'): word = '__endswithic__'
				elif word.lower().endswith('ian'): word = '__endswithian__'
				#elif word.lower().endswith('ians'): word = '__endswithians__'		
				elif word.lower().endswith('ity') or word.lower().endswith('ent') or \
				word.lower().endswith('ion') : word = '__itynoun__'				
				elif word.lower().endswith('s'):  word = self.wordEndsWithS 
				elif word.endswith('ly'): word = self.fakeAdverb
				else: word = self.wordUnknown					
			#END OF EXCEPTION CASES
			
			if i == 0 or prevWord == "": #start case
				for key in self.observationTable[word.lower()].iterkeys(): 
					p = self.observationTable[word.lower()][key] * self.transitionTable[key]['start']
					if p > pMax: 
						pMax, tagMax= p, key
	
			else: 
				for wordTag in self.observationTable[word.lower()].iterkeys(): 
					p = self.observationTable[word.lower()][wordTag] * self.transitionTable[wordTag][posTags[i-1]]					
					if self.observationTable[word.lower()][wordTag] == 1.0: 
						p , tagMax= 1, wordTag
					if p > pMax: 
						pMax, tagMax= p, wordTag
						
			posTags[i]=tagMax
			prevWord = word
		
		result = []
		for i in range(len(posTags)): 
			result.append((sentence[i], posTags[i]))
		return result
				
	
	def doTag(self, textfile):
		"""
		"""
		textfile = open(textfile).read().split('\n')
		result = self.tag(textfile)
		for r in result: 
			print str(r[0])+"\t"+(r[1])
	
		with open('output', 'w') as fi: 
			for r in result: 
				fi.write(str(r[0])+"\t"+(r[1])+'\n')
		
		
if __name__ == "__main__": 
	tagger = HMMTagger()
			
