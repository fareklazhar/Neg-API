# coding: utf-8
import os, commands, sys, json, math, codecs, re
from runParser import ScopeFinding

class Document(object):
  def __init__(self):
    self.sentences = []
    self.previousToken = ""
  def parseGeniaFeature(self, features):
    print features
    tokenNum = 0
    for feature in features.split("\n"):
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
        isNegation = False
        tokenNum = 0
        sentenceNum += 1
  def runParser(self):
    tokens = self.sentences
    for sentence in self.sentences:
      raw_sentence = "".join(tmp.feature["token"] + " "
                             for tmp in sentence.token_Instances)
      sf = ScopeFinding(raw_sentence)
      for i in range(len(sentence.token_Instances)):
        if sentence.token_Instances[i].feature["scope_class"] == "START":
          sentence.token_Instances[i].feature["token"] = "<neg_scope>" + sentence.token_Instances[i].feature["token"]
          sentence.token_Instances[sf.findEND(i)].feature["token"] += "</neg_scope>"
      returnSentence = "".join(tmp.feature["token"] + " "
                               for tmp in sentence.token_Instances)
      sentence.sentence_annotated_scope = returnSentence
  def outputSignalFeature(self, filename):
    for i in range(len(self.sentences)):
      self.sentences[i].outputSignalFeature(filename)
  def makeResponse_JSON(self):
    j = {"status": "OK", "results": []}
    annotated_signal = []
    annotated_scope = []

    for sentence in self.sentences:
      tmp = {
          "result_annotated_signal": sentence.sentence_annotated_signal,
          "result_annotated_scope": sentence.sentence_annotated_scope,
          "isNegation": sentence.isNegation,
      }
      j["results"].append(tmp)

    return json.dumps(j)
  def makeResponse_text(self):
    return "".join(sentence.sentence_annotated_scope + "\n"
                   for sentence in self.sentences)



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
    responseNULL = "".join("\t0" for _ in range(len(requests)))
    if n > 0:
      return ("\t" + self.token_Instances[i + n].getFeatures(requests)
              if len(self.token_Instances) > i + n else responseNULL)
    if i+n >= 0:
      return "\t" + self.token_Instances[i+n].getFeatures(requests)
    else:
      return responseNULL
  def getNeighborChunks(self, i, n):
    responseNULL = "\t0\t0\t0\t0"
    if n > 0:
      return ("\t" + self.chunk_Instances[i + n].getFeatureLine()
              if len(self.chunk_Instances) > i + n else responseNULL)
    if i+n >= 0:
      return "\t" + self.chunk_Instances[i+n].getFeatureLine()
    else:
      return responseNULL
  def setSignalClass(self, tokenNum, signalClass, token):
    self.token_Instances[tokenNum].setSignalClass(signalClass)
    if self.flag == False and signalClass != "OUTSIDE":
      self.negation_signals.append(Negation_signal(token, tokenNum))
      self.sentence_annotated_signal += f"<neg_signal>{token} "
      self.flag = True
    elif self.flag == True and signalClass == "OUTSIDE":
      self.sentence_annotated_signal += f"</neg_signal>{token} "
      self.flag = False
    else:
      if self.flag == True:

        self.negation_signals[len(self.negation_signals) - 1].addNegationToken(token, tokenNum)
      self.sentence_annotated_signal += f"{token} "
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
        scopeFeature += "\n"
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
    self.tokenNums = [tokenNum]
  def addNegationToken(self, token, tokenNum):
    self.neg_phrase += f"-{token}"
    self.tokenNums.append(tokenNum)
  def getDistanceInfo(self, tokenNum):
    distanceInfo = {"isNegSignal": "0"}
    tmp = [
        math.fabs(self.tokenNums[i] - tokenNum)
        for i in range(len(self.tokenNums))
    ]
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
    for i, requestFeature in enumerate(requestFeatureset):
      if i != 0:
        response += "\t"
      response += self.feature[requestFeature]
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
    self.tokenLine += f"-{token}"
    self.lastToken = token
    self.posLine += f"-{pos}"
  def getFirstTokenNum(self):
    return self.firstTokenNum
  def getFeatureLine(self):
    return "\t" + self.firstToken + "\t" + self.lastToken + "\t" + self.tokenLine + "\t" + self.posLine

def validateRequests(options):
  if options["train_type"] in ["clinical_records", "abstracts", "full_papers"]:
    pass
  elif options["train_type"] == "NO_REQUEST":
    options["train_type"] = "clinical_records"
  else:
    print "INVALID_REQUEST_train_type"
    makeNGResponse("INVALID_REQUEST")

  if options["output_type"] in ["json", "text"]:
    pass
  elif options["output_type"] == "NO_REQUEST":
    options["output_type"] = "json"
  else:
    print "INVALID_REQUEST_output_type"
    makeNGResponse("INVALID_REQUEST")

  if (options["sentence"] == "NO_REQUEST" and options["src"] == "NO_REQUEST") or (options["sentence"] != "NO_REQUEST" and options["src"] != "NO_REQUEST"):
    print "INVALID_REQUEST_sentence_or_src"
    makeNGResponse("INVALID_REQUEST")
  elif options["sentence"] != "NO_REQUEST":
    options["input_type"] = "sentence"
  else: 
    options["input_type"] = "src"

def makeNGResponse(status):
  print "**********"
  j = {}
  j["status"] = status
  j["results"] = []
  print json.dumps(j)
  sys.exit()

def runGeniatagger(options):
  os.chdir("../lib/geniatagger-3.0.1/")
  lines = []
  if options["input_type"] == "sentence":
    lines.append(options["sentence"])
  else:
    console = commands.getoutput("wget -O input " + options["src"])
    if len(console.split("\n")) > 2:
      if console.split("\n")[len(console.split("\n")) - 2].find("NOT FOUND") != -1:
        makeNGResponse("SRC_FILE_NOT_FOUND")
      else:
        srcFile = codecs.open("input", "r", "utf-8")
        
        lines = srcFile.readlines()
    else:
      makeNGResponse("INTERNAL_ERROR")
  feature = ""
  for line in lines:
    print "****"
    command = "/usr/local/bin/ruby client.rb \"" + line.replace(".", " . ") + "\""
    command = re.sub(r'[\n|\r|\r\n]', '', command)
    feature += commands.getoutput(command).replace(" ", "\n")
  print feature
  os.chdir("../../cgi-bin")

  return feature

def runPhase1(document, options, features):
  #geniataggerOutput = open("../tmpFiles/SignalIdentification/geniataggerOutput")
  #features = geniataggerOutput.readlines()
  document.parseGeniaFeature(features)
  with open("../tmpFiles/SignalIdentification/features", "w") as output_signalFeature:
    document.outputSignalFeature(output_signalFeature)
  commands.getoutput("/usr/local/bin/timbl -f ../data/phase1/" + options["train_type"] + ".txt -t ../tmpFiles/SignalIdentification/features -o ../tmpFiles/SignalIdentification/timbl_learned")
  with open("../tmpFiles/SignalIdentification/timbl_learned") as inputTimblLearned:
    results = inputTimblLearned.readlines()
    document.parseTimblLearned_signal(results)
def runPhase2(document, options):
  with open("../tmpFiles/ScopeIdentification/features", "w") as output_scopeFeature:
    for sentence in document.sentences:
      sentence.outputScopeFeature(output_scopeFeature)
  commands.getoutput("/usr/local/bin/timbl -f ../data/phase2/" + options["train_type"] + ".txt -t ../tmpFiles/ScopeIdentification/features -o ../tmpFiles/ScopeIdentification/timbl_learned")
  inputTimblLearned = open("../tmpFiles/ScopeIdentification/timbl_learned")
  results = inputTimblLearned.readlines()
  document.parseTimblLearned_scope(results)
  document.runParser()

  

########  main  ########
def main():
  document = Document()
  options = {"train_type" : "clinical_records", "output_type" : "json"}
  print "OK"
  print sys.argv[3]
  if len(sys.argv) > 4:
    options["train_type"] = sys.argv[1]
    options["output_type"] = sys.argv[2]
    options["src"] = sys.argv[3]
    options["sentence"] = sys.argv[4]
    validateRequests(options)
  else:
    makeNGResponse("INTERNAL_ERROR")
  
  feature = runGeniatagger(options)
  runPhase1(document, options, feature)
  runPhase2(document, options)
  print "**********"
  if options["output_type"] == "text":
    print document.makeResponse_text()
  else:
    print document.makeResponse_JSON()
  

if __name__ == "__main__":
  main()
