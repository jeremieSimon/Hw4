"""
Jeremie Simon
N16247912
from POSTagger import *
t = HMMTagger()
t.tag("I love")
"""
import copy

class HMMTagger(object): 
	"""
	"""
	
	def __init__ (self): 
		
		#parse file: 
		f = open("Homework4_corpus/POSData/development.pos").read().split('\n')
		f = [line.split('\t') for line in f]
		
		self.tags = set(['', 'PRP$', 'VBG', 'VBD', '``', 'VBN', "''", 'VBP', 'WDT', 'HYPH', 'JJ', 'WP', 'VBZ', 'DT', 'RP', \
		'NN', ')', '(', 'POS', '.', 'TO', 'COMMA', 'PRP', 'RB', ':', 'NNS', 'NNP', 'VB', 'WRB', 'CC', 'PDT', 'RBS', 'RBR', \
		'CD', 'EX', 'IN', 'WP$', 'MD', 'NNPS', 'JJS', 'JJR', 'UH', '$', 'sigma', 'start'])
		pos = {}
		for tag in self.tags: pos[tag] = 0.0

		#1.0 init observationTable
		self.observationTable = {}
		
		#1.1 build the observation table from the data
		for line in f: 
			if len(line)> 1: 
				if not self.observationTable.has_key(line[0].lower()): 
					self.observationTable[line[0].lower()] = {'sigma': 0.0}
					self.observationTable[line[0].lower()][line[1].split('\r')[0]] = 1
					self.observationTable[line[0].lower()]['sigma']+=1
				else: 
					if not self.observationTable[line[0].lower()].has_key(line[1].split('\r')[0]): 
						self.observationTable[line[0].lower()][line[1].split('\r')[0]]=1.0
					else: 
						self.observationTable[line[0].lower()][line[1].split('\r')[0]]+=1.0
					self.observationTable[line[0].lower()]['sigma']+=1
		
		#1.2 compute the probabilities in the in the observation table: 
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
		self.wordEndsWithS = ""
		mini = 1
		for key in self.observationTable.iterkeys(): 
			if self.observationTable[key].has_key('NNS') and self.observationTable[key].has_key('VBZ'): 
				if  self.observationTable[key]['NNS'] + self.observationTable[key]['VBZ'] <= mini: 
					mini = self.observationTable[key]['NNS'] + self.observationTable[key]['VBZ'] 
					self.wordEndWithS = key
		
		self.wordUnknown = ""
		mini = 1
		for key in self.observationTable.iterkeys(): 
			if self.observationTable[key].has_key('NN') and self.observationTable[key].has_key('JJ'): 
				if  self.observationTable[key]['NN'] + self.observationTable[key]['JJ'] <= mini: 
					mini = self.observationTable[key]['NN'] + self.observationTable[key]['JJ'] 
					self.wordUnknown = key

	def tag(self, sentence):
		"""
		tag given a sentence
		"""
		sentence = sentence.split()
		posTags = ["" for i in range(len(sentence))]
		
		for i, word in enumerate(sentence): 
			pMax, tagMax = 0.0, ""
			
			if not self.observationTable.has_key(word.lower()): #word is not knows
			 	print "not in dict"
				if word.lower().endswith('s'):  #ends with 's'
					word = self.wordEndsWithS
				else: 
					word = self.wordUnknown
			
			if i == 0: #start case
				for key in self.observationTable[word.lower()].iterkeys(): 
					p = self.observationTable[word.lower()][key] * self.transitionTable[key]['start']
					if p > pMax: 
						pMax, tagMax= p, key
	
			else: 
				for wordTag in self.observationTable[word.lower()].iterkeys(): 
					#debug
					print "wordTag", wordTag, "posTags", posTags[i-1]
					print "obs",self.observationTable[word.lower()][wordTag], "transi",self.transitionTable[wordTag][posTags[i-1]]
					print "p", p
				
					p = self.observationTable[word.lower()][wordTag] * self.transitionTable[wordTag][posTags[i-1]]
					if self.observationTable[word.lower()][wordTag] == 1.0: 
						p , tagMax= 1, wordTag
					if p > pMax: 
						pMax, tagMax= p, wordTag
						
			posTags[i]=tagMax
		
		result = []
		for i in range(len(posTags)): 
			result.append((sentence[i], posTags[i]))
		return result
				
	
if __name__ == "__main__": 
	tagger = HMMTagger()
			
