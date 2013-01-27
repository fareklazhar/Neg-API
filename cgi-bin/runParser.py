# coding: utf-8
from parser import Parser
class ScopeFinding:
	def __init__(self, sentence):
		self.sentence = sentence
		self.tokens, self.root = Parser().parse(sentence)
	def findEND(self, START_num):
		start_node = self.root.getLeaves().get(START_num)
		end_node = self.root.getLeaves().get(START_num)
		if START_num != self.root.getLeaves().size() - 1:
			for i in range(self.root.depth() + 1):
				if start_node.ancestor(i, self.root).getLeaves().get(0) != start_node:
					if i != 0 and start_node.ancestor(i-1, self.root).getLeaves().size() == 0:
						pass
					elif i != 0 and start_node.ancestor(i-1, self.root).getLeaves().get(start_node.ancestor(i-1, self.root).getLeaves().size() - 1) == start_node:
						pass
					else:
						scope = start_node.ancestor(i-1, self.root).getLeaves()
						end_node = scope.get(scope.size() - 1)
						break
		for i in range(self.root.getLeaves().size()):
			if self.root.getLeaves().get(i) == end_node:
				return i

def main():
	scopefinding = ScopeFinding("The girl I met was your sister.")
	scopefinding.findEND(3)

