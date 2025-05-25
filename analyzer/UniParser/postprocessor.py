import re
import os.path

rxAna = re.compile('<ana [^<>]*>(?:</ana>)?')
rxPartsGloss = re.compile('parts="([^"]+)" +gloss="([^"]+)"')
rxBadAdv = re.compile('<ana[^<>]+[эо]-у" gloss[^<>]+></ana> *')
rxBadAnalyses = re.compile('<ana[^<>]*lex="шъомбгъуагъэ"[^<>]+></ana>')


def process_plus_glosses_ana(m):
    parts = m.group(1).split('-')
    glosses = m.group(2).split('-')
    if len(parts) != len(glosses):
        return 'parts="' + m.group(1) + '" gloss="' + m.group(2) + '"'
    elif len(glosses) > 1 and glosses[1] == 'STEM' and (parts[:2] == ['я', 'тэ'] or parts[:2] == ['я', 'нэ']):
        return 'parts="й-а' + m.group(1)[2:] + '" gloss="' + m.group(2) + '"'

    elif glosses[-1] == ['NEG', 'ADV'] and parts[-2][-1] == ['е', 'и', 'э']: 
        newendparts = parts[-2][:-1] + 'й-э' + parts[-1] 
        return 'parts="' + m.group(1)[:-2] + newendparts + '" gloss="' + m.group(2) + '"'

    sParts = ''
    sGlosses = ''
    for i in range(len(parts)):
        if '+' not in glosses[i]:
            sParts += '-' + parts[i]
            sGlosses += '-' + glosses[i]
            continue
        if parts[i] == 'я':
            sParts += '-я'
        elif parts[i] == 'ря':
            sParts += '-ря'
        elif parts[i] == 'е':
            sParts += '-й-э'
        elif parts[i] == 'о':
            sParts += '-у-э'
        elif parts[i] == 'шъо':
            sParts += '-шъу-э'
        elif parts[i] == 'мы':
            sParts += '-мы'
            
        # leave 'я'
        if glosses[i] == '3PL.P+POSS':
            sGlosses += '-3PL.P+POSS'

        elif glosses[i] == '3PL.IO+DAT':
            sGlosses += '-3PL.IO+DAT'

        # leave 'мы'
        elif glosses[i] == '2SG.ERG+NEG':
            sGlosses += '-2SG.ERG+NEG'

        # split standalone possessives
        elif glosses[i] == 'P.1SG+POSS':
            sGlosses += '-1SG.P-POSS'
            sParts += 'с-и'

        elif glosses[i] == 'P.2SG+POSS':
            sGlosses += '-2SG.P-POSS'
            sParts += 'у-и'

        elif glosses[i] == 'POSS+ORD':
            sGlosses += '-POSS-ORD'
            sParts += 'и-я'

        else:
            sGlosses += '-' + glosses[i].replace('+', '-')
            
    return 'parts="' + sParts.strip('-') + '" gloss="' + sGlosses.strip('-') + '"'


def process_plus_glosses(word):
    """
    Find all glosses with a plus inside. They correspond
    to one-phoneme affix sequences that are expressed by
    the same letter due to orthographic requirements.
    Replace the glosses and the morphemes.
    """
    return rxPartsGloss.sub(process_plus_glosses_ana, word)


def process_adv_glosses(word):
    """
    Remove the incorrectly split adverbialis suffixes if
    there is a correct variant.
    """
    if '-эу" gloss' in word or '-оу" gloss' in word:
        word = rxBadAdv.sub('', word)
    return word


def remove_bad_analyses(word):
    return rxBadAnalyses.sub('', word)


def transform_parsed_o(fnameIn, fnameOut):
    """
    Change the words containing an O back to the normal
    orthography (уэ -> о)
    """
    fIn = open(fnameIn, 'r', encoding='utf-8-sig')
    fOut = open(fnameOut, 'w', encoding='utf-8')
    rxWord = re.compile('^(.*>)([^<>]*</w>.*)', flags=re.DOTALL)
    for line in fIn:
        m = rxWord.search(line)
        if m is None:
            print('Error:', line)
            continue
        fOut.write(m.group(1) + m.group(2).replace('уэ', 'о'))
    fIn.close()
    fOut.close()

def transform_parsed_lar(fnameIn, fnameOut):
    """
    Change the words containing 'хьа', 'Iа' back to the original
    orthography (хьэ -> хьа), (Iэ -> Iа)
    """
    fIn = open(fnameIn, 'r', encoding='utf-8-sig')
    fOut = open(fnameOut, 'w', encoding='utf-8')
    rxWord = re.compile('^(.*>)([^<>]*</w>.*)', flags=re.DOTALL)
    for line in fIn:
        m = rxWord.search(line)
        if m is None:
            print('Error:', line)
            continue
        fOut.write(m.group(1) + m.group(2).replace('хьэ', 'хьа'))
        fOut.write(m.group(1) + m.group(2).replace('Iэ', 'Iа'))
    fIn.close()
    fOut.close()

def split_o_wordlist(wordlistName, unparsedName):
    """
    Read the word lists and write a list of unparsed words
    that contain an О character, replacing it with УЭ.
    Return the number of words written.
    """
    fAll = open(wordlistName, 'r', encoding='utf-8-sig')
    fUnparsed = open(unparsedName, 'r', encoding='utf-8-sig')
    freqDict = {}
    for line in fAll:
        if len(line) < 3:
            continue
        word_and_freq = line.strip().split('\t')
        if len(word_and_freq) == 2:
            word, freq = word_and_freq[0], word_and_freq[1]
        else:
            word = ""
            freq = word_and_freq[0]
        # word, freq = line.strip().split('\t') ЭТО БЫЛО
        freqDict[word] = int(freq)
    fAll.close()
    nOWords = 0
    fOutO = open('../wordlist-o.csv', 'w', encoding='utf-8-sig')
    fOutAll = open('../wordlist-unparsed-all.csv', 'w', encoding='utf-8-sig')
    for line in fUnparsed:
        line = line.strip()
        freq = 1 # БЫЛО freq = freqDict[line]
        fOutAll.write(line + '\t' + str(freq) + '\n')
        m = re.search('^(.*)о(у(?:т?и|б?а|рэ|шъ)?)$', line)
        if m is None:
            continue
        fOutO.write(m.group(1) + 'уэ' + m.group(2) + '\t' + str(freq) + '\n')
        nOWords += 1
    fOutO.close()
    fOutAll.close()
    return nOWords


def postprocess_parsed_wordlist(fnamesIn, fnameOut):
    """
    Unite the analyzed word lists obtained at different
    stages. Postprocess the entire analyzed word list and write
    the result to a new file.
    """
    fOut = open(fnameOut, 'w', encoding='utf-8')
    for fnameIn in fnamesIn:
        if os.path.exists(fnameIn):
            fIn = open(fnameIn, 'r', encoding='utf-8')
            for line in fIn:
                line = process_plus_glosses(line)
                line = process_adv_glosses(line)
                line = remove_bad_analyses(line)
                if '<ana' in line:
                    fOut.write(line)
            fIn.close()
    fOut.close()

def split_lar_wordlist(wordlistName, unparsedName):
    """
    Read the word lists and write a list of unparsed words
    that contain А after a letter denoting laryngeal sound (except palochka), replacing it with Э.
    Return the number of words written.
    """
    fAll = open(wordlistName, 'r', encoding='utf-8-sig')
    fUnparsed = open(unparsedName, 'r', encoding='utf-8-sig')
    freqDict = {}
    for line in fAll:
        if len(line) < 3:
            continue
        word_and_freq = line.strip().split('\t')
        if len(word_and_freq) == 2:
            word, freq = word_and_freq[0], word_and_freq[1]
        else:
            word = ""
            freq = word_and_freq[0]
        # word, freq = line.strip().split('\t') ЭТО БЫЛО
        freqDict[word] = int(freq)
    fAll.close()
    nLarWords = 0
    fOutLar = open('../wordlist-lar.csv', 'w', encoding='utf-8-sig')
    fOutAll = open('../wordlist-unparsed-all.csv', 'w', encoding='utf-8-sig')
    for line in fUnparsed:
        line = line.strip()
        freq = 1 # БЫЛО freq = freqDict[line]
        fOutAll.write(line + '\t' + str(freq) + '\n')
        m = re.search('^(.*хь|I|.+[^чтфлпцшк]I)(а)(.*)$', line)
        if m is None:
            continue
        fOutLar.write(m.group(1) + 'э' + m.group(3) + '\t' + str(freq) + '\n')
        nLarWords += 1
    fOutLar.close()
    fOutAll.close()
    return nLarWords

def rewrite_unparsed(fnameParsed, fnameUnparsedIn, fnameUnparsedOut):
    """
    Read the initial list of unparsed items and filter it, removing the
    words that were parsed on later stages.
    """
    fParsed = open(fnameParsed, 'r', encoding='utf-8-sig')
    parsedWords = set(re.findall('>([^<>\n]*)</w>', fParsed.read()))
    fParsed.close()
    unparsedInitial = 0
    unparsedFinal = 0
    fUnparsed = open(fnameUnparsedIn, 'r', encoding='utf-8-sig')
    fOut = open(fnameUnparsedOut, 'w', encoding='utf-8-sig')
    for line in fUnparsed:
        unparsedInitial += 1
        line = line.strip()
        if line not in parsedWords:
            fOut.write(line + '\n')
            unparsedFinal += 1
    fOut.close()
    fUnparsed.close()
    # print('Initially ' + str(unparsedInitial) + ' unparsed, final size: ' + str(unparsedFinal))


def finalize():
    """
    Filter and join all files after all stages of analysis have been performed.
    """
    transform_parsed_o('../wordlist.csv-parsed-o.txt', '../wordlist.csv-parsed-o-corrected.txt')
    transform_parsed_lar('../wordlist.csv-parsed-lar.txt', '../wordlist.csv-parsed-lar-corrected.txt')
    postprocess_parsed_wordlist(['../wordlist.csv-parsed-main.txt',
                                 '../wordlist.csv-parsed-o-corrected.txt',
                                 '../wordlist.csv-parsed-lar-corrected.txt',
                                 '../wordlist.csv-parsed-NtoV.txt'],
                                '../wordlist.csv-parsed-final.txt')
    rewrite_unparsed('../wordlist.csv-parsed-final.txt',
                     '../wordlist.csv-unparsed-main.txt',
                     '../wordlist.csv-unparsed-final.txt')


if __name__ == '__main__':
    finalize()
