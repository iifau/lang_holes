import subprocess
import os

punct = "~`!@\"#№;$%^:?&()_+=\\|/,.<>\'[]{}"
excl = {"PRO": "PRON", "NUM": "NUM", "persn": "PROP", "patrn": "PROP", "famn": "PROP", "geo": "PROP", "abbr": "PROP"}
digs = "234567890"

def read_init(in_filename):
    wordlist = []
    with open(in_filename, "r") as fin:
        content = fin.read()
        words = content.split()
        for word in words:
            word = word.lower()
            if len(word) > 0:
                if word[0] == "-":
                    word = word[1:]
                if len(word) > 0:
                    if word[-1] == "-":
                        word = word[:-1]
                if word.isdigit():
                    word = "зы"
                else:
                    for d in digs:
                        if d in word:
                            word = "зы"
                            break
                for sym in word:
                    if sym  in punct:
                        word = word.replace(sym, "")
                    elif sym == "Ӏ" or sym == "ӏ":
                        word = word.replace(sym, "I")
            if len(word) > 0:
                wordlist.append(word)
    return wordlist

def parse_one(word, wordlist_filename, parser_filename, parsed_final_filename):
    with open(wordlist_filename, "w") as fwl:
        fwl.write(word + "\t" + "1" + "\n")
    exec(open(parser_filename).read())
    with open(parsed_final_filename, "r") as fpf:
        analysis = fpf.read()
        length = len(analysis)
        if length < 5:
            return ""
        analysis = analysis[3:]
        analysis = analysis[:analysis.find(">")]
        length = len(analysis)
        for i in range(4, length, 1):
            if analysis[i - 4 : i + 1] == "lex=\"":
                lemma = ""
                j = i + 1
                curr = analysis[j]
                while curr != "\"":
                    lemma = lemma + curr
                    j += 1
                    curr = analysis[j]
                if "[" in lemma:
                    lemma = lemma.replace("[", "")
                if "]" in lemma:
                    lemma = lemma.replace("]", "")
            elif analysis[i - 3 : i + 1] == "gr=\"":
                gr = ""
                j = i + 1
                curr = analysis[j]
                while curr != "\"":
                    gr = gr + curr
                    j += 1
                    curr = analysis[j]
                for key, value in excl.items():
                    if key in gr:
                        lemma = value
        return lemma

def parse_file(in_filename, wordlist_filename, parser_filename, parsed_final_filename, out_filename_sg, out_filename_all):
    lemmatised = []
    init_text = read_init(in_filename)
    for word in tqdm(init_text):
        lemma = parse_one(word, wordlist_filename, parser_filename, parsed_final_filename)
        lemmatised.append(lemma)
    final_text = " ".join(lemmatised)
    with open(out_filename_sg, "w") as fout_1:
        fout_1.write(final_text)
    with open(out_filename_all, "a") as fout_2:
        fout_2.write(final_text + "\n")

directory = "../../adyghe/"
to_parse = os.listdir(directory)

for filename in to_parse:
    in_filename = "../../adyghe/" + filename
    wordlist_filename = "../wordlist_full.csv"
    parser_filename = "analyze_adyghe.py"
    parsed_final_filename = "../wordlist.csv-parsed-final.txt"
    out_filename_sg = "../../adyghe_preparsed/" + "LEM_" + filename
    out_filename_all = "../../LEM_all.txt"
    parse_file(in_filename, wordlist_filename, parser_filename, parsed_final_filename, out_filename_sg, out_filename_all)