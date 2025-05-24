import os
import csv

punct = "~`!@\"#№;$%^:?&()_+=\\|/,.<>\'[]{}"
excl = {"PRO": "PRON", "NUM": "NUM", "persn": "PROP", "patrn": "PROP", "famn": "PROP", "geo": "PROP", "abbr": "PROP"}
digs = "234567890"

def get_filenames(filenames_file):
    with open(filenames_file, "r") as ff:
        filenames = ff.readlines()
    return filenames

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
                wordlist.append([word, "1"])
    return wordlist

def make_wordlist(wordlist, wordlist_filename):
    with open(wordlist_filename, "w") as fwl:
        writer = csv.writer(fwl, delimiter="\t")
        writer.writerows(wordlist)

def run_parser(parser_filename):
    exec(open(parser_filename).read())

def get_lemma(analysis):
    lemma = ""
    length = len(analysis)
    if length < 5:
        return ""
    analysis = analysis[3:]
    analysis = analysis[:analysis.find(">")]
    length = len(analysis)
    got_gr = False
    for i in range(4, length, 1):
        if got_gr:
            break
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
            got_gr = True
    return lemma    

def get_lemmas(parsed_final_filename):
    lemmas = []
    with open(parsed_final_filename, "r") as pff:
        analyses = pff.readlines()
    for analysis in analyses:
        lemma = get_lemma(analysis)
        lemmas.append(lemma)
    return lemmas

def write_fin(lemmas, out_filename_sg, out_filename_tot):
    s = " ".join(lemmas)
    with open(out_filename_sg, "w") as fsg:
        fsg.write(s)
        print(f"SAVED TO {out_filename_sg}")
    with open(out_filename_tot, "a") as ftot:
        ftot.write(s + "\n")

def parse_file(in_filename, wordlist_filename, parser_filename, parsed_final_filename, out_filename_sg, out_filename_tot):
    wordlist = read_init(in_filename)
    make_wordlist(wordlist, wordlist_filename)
    run_parser(parser_filename)
    lemmas = get_lemmas(parsed_final_filename)
    write_fin(lemmas, out_filename_sg, out_filename_tot)

def main():
    filenames_file = "../../filenames_list.txt"
    filenames = list(reversed(get_filenames(filenames_file)))
    # i = 0
    for filename in filenames:
        # if i < 1130:
            # i += 1
            # continue
        if len(filename) < 3:
            # i += 1
            continue
        in_filename = "../../adyghe/" + filename.strip()
        wordlist_filename = "../wordlist_full.csv"
        parser_filename = "analyze_adyghe.py"
        parsed_final_filename = "../wordlist.csv-parsed-final.txt"
        out_filename_sg = "../../adyghe_preparsed/" + "LEM_BAG_" + filename.strip()
        out_filename_tot = "../../TOT_LEM_BAG.txt"
        parse_file(in_filename, wordlist_filename, parser_filename, parsed_final_filename, out_filename_sg, out_filename_tot)
        print(f"PARSED {filename}")
        # i += 1

if __name__ == '__main__':
    main()