from tqdm import tqdm
import os.path

def is_good(in_folder, out_folder, name, thr):
    in_filename = in_folder + name
    out_filename = out_folder + "LEM_BAG_" + name
    with open(in_filename, "r") as fin:
        lines = fin.readlines()
        in_text = " ".join(lines)
    with open(out_filename, "r") as fout:
        lines = fout.readlines()
        if len(lines) > 1:
            print(f"{out_filename} BEHAVING STRANGELY: MORE LINES")
        out_text = " ".join(lines)
    in_tokens_q = len(in_text.split())
    out_tokens_q = len(out_text.split())
    if in_tokens_q == 0:
        print(f"{in_filename} IS EMPTY")
        return False
    ratio = out_tokens_q / in_tokens_q
    if ratio > 1:
        print(f"{out_filename} BEHAVING STRANGELY: RATIO > 1")
    elif ratio > thr:
        return True
    return False

in_folder = "adyghe/"
out_folders = ["adyghe_preparsed_1/", "adyghe_preparsed_2/", "adyghe_preparsed_3/", "adyghe_preparsed_4/", "adyghe_preparsed_questionable/", "adyghe_preparsed_5/"]
good, bad = [], []
ok_exists = {}
thr = 0.83

with open("filenames_list.txt", "r") as f:
    filenames = f.readlines()

for name in tqdm(filenames):
    name = name.strip()
    for out_folder in out_folders:
        out = out_folder + "LEM_BAG_" + name
        if not os.path.exists(out):
            continue
        if is_good(in_folder, out_folder, name, thr):
            good.append(out_folder + "LEM_BAG_" + name)
            ok_exists.setdefault(name, [])
            ok_exists[name].append(out_folder)
        else:
            bad.append(out_folder + "LEM_BAG_" + name)

for_embs = []
c = 0
for key, value in ok_exists.items():
    if len(value) > 0:
        c += 1
        folder = value[0]
        print("DEBUG", key, value, folder)
        end_name = folder + "LEM_BAG_" + key
        
        for_embs.append(end_name)

print(f"total good: {c}")
print(good[:5], "some good")
print(bad[:5], "some bad")

with open("lem_corpus_mini.txt", "w") as fout:
    for name in tqdm(for_embs):
        with open(name, "r") as fin:
            text = fin.read()
        fout.write(text + "\n")

print("done 1")

c2 = 0
for key, value in ok_exists.items():
    if "adyghe_preparsed_5/" in value:
        c2 += 1

print("last good", c2)