from __future__ import print_function
import numpy as np
import scipy.sparse as sp
from sklearn.utils import shuffle
from sklearn.datasets import load_svmlight_file
import ujson
from common import ir, similarity, tsne
from docnade import DocNADE
from rsm import RSM
from nvdm import NVDM
from deepdocnade import DeepDocNADE
from vaenade import VAENADE
from dvae import DVAE


def load_data(input_file):
    npzfile = np.load(input_file)
    mat = sp.csr_matrix((npzfile['data'], npzfile['indices'],
                         npzfile['indptr']),
                        shape=tuple(list(npzfile['shape'])))
    return mat


def load_seq():
    # sub = 'reuters_seq'
    # sub = 'reuters_big_seq'
    sub = '20ng_seq'
    if sub == 'reuters_big_seq':
        split = 10000
        data = load_data('data/' + sub + '/data.npz')
        data_target = load_data('data/' + sub + '/data_lbl.npz')
        train = data[:-split]
        train_target = data_target[:-split]
        test = data[-split:]
        test_target = data_target[-split:]
        print("Reading sequence")
        with open('data/' + sub + '/seq_data', 'r') as f:
            data = ujson.load(f)
            train_seq = data[:-split]
            test_seq = data[-split:]
    else:
        train, train_target = load_svmlight_file('data/' + sub + '/train')
        test, test_target = load_svmlight_file('data/' + sub + '/test')
        with open('data/' + sub + '/seq_train', 'r') as f:
            train_seq = ujson.load(f)
        with open('data/' + sub + '/seq_test', 'r') as f:
            test_seq = ujson.load(f)
    with open('data/' + sub + '/meta_data', 'r') as f:
        dump = ujson.load(f)
        word2idx = dump['w2i']
        idx2word = dump['i2w']
    return (train, train_seq, train_target, test, test_seq, test_target,
            word2idx, idx2word)


def load_20ng():
    train = load_data('data/20ng/train_data.npz')
    train_target = np.load('data/20ng/train_labels.npy')
    validation = load_data('data/20ng/valid_data.npz')
    validation_target = np.load('data/20ng/valid_labels.npy')
    test = load_data('data/20ng/test_data.npz')
    test_target = np.load('data/20ng/test_labels.npy')
    train, train_target = shuffle(train, train_target)
    validation, validation_target = shuffle(validation, validation_target)
    test, test_target = shuffle(test, test_target)
    with open('data/20ng/vocab.txt', 'r') as f:
        voc = f.read().splitlines()
    input_dim = len(voc)
    idx2word = np.array(voc)
    word2idx = dict(zip(voc, range(0, input_dim)))
    return (train, train_target, validation, validation_target, test,
            test_target, idx2word, word2idx)


def load_reuters():
    train = load_data('data/reuters/train_data.npz')
    train_target = np.load('data/reuters/train_labels.npz')
    validation = load_data('data/reuters/valid_data.npz')
    validation_target = np.load('data/reuters/valid_labels.npz')
    test = load_data('data/reuters/test_data.npz')
    test_target = np.load('data/reuters/test_labels.npz')
    train, train_target = shuffle(train, train_target)
    validation, validation_target = shuffle(validation, validation_target)
    test, test_target = shuffle(test, test_target)
    return (train, train_target, validation, validation_target, test,
            test_target)


def evaluate_ir(queries):
    # intervals = [0.0002, 0.001, 0.004, 0.016, 0.064, 0.256]
    intervals = [0.00001, 0.00006, 0.00051, 0.004, 0.016, 0.064, 0.256]
    frac = np.array(intervals) * train.shape[0]
    prec = []
    for i in frac:
        subset = queries[:int(i+1)]
        prec.append(np.mean(subset))
    return prec


def dump(data, name):
    with open(name, 'wb') as f:
        ujson.dump(data, f)

# Load data-------------------------------------
# Bag of words vectors for NVDM and RSM.
# Sequence of word-indicies for DocNADE

# (train, train_seq, train_target, test, test_seq, test_target,
#  word2idx, idx2word) = load_seq()
# (train, train_target, validation, validation_target, test, test_target,
#  idx2word, word2idx) = load_20ng()

# (train, train_target, validation, validation_target, test, test_target)\
#         = load_reuters()

# Convert sparse bag of words to DocNADE sequences with randomized order.
# train_dn = []
# for i, doc in enumerate(train):
#     d = []
#     for idx, count in zip(doc.indices, doc.data):
#         for j in range(int(count)):
#             d.append(idx)
#     np.random.shuffle(d)
#     train_dn.append(d)

# valid_dn = []
# for i, doc in enumerate(validation):
#     d = []
#     for idx, count in zip(doc.indices, doc.data):
#         for j in range(int(count)):
#             d.append(idx)
#     np.random.shuffle(d)
#     valid_dn.append(d)

# test_dn = []
# for i, doc in enumerate(test):
#     d = []
#     for idx, count in zip(doc.indices, doc.data):
#         for j in range(int(count)):
#             d.append(idx)
#     np.random.shuffle(d)
#     test_dn.append(d)


# Use models.
# DocNADE
# dn = DocNADE(voc_size=train.shape[1])
# dn.restore('checkpoints/docnade_r2_p=485.ckpt')
# dn.restore('best_ckpt/docnade_20ng.ckpt')
# sim = similarity(train, test, train_target, test_target, dn)
# print(sim, np.mean(sim))
# dn.train(train_seq[100:], train_seq[:100])
# print(dn.closest_words("medical"))
# print(dn.perplexity(test_dn))
# queries = ir(train, test, train_target, test_target, dn, multi_label=True)
# dump(queris, 'docnade_q')
# print(evaluate_ir(queries))

# RSM
# rsm = RSM(input_dim=train.shape[1])
# rsm.restore('checkpoints/rsm_p=975.ckpt')
# rsm.train(train, max_iter=100)
# print(rsm.closest_word("medical"))
# print(rsm.perplexity(test, steps=1000))
# print(rsm.ir(train, test, train_target, test_target))

# NVDM
# nvdm = NVDM(input_dim=train.shape[1], word2idx=word2idx, idx2word=idx2word)
# nvdm.restore('best_ckpt/nvdm_20seq.ckpt')
# nvdm.train(train, test, alternating=False, learning_rate=0.0005, max_iter=10000,
#            batch_size=100)
# print(nvdm.closest_words("medical"))
# print(nvdm.perplexity(test))
# queries = ir(train, test, train_target, test_target, nvdm)
# print(evaluate_ir(queries))
# tsne(train, train_target, nvdm)
# sim = similarity(train, test, train_target, test_target, nvdm)
# print(sim, np.mean(sim), np.std(sim))

# DeepDocNADE
# ddn = DeepDocNADE(word2idx=word2idx, idx2word=idx2word, voc_size=train.shape[1])
# ddn.train(train, test, learning_rate=0.0005)
# ddn.restore('best_ckpt/deep_docnade_20ng.ckpt')
# ddn.restore('best_ckpt/deep_docnade_2l_20ng.ckpt')
# print(ddn.perplexity(test_seq, True, ensembles=1))
# print(ddn.perplexity(test_dn, True, ensembles=1))
# print(ddn.perplexity(valid_dn, True))
# queries = ir(train, test, train_target, test_target, ddn)
# print(evaluate_ir(queries))
# sim = similarity(train, test, train_target, test_target, ddn)
# print(sim, np.mean(sim))
# tsne(train, train_target, ddn)

# VAENADE
# vn = VAENADE(voc_dim=train.shape[1])
# vn.train(train, train_seq)
# vn.restore('checkpoints/vaenade_1g.ckpt')
# vn.restore('best_ckpt/vaenade_20ng.ckpt')
# sim = similarity(train, test, train_target, test_target, vn)
# print(sim, np.mean(sim), np.std(sim))
# tsne(train, train_target, vn)
# print(vn.perplexity(test, test_seq))
# queries = ir(train, test, train_target, test_target, vn)
#  print(evaluate_ir(queries))

# DVAE
# dvae = DVAE(voc_size=train.shape[1]) 
# dvae.train(train, test, learning_rate=0.0005)
