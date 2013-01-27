# coding: utf-8
import os, commands, sys, json, math
from runParser import ScopeFinding

class Document(object):
  def __init__(self):
    self.sentences = []
    self.previousToken = ""
  def parseGeniaFeature(self, features):
    tokenNum = 0
    for feature in features:
      feature_array = feature.replace("\n", "").split("\t")
      if len(feature_array) == 5:
        self.selectSentence(feature_array, tokenNum)
        if feature_array[0] == ".":
          tokenNum = 0
        else:
          tokenNum += 1
  def selectSentence(self, feature_array, tokenNum):
    if len(self.sentences) == 0 or (len(self.sentences) > 0 and self.previousToken == "."):
      self.sentences.append(Sentence())
    self.sentences[len(self.sentences) - 1].storeFeature(feature_array, tokenNum)
    self.previousToken = feature_array[0]
  def parseTimblLearned_signal(self, results):
    tokenNum = 0
    sentenceNum = 0
    isNegation = False
    for i in range(len(results)):
      result_array = results[i].replace("\n", "").split(" ")
      if len(result_array) > 1:
        if result_array[len(result_array) - 1] != "OUTSIDE\n":
          isNegation = True
        self.sentences[sentenceNum].setSignalClass(tokenNum, result_array[len(result_array) - 1], result_array[0])
        tokenNum += 1
      if result_array[0] == ".":
        self.sentences[sentenceNum].setIsNegation(isNegation)
        tokenNum = 0
        sentenceNum += 1
  def parseTimblLearned_scope(self, results):
    tokenNum = 0
    sentenceNum = 0
    isNegation = False
    for i in range(len(results)):
      result_array = results[i].replace("\n", "").split(" ")
      if len(result_array) > 1:
        label = "NEITHER"
        
        if result_array[len(result_array) - 1] == "START":
          isNegation = True
          label = "START"
        self.sentences[sentenceNum].setScopeClass(tokenNum, label, result_array[0])
        tokenNum += 1
      if result_array[0] == ".":
        self.sentences[sentenceNum].setIsNegation(isNegation)
        tokenNum = 0
        sentenceNum += 1
  def runParser(self):
    tokens = self.sentences
    for sentence in self.sentences:
      raw_sentence = ""
      for tmp in sentence.token_Instances:
        raw_sentence += tmp.feature["token"] + " "
      sf = ScopeFinding(raw_sentence)
      for i in range(len(sentence.token_Instances)):
        if sentence.token_Instances[i].feature["scope_class"] == "START":
          sentence.token_Instances[i].feature["token"] = "<neg_scope>" + sentence.token_Instances[i].feature["token"]
          sentence.token_Instances[sf.findEND(i)].feature["token"] += "</neg_scope>"
      returnSentence = ""
      for tmp in sentence.token_Instances:
         returnSentence += tmp.feature["token"] + " "
      sentence.sentence_annotated_scope = returnSentence
  def outputSignalFeature(self, filename):
    for i in range(len(self.sentences)):
      self.sentences[i].outputSignalFeature(filename)
  def makeResponse_JSON(self):
    j = {}
    j["status"] = "OK"
    j["results"] = []
    annotated_signal = []
    annotated_scope = []
    for sentence in self.sentences:
      tmp = {}
      tmp["result_annotated_signal"] = sentence.sentence_annotated_signal
      tmp["result_annotated_scope"] = sentence.sentence_annotated_scope
      tmp["isNegation"] = sentence.isNegation
      j["results"].append(tmp)
    
    return json.dumps(j)



class Sentence(object):
  def __init__(self):
    self.signal_timblLearned = ""
    self.token_Instances = []
    self.chunk_Instances = []
    self.isNegation = False
    self.sentence_annotated_signal = ""
    self.sentence_annotated_scope = ""
    self.negation_signals = []
    self.previousTypeOfChunk = ""
    self.flag = False
  def storeFeature(self, feature_array, tokenNum):
    instance = Token(feature_array)
    self.token_Instances.append(instance)
    if len(self.chunk_Instances) == 0:
      self.chunk_Instances.append(Chunk(0, feature_array[0], feature_array[2]))
    else:
      typeOfChunk = feature_array[3].split("-")[0]
      if typeOfChunk == "I":
        self.chunk_Instances[len(self.chunk_Instances) - 1].addToken(feature_array[0], feature_array[2])
      else:
        self.chunk_Instances.append(Chunk(tokenNum, feature_array[0], feature_array[2]))
  def outputSignalFeature(self, filename):
    signalFeature = ""
    for i in range(len(self.token_Instances)):
      signalFeature = self.token_Instances[i].getFeatures(["token", "raw_word", "pos", "chunk"]) 
      signalFeature += self.getNeighborFeatures(["raw_word", "pos", "chunk"], i, 1)
      signalFeature += self.getNeighborFeatures(["raw_word", "pos", "chunk"], i, -1)
      signalFeature += self.getNeighborFeatures(["raw_word"], i, 2)
      signalFeature += self.getNeighborFeatures(["raw_word"], i, -2)
      signalFeature += "\tUNKNOWN_LABEL\n"
      filename.write(signalFeature)
  def getNeighborFeatures(self, requests, i, n):
    responseNULL = ""
    for x in range(len(requests)):
      responseNULL += "\t0"
    if n > 0:
      if len(self.token_Instances) > i+n:
        return "\t" + self.token_Instances[i+n].getFeatures(requests)
      else:
        return responseNULL
    else:
      if i+n >= 0:
        return "\t" + self.token_Instances[i+n].getFeatures(requests)
      else:
        return responseNULL
  def getNeighborChunks(self, i, n):
    responseNULL = "\t0\t0\t0\t0"
    if n > 0:
      if len(self.chunk_Instances) > i+n:
        return "\t" + self.chunk_Instances[i+n].getFeatureLine()
      else:
        return responseNULL
    else:
      if i+n >= 0:
        return "\t" + self.chunk_Instances[i+n].getFeatureLine()
      else:
        return responseNULL
  def setSignalClass(self, tokenNum, signalClass, token):
    self.token_Instances[tokenNum].setSignalClass(signalClass)
    if self.flag == False and signalClass != "OUTSIDE":
      self.negation_signals.append(Negation_signal(token, tokenNum))
      self.sentence_annotated_signal += "<neg_signal>" + token + " "
      self.flag = True
    elif self.flag == True and signalClass == "OUTSIDE":
      self.sentence_annotated_signal += "</neg_signal>" + token + " "
      self.flag = False
    else:
      if self.flag == True:
        self.negation_signals[len(self.negation_signals - 1)].addNegationToken(token, tokenNum)
      self.sentence_annotated_signal += token + " "
  def setScopeClass(self, tokenNum, scopeClass, token):
    self.token_Instances[tokenNum].setScopeClass(scopeClass)
  def setIsNegation(self, isNegation):
    self.isNegation = isNegation
  def getMyChunkNum(self, tokenNum):
    for i in range(len(self.chunk_Instances)):
      if tokenNum == 0:
        return 0
      if tokenNum < self.chunk_Instances[i].getFirstTokenNum():
        return i - 1
    return len(self.chunk_Instances) - 1
  def outputScopeFeature(self, filename):
    scopeFeature = ""
    instances = self.token_Instances
    for i in range(len(instances)):
      scopeFeature = instances[i].getFeatures(["token"])
      if len(self.negation_signals) == 0:
        for i in range(47):
          scopeFeature += "\t0"
      else:
        tmp_negation_signals = sorted(self.negation_signals, key=lambda x:x.getDistanceInfo(i)["distance"])
        scopeFeature += "\t" + tmp_negation_signals[0].neg_phrase
        scopeFeature += "\t" + self.token_Instances[i].getFeatures(["raw_word", "pos", "chunk", "typeOfChunk"])
        scopeFeature += self.getNeighborFeatures(["raw_word", "pos", "chunk", "typeOfChunk"], i, -1)
        scopeFeature += self.getNeighborFeatures(["raw_word"], i, -2)
        scopeFeature += self.getNeighborFeatures(["raw_word"], i, -3)
        scopeFeature += self.getNeighborFeatures(["raw_word", "pos", "chunk", "typeOfChunk"], i, +1)
        scopeFeature += self.getNeighborFeatures(["raw_word", "pos", "chunk", "typeOfChunk"], i, +2)
        scopeFeature += self.getNeighborFeatures(["raw_word", "pos", "chunk", "typeOfChunk"], i, +3)
        scopeFeature += self.chunk_Instances[self.getMyChunkNum(i)].getFeatureLine()
        scopeFeature += self.getNeighborChunks(self.getMyChunkNum(i), -1)
        scopeFeature += self.getNeighborChunks(self.getMyChunkNum(i), -2)
        scopeFeature += self.getNeighborChunks(self.getMyChunkNum(i), +1)
        scopeFeature += self.getNeighborChunks(self.getMyChunkNum(i), +2)
        
        scopeFeature += "\t" + str(int(tmp_negation_signals[0].getDistanceInfo(i)["distance"]))
        scopeFeature += "\t" + tmp_negation_signals[0].getDistanceInfo(i)["position"]
        scopeFeature += "\t" + tmp_negation_signals[0].getDistanceInfo(i)["isNegSignal"]
        scopeFeature += "\tUNKNOWN_LABEL\n"
      filename.write(scopeFeature)
    

class Negation_signal(object):
  def __init__(self, token, tokenNum):
    self.neg_phrase = token
    self.tokenNums = []
    self.tokenNums.append(tokenNum)
  def addNegationToken(self, token, tokenNum):
    self.neg_phrase += "-" + token
    self.tokenNums.append(tokenNum)
  def getDistanceInfo(self, tokenNum):
    tmp = []
    distanceInfo = {}
    distanceInfo["isNegSignal"] = "0"
    for i in range(len(self.tokenNums)):
      tmp.append(math.fabs(self.tokenNums[i] - tokenNum))
    if min(tmp) == 0:
      distanceInfo["position"] = "SAME"
      distanceInfo["isNegSignal"] = "Neg"
    elif tokenNum - self.tokenNums[0] > 0:
      distanceInfo["position"] = "POST"
    else:
      distanceInfo["position"] = "PRE"     
    distanceInfo["distance"] = min(tmp)
    return distanceInfo

class Token(object):
  def __init__(self, feature):
    self.feature = {}
    self.setFeature(feature)
  def setFeature(self, feature):
    self.feature["token"] = feature[0]
    self.feature["raw_word"] = feature[1]
    self.feature["pos"] = feature[2]
    self.feature["chunk"] = feature[3]
    if len(feature[3].split("-")) == 2:
      self.feature["typeOfChunk"] = feature[3].split("-")[1]
    else:
      self.feature["typeOfChunk"] = "0"
  def getFeatures(self, requestFeatureset):
    response = ""
    i = 0
    for requestFeature in requestFeatureset:
      if i != 0:
        response += "\t"
      response += self.feature[requestFeature]
      i += 1
    return response
  def setSignalClass(self, signalClass):
    self.feature["signal_class"] = signalClass
  def setScopeClass(self, scopeClass):
    self.feature["scope_class"] = scopeClass
class Chunk(object):
  def __init__(self, tokenNum, token, pos):
    self.firstTokenNum = tokenNum
    self.firstToken = token
    self.lastToken = token
    self.tokenLine = token
    self.posLine = pos
  def addToken(self, token, pos):
    self.tokenLine += "-" + token
    self.lastToken = token
    self.posLine += "-" + pos
  def getFirstTokenNum(self):
    return self.firstTokenNum
  def getFeatureLine(self):
    return "\t" + self.firstToken + "\t" + self.lastToken + "\t" + self.tokenLine + "\t" + self.posLine



def runPhase1(document):
###  parse using geniatagger  ###
  os.chdir("../lib/geniatagger-3.0.1/")
  if len(sys.argv) > 1:
    userInputSentence = sys.argv[1]
    commands.getoutput("echo " + userInputSentence + " | ./geniatagger > ../../tmpFiles/SignalIdentification/geniataggerOutput")
  os.chdir("../../cgi-bin")
###  make featureset_signal using geniatagger output  ###
  geniataggerOutput = open("../tmpFiles/SignalIdentification/geniataggerOutput")
  features = geniataggerOutput.readlines()
  document.parseGeniaFeature(features)
  output_signalFeature = open("../tmpFiles/SignalIdentification/features", "w")
  document.outputSignalFeature(output_signalFeature)
  output_signalFeature.close()
  commands.getoutput("/usr/local/bin/timbl -f ../data/phase1/clinical_records.txt -t ../tmpFiles/SignalIdentification/features -o ../tmpFiles/SignalIdentification/timbl_learned")
  inputTimblLearned = open("../tmpFiles/SignalIdentification/timbl_learned")
  results = inputTimblLearned.readlines()
  document.parseTimblLearned_signal(results)
  inputTimblLearned.close()

def runPhase2(document):
  output_scopeFeature = open("../tmpFiles/ScopeIdentification/features", "w")
  for sentence in document.sentences:
    sentence.outputScopeFeature(output_scopeFeature)
  output_scopeFeature.close()
  commands.getoutput("/usr/local/bin/timbl -f ../data/phase2/clinical_records.txt -t ../tmpFiles/ScopeIdentification/features -o ../tmpFiles/ScopeIdentification/timbl_learned")
  inputTimblLearned = open("../tmpFiles/ScopeIdentification/timbl_learned")
  results = inputTimblLearned.readlines()
  document.parseTimblLearned_scope(results)
  document.runParser()


########  main  ########
if __name__ == "__main__":
  document = Document()
  runPhase1(document)
  runPhase2(document)
  print "**********"
  print document.makeResponse_JSON()
  
