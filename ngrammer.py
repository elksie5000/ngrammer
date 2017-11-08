#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, string, zipfile, glob


class Document(object):
    """Represents a document used by the Corpus class.

    Public attributes:
    text: container for text
    word_ngrams: boolean used in create_ngrams method to create
                 words (True) or char-ngrams (False)
    ngram_len = defines length of returned ngrams (in words or chars)
    ngram_freq = dict of frequency counts for ngrams in document
    ngram_list = list of ngrams
    """
    #Modify punctuation to stop removal of hyphens, but include smart quotes
    PUNCT = (string.punctuation).replace("-", "") + "’‘“”"
    #Compile regexes for words and chars and set as constant
    WORD_REGEX = re.compile('[%s]' % re.escape(PUNCT))
    CHAR_REGEX = re.compile('[%s]' % re.escape("\r\n\t"))
    
    def __init__(self, text, doc_id):
        self.text = text
        self.doc_id = doc_id
        self.ngram_len = 0
        self.word_ngrams = False
       
    
    def __str__(self):
           return str(self.ngrams)
    
    
    def preprocess_document(self, word_ngrams):
        """Strip punctuation when word_ngrams is True,
        else return lower case string"""
        self.word_ngrams = word_ngrams
        strng = self.text
        strng = strng.lower()
        if self.word_ngrams: 
               strng_no_punc = self.WORD_REGEX.sub('', strng).split()
               #Strip hyphens at end of words
               strng_no_punc = (s.strip('-') for s in strng_no_punc)
               #Remove double hyphens used in Gutenberg files
               strng_no_punc = (s.replace("--", " ") for s in strng_no_punc)
               #Recreate string
               self.text = " ".join(strng_no_punc)
        else:
               strng = self.CHAR_REGEX.sub(" ", strng)
               self.text = strng
        
    
    def create_ngrams(self, n, t):
        """Generate ngrams from t with n length.
        Boolean attribute self.word_ngrams provides switch
        between word (True), or character (False)"""
        self.ngrams = ""
        t = t.replace(" ", "_")
        if self.word_ngrams:
            t = t.split("_") 
        ngrams = [", ".join(t[i:i+n]) for i in range(len(t)-n+1)]
        return ngrams
        
    
    def count_freq(self):
        """Generate dictionary with frequency of ngrams"""
        freq  = {}
        for n in self.ngrams:
            freq[n] = freq.get(n, 0) + 1
        return freq
    
    def set_ngrams(self, ngram_len):
        """Wrapper function to create and count ngrams of n-length"""
        self.ngrams = self.create_ngrams(ngram_len, self.text)
        
        self.ngram_freq = self.count_freq()
    
    
class Corpus:
    """Container class to hold Documents, and provides methods to insert 
    documents and to summarise by defined author
    """


    def __init__(self):
        self.documents = {}
        self.summary = {}
        self.doc_count = 0
        self.author_docs = {}

    
    def __str__(self):
           output = "Corpus()\nAuthor \t\tNumber of documents"
           total = 0
           for k in self.documents.keys():
               count = len(self.documents[k])
               output += "\n{0}: \t\t{1}".format(k,
                         str(count))
               total += count
           output += "\nTotal: \t\t{0}".format(total)
           return output

    def load_corpus(self, path= None, exclusion_list=None):    
        """Returns a Corpus of Document objects based sample texts.
        Variables:
        path : path to folder of files"""

        files_to_load = glob.glob("*")
        for file in files_to_load:
            if (".txt" in file) and (file not in exclusion_list):
                with open(file, 'r', encoding="utf-8") as f:
                    text = f.read()
                    author_id = file[:1]
                    corpus.insert_document(text, author_id)
        return corpus
    
    def insert_document(self, text, author):
        """This is a wrapper function takes a text file, instantiates a 
        Document object"""
        doc = Document(text, self.doc_count)
        self.documents.update({self.doc_count: doc})
        #Create/update dictionary to key on author        
        if author not in self.author_docs.keys():
            self.author_docs.update({author: [self.doc_count]})
        else:
            self.author_docs[author].append(self.doc_count)
        self.doc_count += 1
    
    
    def set_model(self, ngram_len, word_ngrams):
        """Creates/updates ngrams and freq. counts for every Document
        in corpus"""
        for i in range(self.doc_count):
            self.documents[i].preprocess_document(word_ngrams)
            self.documents[i].set_ngrams(ngram_len)
            
    def calc_stats(self, lst, num_docs):
               """Returns calculates mean and standard deviation
               for a list of non-zero frequency counts"""
               
               zeroes = [0]*(num_docs - len(lst))
               result_lst = lst + zeroes
               avg = mean(result_lst)
               ss = sum_squares(result_lst, avg)
               std = stdev(ss, len(result_lst))
               return round(avg, 2), round(std, 2)
           
            
    def summarise(self, author, num=20):
        """Returns the average ngram occurence and std. deviation for 
        the top n-occurring ngrams for a collection of writings by an
        author."""
        
        doc_ngrams = [self.documents[d].ngram_freq for d in self.author_docs[author]]
        num_documents = len(self.author_docs[author])
        counts = {}
        #Loop through doc_ngrams and add counts to list
        for doc in doc_ngrams:
            #Calculate total number of ngrams in document
            total_ngrams = sum(v for v in doc.values()) #Number of unique
                                                         #ngrams in document
            for k, v in doc.items():
                if k in counts.keys():
                    counts[k]['frequency'].append(doc.get(k,0))
                    counts[k]['total_freq'] += doc.get(k,0)
                    counts[k]['num_ngrams'].append(total_ngrams)
                else:
                    counts[k] = {'frequency': [doc.get(k,0)], 
                                "total_freq": doc.get(k,0),
                                'num_ngrams': [total_ngrams]}
        
        #Sort the dictionary on total_freq to return top n-occuring keys
        top_ngram_keys = sorted(counts, 
                                key=lambda x: counts[x]['total_freq'], 
                                reverse=True)[:num]
        #Then calculate mean and standard deviation on this subset.
        result = {k: self.calc_stats(counts[k]['frequency'], 
                                     num_documents) for k in top_ngram_keys}
        
        
        #Insert summary into dictionary
        self.summary.update({author: result })
        return result
    
def mean(lst):
    return sum(l for l in lst) / len(lst)


def sum_squares(lst, mean):
    return sum((x-mean)**2 for x in lst)


def stdev(ss, n):
    return (ss/n)**0.5 


def compute_distance(a, b):
    """Compute the Euclidean distance two authors
    based on the average ngram frequencies of ngrams that exist in both."""
    sums = 0
    for key in a.keys():
        if key in b.keys():
            sums += pow(a[key][0] - b[key][0], 2)
    return sums **.5



    

z = zipfile.ZipFile("texts.zip")
z.extractall()

corpus = Corpus()
corpus.load_corpus(exclusion_list=["readme.txt"])
corpus.set_model(4, False)

#Return a dict of the most common num ngrams for an author
#The author name is taken to be the first letter of the filename
results_a = corpus.summarise('A', num=20)
results_b = corpus.summarise('B', num=20)
results_c = corpus.summarise('C', num=20)

print(results_a)

print(round(compute_distance(results_a, results_c)), 2)
print(round(compute_distance(results_b, results_c)), 2)







import time
results = {"A":0, "B":0}
non_zero_tests = 0

for boolean in [True, False]:
    for n in range(1, 21):
        
        print(str(n)+"-length", "Word ngrams" if boolean else "Char ngrams")
        corpus.set_model(n, boolean) 
        print("Sample: ", corpus.documents[0].ngrams[1])
        results_a = corpus.summarise('A', 20)
        results_b = corpus.summarise('B', 20)
        results_c = corpus.summarise('C', 20)
        distancea_c = compute_distance(results_a, results_c)
        
        distanceb_c = compute_distance(results_b, results_c)
        
        if distancea_c == distanceb_c == 0:
            continue
        non_zero_tests += 1
        if distancea_c < distanceb_c:
            results["A"] += 1
        else:
            results["B"] += 1
        time_end = time.clock()
        print("A to C: ", round(distancea_c, 2))
        print("B to C: ", round(distanceb_c, 2))
        




print("""In {0} separate tests, A was judged closer to C {1}
        times, while B was ranked closer on {2} occasions.
        """.format(non_zero_tests, results['A'], results['B']))


#Check whether the ngrams ngram_freq section is longer