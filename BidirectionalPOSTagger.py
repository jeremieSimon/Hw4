"""
Jeremie Simon
N16247912

Implementation details: 
With the basic HMM Tagger using a bigram model, I scored a 83% precision. 
I tried then to keep the same model and add a few features for the unknown words 
by treating the differently depending on how do they end (ed, ing...). 
I also made a few assumptions.A non-starting word in a sentence starting with an uppercase letter is a PPN and if 
it ends with a 's' it is a PPNS
I added a few basic things, like the month of the year and the day of the week to the vocabulary.
With just these few optimizations, I was able to score a 85% of precision.

I then used a bidirectional model from left to right and right to left. 
And make the result of these 2 converging to the one with highest confidence. 
This made my score rised to 88%. 
"""

import copy
import string
import sys

class HMMTagger(object): 
	"""
	"""
	
	def __init__ (self): 
		
		#parse file: 
		f = open("training.pos").read().split('\n')
		#f = open("trainingTest.txt").read().split('\n')
		f = [line.split('\t') for line in f]
		
		self.numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, '-']
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',\
		 'November', 'December']
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		
		self.tags = set(['', 'PRP$', 'VBG', 'VBD', '``', 'VBN', "''", 'VBP', 'WDT', 'HYPH', 'JJ', 'WP', 'VBZ', 'DT', 'HV', 'RP', '$', 'NN', \
		'PRT', ')', '(', 'FW', 'POS', '.', 'TO', 'COMMA', 'PRP', 'RB', ':', 'NNS', 'NNP', 'NNS-4', 'VB', 'ADVP-MNR', 'WRB', \
		'CC', 'LS', 'PDT', 'RBS', 'RBR', 'CD', '-LSB-', 'EX', 'IN', 'WP$', 'MD', 'NNPS', 'JJS', 'JJR', 'SYM', 'UH', 'AFX', \
		'-RSB-', 'sigma', 'start'])
		pos = {}
		for tag in self.tags: pos[tag] = 0.0

		#1.0 init observationTable
		self.observationTable = {}
		self.observationTable['__endswithing__'] = {'sigma':0.0}
		self.observationTable['__endswithed__'] = {'sigma':0.0}
		self.observationTable['__endswithic__'] = {'sigma':0.0}
		self.observationTable['__endswithian__'] = {'sigma':0.0}
		self.observationTable['__endswithians__'] = {'sigma':0.0}
		self.observationTable['__endswithen__'] = {'sigma':0.0}
		self.observationTable['__endswithal__'] = {'sigma':0.0}
		self.observationTable['__endswithious__'] = {'sigma':0.0}
		self.observationTable['__endswithul__'] = {'sigma':0.0}
				
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
						
				if line[0].lower().endswith('ed'): helper('ed')
				elif line[0].lower().endswith('en') and not line[0][0] in string.uppercase:helper('en')
				elif line[0].lower().endswith('ing'): helper('ing')
				elif line[0].lower().endswith('ic'): helper('ic')
				elif line[0].lower().endswith('ian'): helper('ian')
				elif line[0].lower().endswith('ians'): helper('ians')
				elif line[0].lower().endswith('al'): helper('al')
				elif line[0].lower().endswith('ious'): helper('ious')
				elif line[0].lower().endswith('ul'): helper('ul')
								
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
						self.observationTable['__propernoun__'] = {'sigma':1.0}
						self.observationTable['__propernoun__']['NNP'] = 1
					
					#3. neither proper noun or numbers. regular case
					else:						
						self.observationTable[line[0].lower()] = {'sigma': 0.0}
						self.observationTable[line[0].lower()][line[1].split('\r')[0]] = 1
						self.observationTable[line[0].lower()]['sigma']+=1
				#word is known
				else: 
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
		self.transitionTableLeftRight = {}
		self.transitionTableRightLeft = {}


		#2.1 init transitionTableLeftRight
		for tag in pos: 
			if tag != 'sigma' and tag != 'start': 
				self.transitionTableLeftRight[tag] = copy.deepcopy(pos)
				self.transitionTableRightLeft[tag] = copy.deepcopy(pos)
				
		#2.2 build transitionTableLeftRight
		for i, line in enumerate(f): 
			if len(line)> 1:
				if i == 0: #start case: 
					self.transitionTableLeftRight[line[1].split('\r')[0]]['start'] +=1
					self.transitionTableLeftRight[line[1].split('\r')[0]]['sigma'] +=1
				else: 
					tag = f[i-1][1].split('\r')[0]
					#tag is empty: 
					if tag == "": 
						self.transitionTableLeftRight[line[1].split('\r')[0]]['start']+=1
					else: 
						self.transitionTableLeftRight[line[1].split('\r')[0]][tag]+=1
					self.transitionTableLeftRight[line[1].split('\r')[0]]['sigma'] +=1

		#2.3 build transitionTableRightLeft
		for i in range(len(f)-1, -1, -1): 
			line = f[i]
			if len(line)> 1:
				if i == len(f)-1: #start case: 
					self.transitionTableRightLeft[line[1].split('\r')[0]]['start'] +=1
					self.transitionTableRightLeft[line[1].split('\r')[0]]['sigma'] +=1
				else: 
					#tag is empty: 
					if f[i+1] == [""]: 
						self.transitionTableRightLeft[line[1].split('\r')[0]]['start']+=1
					else: 
						tag = f[i+1][1].split('\r')[0]
						self.transitionTableRightLeft[line[1].split('\r')[0]][tag]+=1
					self.transitionTableRightLeft[line[1].split('\r')[0]]['sigma'] +=1
			
		#2.3 transform to probabilities
		for tags in self.transitionTableLeftRight.itervalues(): 
			for key in tags.iterkeys(): 
				if key != 'sigma':
					try: 
						tags[key] = tags[key] / tags['sigma']
					except ZeroDivisionError: pass	
			del(tags['sigma']) #sigma is no longer needed
		
		for tags in self.transitionTableRightLeft.itervalues(): 
			for key in tags.iterkeys(): 
				if key != 'sigma':
					try: 
						tags[key] = tags[key] / tags['sigma']
					except ZeroDivisionError: pass	
			del(tags['sigma']) #sigma is no longer needed
		
				
		#3. search word with lowest NNS and VBZ: 		
		self.observationTable['__propernouns__'] = {'NNPS': 1.0}
		self.observationTable['__noun__'] = {'NN':1.0}		
		self.observationTable['__nouns__'] = {'NNS':1.0}
		#self.observationTable['COMMA'] = {'COMMA':1.0}
	
		self.wordEndsWithS = "" 
		mini = 10
		for key in self.observationTable.iterkeys(): 
			if self.observationTable[key].has_key('NNS') and self.observationTable[key].has_key('VBZ') and \
			not key.startswith('__'): 
				if  (self.observationTable[key]['NNS'] + self.observationTable[key]['VBZ']) <= mini: 
					mini = self.observationTable[key]['NNS'] + self.observationTable[key]['VBZ'] 
					self.wordEndsWithS = key
		
		self.wordUnknown = ""
		mini = 10
		for key in self.observationTable.iterkeys(): 
			if self.observationTable[key].has_key('NN') and self.observationTable[key].has_key('JJ') and \
			not key.startswith('__'): 
				if  self.observationTable[key]['NN'] + self.observationTable[key]['JJ'] <= mini: 
					mini = self.observationTable[key]['NN'] + self.observationTable[key]['JJ'] 
					self.wordUnknown = key
		
		self.observationTable["__fakeadverb__"] = {'RB':0.90, 'NN':0.09, "JJ":0.01}

	def _tagLeftToRight(self, sentence):
		"""
		Description: called by generateTag. Use HMM algo from left to right
		@return list of tuples (word, tag) and the list of probabilities for each tag choosen 
		@param sentence 		
		"""
		
		posTags = ["" for i in range(len(sentence))]
		isEndOfSentence = [False, False]
		prevWord = ""
		pMax = [0.0 for i in range(len(sentence))]
		for i, word in enumerate(sentence): 
			tagMax = ""
			if word == "" or i == 0: isEndOfSentence[i%2] = True 
			else: isEndOfSentence[i%2] = False

			#EXCEPTION CASES
			#1. identify if it is a number: 
			if True in (True for num in self.numbers if word.startswith(str(num))): 
				try: 
					number = int(word)
					word = '__numeric__'
				except ValueError: pass
		
			#2. word is a proper noun
			if not True in isEndOfSentence and word[0] in string.uppercase and word != "COMMA" and word != "I": 
				if word.endswith('s'): word = '__propernouns__'
				else: word = '__propernoun__'
			
			#3. word is not known 
			if not self.observationTable.has_key(word.lower()): 
				if word.lower().endswith('ions') or word.lower().endswith('ies'): word = '__nouns__'
				elif word.lower().endswith('ity') or word.lower().endswith('ent') or \
					word.lower().endswith('ion') : word = '__noun__'
				elif word.lower().endswith('ing'): word = '__endswithing__'
				elif word.lower().endswith('ed'): word = '__endswithed__'
				elif word.lower().endswith('ic'): word = '__endswithic__'
				elif word.lower().endswith('ian'): word = '__endswithian__'
				elif word.lower().endswith('ian'): word = '__endswithians__'	
				elif word.lower().endswith('en'): word = '__endswithen__'
				elif word.lower().endswith('al'): word = '__endswithal__'
				elif word.lower().endswith('ious'): word = '__endswithious__'
				elif word.lower().endswith('ul'): word = '__endswithul__'
				elif word.lower().endswith('s'):  word = self.wordEndsWithS 
				elif word.endswith('ly'): word = '__fakeadverb__'
				else: word = self.wordUnknown					
			#END OF EXCEPTION CASES
			
			if i == 0 or prevWord == "": #start case
				for key in self.observationTable[word.lower()].iterkeys(): 
					p = self.observationTable[word.lower()][key] * self.transitionTableLeftRight[key]['start']
					if p > pMax[i]: 
						pMax[i], tagMax= p, key
													
			else: 
				for wordTag in self.observationTable[word.lower()].iterkeys(): 
					p = self.observationTable[word.lower()][wordTag] * self.transitionTableLeftRight[wordTag][posTags[i-1]]	
					if self.observationTable[word.lower()][wordTag] == 1.0: 
						p , tagMax= 1, wordTag
					if p > pMax[i]: 
						pMax[i], tagMax= p, wordTag
			posTags[i]=tagMax
			prevWord = word
		
		result = []
		for i in range(len(posTags)): 
			result.append((sentence[i], posTags[i]))
		return result, pMax

	def _tagRightToLeft(self, sentence):
		"""
		Description: called by generateTag. Use HMM algo from right to left
		@return list of tuples (word, tag) and the list of probabilities for each tag choosen 
		@param sentence 		
		"""

		posTags = ["" for i in range(len(sentence))]
		isEndOfSentence = [False, False]
		pMax = [0.0 for j in range(len(sentence))]
		for i in range(len(sentence)-1, -1, -1): 
			word = sentence[i]
			nextWord = sentence[i-1] 
			tagMax = ""
			if nextWord == "" or i == 0: isEndOfSentence[i%2] = True 
			else: isEndOfSentence[i%2] = False

			#EXCEPTION CASES
			#1. identify if it is a number: 
			if True in (True for num in self.numbers if word.startswith(str(num))): 
				try: 
					number = int(word)
					word = '__numeric__'
				except ValueError: pass

			#2. word is a proper noun
			if word!= "" and not True in isEndOfSentence and word[0] in string.uppercase and word != "COMMA" and word != "I": 
				if word.endswith('s'): word = '__propernouns__'
				else: word = '__propernoun__'

			#3. word is not known 
			if not self.observationTable.has_key(word.lower()): 
				if word.lower().endswith('ions') or word.lower().endswith('ies'): word = '__nouns__'
				elif word.lower().endswith('ity') or word.lower().endswith('ent') or \
					word.lower().endswith('ion') : word = '__noun__'
				elif word.lower().endswith('ing'): word = '__endswithing__'
				elif word.lower().endswith('ed'): word = '__endswithed__'
				elif word.lower().endswith('ic'): word = '__endswithic__'
				elif word.lower().endswith('ian'): word = '__endswithian__'
				elif word.lower().endswith('ian'): word = '__endswithians__'	
				elif word.lower().endswith('en'): word = '__endswithen__'
				elif word.lower().endswith('al'): word = '__endswithal__'
				elif word.lower().endswith('ious'): word = '__endswithious__'
				elif word.lower().endswith('ul'): word = '__endswithul__'
				elif word.lower().endswith('s'):  word = self.wordEndsWithS 
				elif word.endswith('ly'): word = '__fakeadverb__'
				else: word = self.wordUnknown					
			#END OF EXCEPTION CASES

			if i == len(sentence)-1 or nextWord == "": #start case
				for key in self.observationTable[word.lower()].iterkeys(): 
					p = self.observationTable[word.lower()][key] * self.transitionTableLeftRight[key]['start']
					if p > pMax[i]: 
						pMax[i], tagMax= p, key

			else: 
				for wordTag in self.observationTable[word.lower()].iterkeys(): 
					p = self.observationTable[word.lower()][wordTag] * self.transitionTableRightLeft[wordTag][posTags[i+1]]	
					if self.observationTable[word.lower()][wordTag] == 1.0: 
						p , tagMax= 1, wordTag
					if p > pMax[i]: 
						pMax[i], tagMax= p, wordTag

			posTags[i]=tagMax

		result = []
		for i in range(len(posTags)): 
			result.append((sentence[i], posTags[i]))
		return result, pMax
				
	
	def generateTag(self, textfile):
		"""
		Description: transform the textfile as an array of words, call the function to add tag
		to each word and return the output
		@param textfile
		"""
		textfile = open(textfile).read().split('\n')
		sentence = []
		results = []
		for word in textfile: 
			sentence.append(word)
			if word == "": 				
				#result left to right
				left = self._tagLeftToRight(sentence)
				#result right to left
				right = self._tagRightToLeft(sentence)
				result = left[0]
				for i in range(len(sentence)): 
					if left[0][i] != right[0][i]: 
						if left[1][i] >= right[1][i]: 
							result[i] = left[0][i]
						else:  
							result[i] = right[0][i]
				results.append(result)
				sentence = []
		results = [el for sentence in results for el in sentence]

		with open('output', 'w') as f: 
	 		for result in results: 
				f.write(str(result[0])+"\t"+(result[1])+'\n')
		
		
if __name__ == "__main__": 
	#only 1 argument is passed to the command line
	#The argument should be a textfile with one word on each line
	#The format has to be the same has the one proposed in both training.txt and development.txt
	tagger = HMMTagger()
	textfile = sys.argv[1]
	tagger.generateTag(textfile)
	
			
