import sys
import itertools
import numpy as np
from collections import defaultdict

import spacy

import frontend



# Should be in a struct, but I moved it around when struggling with a segfault.
nlp = None
freq_dict = defaultdict(int)


def initialize_freq_dict():
    global freq_dict
    for l in file("ke/count_1w_lemmatized.txt"):
        w, c = l.strip().split("\t")
        freq_dict[w] += int(c)


def initialize():
    global nlp

    sys.stderr.write("loading spacy model...\n")
    nlp = spacy.load('en')
    sys.stderr.write("spacy model loaded.\n")

    initialize_freq_dict()


def rank_tokens(nlp, sent):
    freqs = [freq_dict.get(token.lemma_.lower(), 0) for token in sent]

    # smaller is better
    def score(token, freq):
        if freq == 0:
            sc = 1e9 # lame
        else:
            sc = freq
            tag = token.tag_
            if tag in ("NN", "NNP"):
                sc //= 10
            if tag in ("NNS", "NNPS"):
                sc //= 5
            if tag.startswith("V"): # verb
                sc *= 2
            if tag.startswith("W"): # wh-pronoun, wh-adverb
                pass # no-op, they are frequent anyway
        return sc

    scores = [(score(token, freq), freq, token) for (token, freq) in zip(sent, freqs)]

    ranking = sorted(scores)
    return ranking


def process_isolated_sent(nlp, sent):
    ranking = rank_tokens(nlp, sent)
    # print " ".join(map(lambda (s, f, t): "(%d %s %d)" % (s, str(t), f), ranking))
    ranking = ranking[:3]

    # print " ".join(map(lambda (s, f, t): "(%d %s %d)" % (s, str(t), f), ranking))

    best_token = ranking[0][2] # tuple of (score, frequency, token), that's why the [2]
    # print frontend.render(sent, positions_to_bold=[best_token.i])
    return best_token


# Returns a list of spacy Tokens.
def backend(items):
    rankings = []
    for item in items:
        sent = nlp(item)
        ranking = rank_tokens(nlp, sent)
        rankings.append(ranking)

    keywords = []
    extracted_lemmata = set()
    for ranking in rankings:
        extracted_keyword = None
        for score, frequency, token in ranking:
            if token.lemma_ not in extracted_lemmata:
                extracted_keyword = token
                break
        if extracted_keyword is None:
            extracted_keyword = ranking[0][2] # no chance to obey uniqueness

        extracted_lemmata.add(extracted_keyword.lemma_)
        keywords.append(extracted_keyword)
    return keywords


# Extracts relevant information from list of spacy tokens.
def tokens_to_dicts(keyword_tokens):
    return [{ "token": unicode(token), "lemma": token.lemma_} for token in keyword_tokens]


# Items as in list of bullet point items.
# Isolated as in each bullet point is processed individually, so e.g. no deduplication.
def backend_isolated(items):
    keywords = []
    for item in items:
        sent = nlp(item)
        extracted_token = process_isolated_sent(nlp, sent)
        keywords.append(extracted_token)
    return keywords


# TODO two calls to nlp(item), lame.
def frontend_render(items):
    keyword_tokens = backend(items)
    html_lines = []
    for token, item in zip(keyword_tokens, items):
        sent = nlp(item)
        html_lines.append("<p>\n" + frontend.render(sent, positions_to_bold=[token.i], show_icon=True) + "\n</p>\n")
    return "".join(html_lines)


def process_isolated_lines():
    for line in sys.stdin:
        line = line.decode('utf-8').strip()
        sent = nlp(line)
        # print " ".join(str(token)+"/"+str(token.tag_) for token in sent)
        extracted_token = process_isolated_sent(nlp, sent)
        print "<p>\n" + frontend.render(sent, positions_to_bold=[extracted_token.i], show_icon=True) + "\n</p>\n"


def main():
    initialize()

    process_isolated_lines()


if __name__ == "__main__":
    main()
