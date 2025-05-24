from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
import numpy as np

def make_matrix(lemm_filename, min_df, max_df=None, token_pattern=None, use_idf=True):
    with open(lemm_filename, "r") as f:
        if token_pattern:
            vec = TfidfVectorizer(analyzer="word", min_df=min_df, token_pattern=token_pattern, use_idf=use_idf)
        else:
            vec = TfidfVectorizer(analyzer="word", min_df=min_df, use_idf=use_idf)
        vectorized = vec.fit_transform(f)
        return vectorized, vec.get_feature_names_out()

def apply_svd(A, k, output_folder):
    u, sigma, vt = svds(A, k)
    
    desc = np.flip(np.argsort(sigma))
    u = u[:,desc]
    vt = vt[desc]
    sigma = sigma[desc]
    
    assert sigma.shape == (k,)
    assert vt.shape == (k, A.shape[1])
    assert u.shape == (A.shape[0], k)
    
    with open(output_folder+ "/" + str(k) + "_sigma_vt.npy", "wb") as f:
        np.save(f, np.dot(np.diag(sigma), vt).T)
    with open(output_folder+ "/" +  str(k) + "_sigma.npy", "wb") as f:
        np.save(f, sigma)
    with open(output_folder+ "/" +  str(k) + "_u.npy", "wb") as f:
        np.save(f, u)
    with open(output_folder+ "/" +  str(k) + "_vt.npy", "wb") as f:
        np.save(f, vt)
    return np.dot(np.diag(sigma), vt).T

def make_dict(wordlist, lem_vecs, out_filename):
    d = {}
    for word, vec in zip(wordlist, lem_vecs):
        d[word] = vec
    np.savez(out_filename, **d)
    return d

token_pattern = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяilIӀӏ[0-9]PROPNUM"
lemm_filename = "lem_corpus_mini.txt"
output_folder = "svd_folder"
dict_filename  = "adyghe_dict.npz"

A, wordlist = make_matrix(lemm_filename, 1)
print(A.shape)
print(len(wordlist))

ind = -1
print(wordlist[ind], A[:, ind].toarray())

lem_vecs = apply_svd(A, 100, output_folder)
print(lem_vecs.shape)

dictionary = make_dict(wordlist, lem_vecs, dict_filename)
# print(dictionary)