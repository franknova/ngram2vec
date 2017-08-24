from docopt import docopt
from representations.matrix_serializer import save_count_vocabulary
from sys import getsizeof


def main():
    args = docopt("""
    Usage:
        corpus2vocab.py [options] <corpus> <output>
    
    Options:
        --ngram NUM              Ngram [default: 1]
        --memory_size NUM        Memory size available [default: 8.0]
        --min_count NUM          Ignore words below a threshold [default: 10]
    """)

    print "corpus2vocab"
    ngram = int(args['--ngram'])
    memory_size = float(args['--memory_size']) * 1000**3
    min_count = int(args['--min_count'])
    vocab = {}
    reduce_thr = 1
    memory_size_used = 0 # size of memory used by keys & values in dictionary (not include dictionary itself) 

    with open(args['<corpus>']) as f:
        token_num = 0
        print str(token_num/1000**2) + "M tokens processed."
        for line in f:
            print "\x1b[1A" + str(token_num/1000**2) + "M tokens processed."
            tokens = line.strip().split()
            token_num += len(tokens)
            for pos in xrange(len(tokens)):            
                for gram in xrange(1, ngram+1):
                    token = getNgram(tokens, pos, gram)
                    if token is None :
                        continue
                    if token not in vocab :
                        memory_size_used += getsizeof(token)
                        vocab[token] = 1
                        if memory_size_used + getsizeof(vocab) > memory_size * 0.8:
                            reduce_thr += 1
                            vocab_size = len(vocab)
                            vocab = {w: c for w, c in vocab.iteritems() if c >= reduce_thr}
                            memory_size_used *= float(len(vocab)) / vocab_size
                    else:
                        vocab[token] += 1

    vocab = {w: c for w, c in vocab.iteritems() if c >= min_count}
    vocab = sorted(vocab.iteritems(), key=lambda item: item[1], reverse=True)
    save_count_vocabulary(args['<output>'], vocab)
    print "number of tokens: " + str(token_num)
    print "vocab size: " + str(len(vocab))
    print "low-frequency threshold: " + str(min_count if min_count > reduce_thr else reduce_thr)
    print "corpus2vocab finished"


def getNgram(tokens, pos, gram): #uni:gram=1  bi:gram=2 tri:gram=3
    if pos < 0:
        return None
    if pos + gram > len(tokens):
        return None
    token = tokens[pos]
    for i in xrange(1, gram):
        token = token + "@$" + tokens[pos + i]
    return token


if __name__ == '__main__':
    main()
