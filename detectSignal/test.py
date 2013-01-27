class Sentence(object):
  def __init__(self):
    self.tokens = []
  def setToken(self, token):
    self.tokens.append(token)
  def getToken(self):
    return "test"
  def getTokens(self):
    print self.tokens
    print "testes"
    return self.tokens

def main():
  sentence = Sentence()
  sentence.setToken('aaa')
  sentence.setToken('bbb')
  sentence.getTokens()
  #print sentence.getToken
if __name__ == "__main__":
  main()
  print "OK"
