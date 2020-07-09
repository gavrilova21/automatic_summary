#!/usr/bin/env python
# coding: utf-8

# In[1]:


import nltk
import re
import pawn


# In[2]:


pawn.language()
pawn.set_language('ru')
print(pawn.language())


# In[3]:


from pawn import wordnet as wnp


# In[ ]:


from nltk.corpus import wordnet_ic
brown_ic = wnp.ic('ic-brown.dat') 


# In[ ]:


#Кнопаем для интерфейса
import sys
# Импортируем наш интерфейс
from interface23 import *
from PyQt5 import QtCore, QtGui, QtWidgets


# In[ ]:


from cleaner import clean_text_by_sentences as clean
from nltk.tokenize import sent_tokenize


# In[ ]:


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        bar = self.menuBar()
        file_menu = bar.addMenu('Файл')
        
        # adding actions to file menu
        close_action = QtWidgets.QAction('Закрыть', self)
        file_menu.addAction(close_action)

        # use `connect` method to bind signals to desired behavior
        close_action.triggered.connect(self.close)
    
        self.ui.pushButton.clicked.connect(self.DomainCheck)   
    def close_application(self):
        sys.exit()
    def on_Button_clicked(self, checked=None):
        if checked==None: return
        dialog = QDialog()
        dialog.ui = Ui_MyDialog()
        dialog.ui.setupUi(dialog)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.exec_()
    # Пока пустая функция которая выполняется
    # при нажатии на кнопку                  
    def DomainCheck(self):
        # Очищаем второе текстовое поле
        self.ui.textEdit_2.setText("")
        # В переменную stroki получаем текст из левого поля ввода
        lines = self.ui.textEdit.toPlainText() 
        # Получаем массив строк разделив текст по знаку переноса строки 
        threshold = 0.6 #treshold for wup
        jcnTreshold = 0.09 #jcn
        pathTeshold = 0.1 #path
        lexical_chains = [] #empty list to hold all the chains
        dictionary = {} #empty dictionart to hold the count of each word encountered

        #class Chain 

        class Chain(): 
            def __init__(self, words, senses, count = 0):
                    self.words = set(words)
                    self.senses = set(senses)
                    dictionary[words[0]] = 1 #initialize counter

            def addWord(self, word):
                if(len(self.words.intersection([word])) > 0):
                    dictionary[word] += 1
                else:
                    dictionary[word] = 1

                self.words.add(word)


            def addSense(self, sense):
                self.senses.add(sense)

            def getWords(self):
                return self.words

            def getSenses(self):
                return self.getSenses

            def incCount(self):
                self.count += 1

            def setScore(self, sc):
                self.score = sc

            def mfword(self):
                maxfreq = 0
                for word in self.getWords():
                    if dictionary[word] > maxfreq:
                        maxword = word	
                        maxfreq = dictionary[word]
                return maxword

        def findWholeWord(w):
            return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
        def add_word(word):
            maximum = 0 
            maxJCN = 0
            flag = 0
            for chain in lexical_chains: #for all chains that are present
                print(pawn.wordnet.synsets(word))
                for synset in wnp.synsets(word): #for all synsets of current word
                   
                    for sense in chain.senses:  #for all senses of the current word in current element of the current chain #using wup_similarity 
                        try:
                            similarity = sense.wup_similarity(synset)
                            if(similarity >= maximum):
                                if similarity >= threshold:
                                #print word, synset, sense, sense.jcn_similarity(synset, brown_ic)
                                    JCN = sense.jcn_similarity(synset, brown_ic) #using jcn_similarity
                                    if JCN >= jcnTreshold: 
                                        if sense.path_similarity(synset) >= 0.2: #using path similarity
                                            if JCN >= maxJCN:
                                                maximum = similarity
                                                maxJCN = JCN
                                                maxChain = chain
                                                flag = 1
                        except:
                            pass
            if flag == 1:                            
                maxChain.addWord(word)
                maxChain.addSense(synset)
                return    
            lexical_chains.append(Chain([word], wnp.synsets(word)))

        
        '''fileName = input("Enter file path + name, if file name is 'nlp.txt', type 'nlp' \n \n")
        fileName += ".txt"
        print ("\n\n")
        #fileName = "nlp.txt"
        File = open(fileName) #open file
        lines = File.read() #read all lines '''
        is_noun = lambda x: True if (x == 'NN' or x == 'NNP' or x == 'NNS' or x == 'NNPS'or x =='S') else False
        nouns = [word for (word, pos) in nltk.pos_tag(nltk.word_tokenize(lines),lang='rus') if is_noun(pos)and word!='—']#extract all nouns

        #for (word, pos) in nltk.pos_tag(nltk.word_tokenize(lines),lang='rus'):
           # print(word, pos)
        print(nouns)
        for word in nouns:
            print(word)
            if(len(pawn.wordnet.synsets(word))>0):
                add_word(word)

        print('Chains')
        #print all chains
        for chain in lexical_chains:
            print (", ".join(str(word + "(" + str(dictionary[word]) + ")") for word in chain.getWords()))

        print('Scoring Chains')
        #print all chains
        for chain in lexical_chains:
            chain_length = 0
            dis_word = 0
            for word in chain.getWords():
                print (str(word + "(" + str(dictionary[word]) + ")") + ',')
                chain_length = chain_length + dictionary[word]
                dis_word = dis_word + 1
            print ('Length =' + str(chain_length))
            hom = 1 - (dis_word*1.0/chain_length)
            print ('Homogeneity (однородность) =' + str(hom))
            score = 1.0*chain_length*hom
            print ('Score =' + str(score))
            chain.setScore(score)
        
        print ('Sorted start')
        lexical_chains.sort(key=lambda x: x.score, reverse=True)

        for chain in lexical_chains:
            if(chain.score>0.0):
                for word in chain.getWords():
                    print( str(word + "(" + str(dictionary[word]) + ")") + ',')
                print ('Score=' + str(chain.score))
        summary = []
        line_flags = []
        line_score=[]
        clean_lines = clean(lines)
        #clean_lines =  [sent for sent in sent_tokenize(lines, 'russian')]
        print(lines)
        line_list = [clean_line.text for clean_line in clean_lines]
        for line in line_list:
            line_flags.append(0)
            line_score.append(0)
        summary = []
        for chain in lexical_chains:

            bigword = chain.mfword()
            chain_score = chain.score
            #print '\nMF word ', bigword
            for i in range(len(line_list)):
                line=line_list[i]
                print(bigword)
                print(line)
                x = findWholeWord(bigword)(line) 
                print(x)

                    #print 'Exception : Error in finding word'
                    #x = None
                if x!=None:
                    #((line.find(' '+str(bigword)+' ')!=-1) or (line.find(' '+str(bigword)+'.')!=-1)):
                    if line_flags[i]==0:
                        summary.append(line)
                        #print 'i  ', count_words(summary)
                        line_flags[i] = 1
                        line_score[i] = chain_score
                        #print 'line_score ', line_score
                        #print 'line_flags ', line_flags

                        break
                    #elif line_flags[i]==1:
                        #line_score[i] = line_score[i] + chain.score
                        #print '\nline_score ', line_score
                    #print 'line_flags ', line_flags
                if(len(summary)>5):
                    break			


        #print(' '.join(summary)[:600]+'...')
        self.ui.textEdit_2.setText(' '.join(summary)[:600]+'...')
if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    
    wgt = QtWidgets.QLabel()
    wgt.setText("   Данная программа позволяет реферировать документы. \n Чтобы получить аннотацию документа вставте текст в левое окошко, заполните название документа и нажмите кнопку Реферировать.\n Все права защищены. \n КубГУ, 2019.")
    wgt.resize(950, 150)
    wgt.setWindowTitle('О программе')
    
    bar = myapp.menuBar()
    hell_menu = bar.addMenu('О программе')
    showWidgetAction = QtWidgets.QAction('&Справка', myapp)
    showWidgetAction.triggered.connect(wgt.show)
    hell_menu.addAction(showWidgetAction)
    sys.exit(app.exec_())
