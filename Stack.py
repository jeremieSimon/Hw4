from collections import deque

class Stack(object): 
	
	def __init__ (self, size): 
		self.size = size
		self.stack = deque([])
	
	def insert(self, element): 
		self.stack.append(element)
		while len(self.stack) > self.size: 
			self.stack.popleft()
