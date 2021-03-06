# -*- coding: utf-8 -*-

import os
import glob
import sys
import re

# Display debug information, print to statistics file
verbose = 0

obstruents = {'b':'B', 'd':'D', 'g':'G'}
nasals = ['m', 'n', 'N']
# Vocales
vowels = ['a', 'e', 'i', 'o', 'u']
# Semivocales
semivowels = ['%', '#', '@', '$', '&', '!', '*', '+', '-', '3']
# Voiced consonants
voiced = ['b', 'B', 'd', 'D', 'g', 'G', 'm', 'n', 'N', '|', 'J', 'r', 'R']

# Track the number of utterances
numUtterances = 0
# Track the number of words
numWords = 0
#wordsPerUtterance = []
phonemesPerWord = []

def interVocalicRules(sent):
    newSent = sent
    
    # Create all the dipthongs that occur between words
    newSent = newSent.replace('a i', '- ')
    newSent = newSent.replace('a u', '+ ')
    # Do I indicate vowel lengthening?
#    newSent = newSent.replace('a a', 'aa ')
    newSent = newSent.replace('e i', '* ')
#    newSent = newSent.replace('e e', 'ee ')
    newSent = newSent.replace('i a', '% ')
    newSent = newSent.replace('i e', '# ')
    newSent = newSent.replace('i o', '@ ')
#    newSent = newSent.replace('i i', 'ii ')
    newSent = newSent.replace('o i', '3 ')
#    newSent = newSent.replace('o o', 'oo ')
    # This is not a dipthong replacement but it still needs to happen:
    # lo ultimo = [lultimo]
    newSent = newSent.replace('o u', 'u ')
    newSent = newSent.replace('u a', '& ')
    newSent = newSent.replace('u e', '$ ')
    newSent = newSent.replace('u i', '! ')
#    newSent = newSent.replace('u u', 'uu ')

    # Avoid creating onsets that are illegal
    newSent = newSent.replace(' nt','n t')
    newSent = newSent.replace(' nR','n R')
    newSent = newSent.replace(' zl','z l')
    newSent = newSent.replace(' zR','z R')
    newSent = newSent.replace(' ts','t s')
    newSent = newSent.replace(' tl','t l')
    newSent = newSent.replace(' tR','t R')
    newSent = newSent.replace(' nd','n d')
    newSent = newSent.replace(' ks','k s')
    newSent = newSent.replace(' kl','k l')

    
    # Turn b/d/g's into B/D/G's where appropriate
    strList = list(newSent)
    i = 0
    prev = None
    for symbol in strList:
        if symbol in obstruents:
            if not prev or prev in nasals:
                i += 1
                continue
            else:
                strList[i] = obstruents[symbol]
        if symbol in voiced:
            if prev == 's':
                strList[i-1] = 'z'
        prev = symbol
        i += 1
    newSent = "".join(strList)
    
    return newSent

def sententialRules(sentence):
    # Apply rules between words, like when a [b] occurs between vowels, turn it into a [B]
    # Vowels together.. a aser = aser
    # Apply rule for two vowels being together.. si aqui = s(ia dipthong)ki...
    
    # Split the sentence into chunks based on pauses.
    # This distinction exists because:
    
    chunks = sentence.split('[/]')
    # This has to be done here because I allow [/] to be remain up until this point
    # for the purpose of knowing where boundaries occur, but we don't want to count [/]

    newChunkList = []
    for chunk in chunks:
        #wordsPerUtterance.append(len(chunk.split()))
        globals()["numWords"] += len(chunk.split())
        
        newChunk = interVocalicRules(chunk)
        if verbose == 1:
                print newChunk
                      
        newChunkList.append(newChunk)
        
    return newChunkList   

def main():
    dictFile = "Spanish/dicts/dict_converted.txt"
    chaDir = "Spanish/cha_files/"
    
    file = open(dictFile, 'r')
    lines = file.readlines()
    file.close()
    
    # Word bank is a dictionary - lookup by its key retrieves its IPA translation
    word = {}
    
    # Split by whitespace since that's how it's set up
    for line in lines:
        x = line.split()
        word[x[0].lower()] = x[1]

    keyErrors = open("Spanish/dicts/keyErrors.txt", "w")
    outFile = open("Spanish/Spanish-phon.txt", 'w')
    outFileOrig = open("Spanish/Spanish-ortho.txt", 'w')
    
    for fileName in sorted(glob.glob(os.path.join(chaDir, '*.cha'))):
        # Skip file if it's not below 20 months
        if fileName.startswith(tuple([chaDir + str(28),chaDir + str(36)])):
                continue

        if verbose == 1:
                print fileName
        file = open(fileName, 'r')
        lines = file.readlines()
        file.close()
        
        #file = open(fileName.replace('.cha', '_ipa.txt'), 'w')
        for line in lines:
            # Only look at child-directed speech(from INV or PAR)
            if line.startswith('*INV') or line.startswith('*PAR') or line.startswith('*TEA') or line.startswith('*FAT'):
                if verbose == 1:
                        print 'Original line: ' + line

                # Split on pauses to separate utterances and count them
                #numUtterances += len(line.split('[/]'))
                # Split the sentence into individual words
                words = line.split()
                # Build the IPA-translated sentence
                ipaSentence = ""

                # Look up individual words
                for x in words[1:]:
                    # Ignore punctuation
                    if x == '.' or x == '?' or x == '!':
                        continue

                    outFileOrig.write(x + ' ')

                    # Need to make some character substitions to make dictionary search work
                    x = re.sub('é','}',x)
                    x = re.sub('á','{',x)
                    x = re.sub('í','<',x)
                    x = re.sub('ó','>',x)
                    x = re.sub('ú','}',x)
                    x = re.sub('ñ','|',x)
                    x = re.sub('ü','=',x)
                    x = re.sub(':','',x)
                    x = re.sub('<.+>','',x)
                    
                    try:
                        ipaSentence += word[x.lower()]
                        ipaSentence += " "
                    except KeyError:
                        keyErrors.write("KeyError with: " + x.lower() + "\n")
                        continue

                outFileOrig.write('\n')                

                newChunks = sententialRules(ipaSentence)
                ipaSentence = ""

                for chunk in newChunks:
                    ipaSentence += chunk
                    ipaSentence += " "
                
                newChunks = ipaSentence.split()
                ipaSentence = ""
                for chunk in newChunks:
                    ipaSentence += chunk
                    ipaSentence += " "
                # Remove trailing whitespace
                ipaSentence = ipaSentence.rstrip()
                # Calculate phonemes per word
                ipaWords = ipaSentence.split()
                phonemesInWord = 0
                for ipaWord in ipaWords:
                    phonemesInWord += len(ipaWord)
                # Number of original words is the length of the "words" variable beyond the first
                # part that indicates the speaker(i.e. *INV:)
                globals()["phonemesPerWord"].append(float(float(phonemesInWord) / float(len(words[1:]))))
               
                if verbose == 1:
                        print ipaSentence
                if len(ipaSentence) > 0:
                    outFile.write(ipaSentence + '\n')
                    globals()["numUtterances"] += 1
                #file.write(ipaSentence + '\n')

        #file.close()
    outFile.close()
    keyErrors.close()
    
    if verbose == 1:
        statisticsFile = open("statistics.txt", 'w')
        statisticsFile.write("Number of utterances: " + str(globals()["numUtterances"]) + "\n")
        statisticsFile.write("Number of words by tokens: " + str(globals()["numWords"]) + "\n")
        statisticsFile.write("Number of words by type: " + str(len(word)) + "\n")
        averageWordsPerUtterance = float(float(globals()["numWords"]) / float(numUtterances))
        statisticsFile.write("Words per utterance on average: " + str(averageWordsPerUtterance) + "\n")
        averagePhonemesPerWord = float(float(sum(globals()["phonemesPerWord"])) / float(len(globals()["phonemesPerWord"])))
        statisticsFile.write("Phonemes per word on average: " + str(averagePhonemesPerWord))
    
        statisticsFile.close()
    
if __name__ == "__main__":
    main()
    
