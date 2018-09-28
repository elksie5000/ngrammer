#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""N-gram counter submission
Author: David Elks
Date submitted: November 9, 2017

Notes:
    
The following script provides a mechanism for creating user-defined
ngrams in text documents.



It consists two classes:
    1) Document - a class which contains text, and from which n-grams, and 
    frequencies can be calculated.
    2) Corpus - This is a container for Documents and contains methods
    for loading text files and creating Documents. It has a set_model method
    to create/update ngrams/ngram counts across all documents within the 
    Corpus.
    It also contains a summarise method to calculate the average ngram
    co-occurence for a particular author.
    
    The use of the self.author_docs dictionary is designed to allow avoid 
    looping over the self.documents dictionary when calculating the 
    average and standard deviation for a particular author.
        
Regex compilation:
    The regular expressions to strip punctuation and handle newline or tab 
    characters was set as a constant at the top of the Document to avoid 
    repeated recompilation. 
    

Summarise/Calc_stats methods within Corpus:
    The summarise method builds a list of dictionaries of ngram frequencies
    based on a particular author within self.author_docs.
    The method then loops through each document and adds counts of every
    ngram found to a 'count' dictionary. 
    However, the consequence of this is that zero occurences is not listed.
    To correct for this, the first two lines of the calc_stats method
    calculates how many zero-values need to be appended.
    This was done to avoid extra testing for nulls and the fact that
    average and standard deviation calculations are not affected by the 
    location of these zero values.
    
Author names
    The insert_document method takes the author name from the first character
    of the filename. However, the function could also be used to add extra
    documents with other authors.
"""


import re, string, zipfile, glob
#zipfile is a standard module for extracting files from zip
#glob is used to find all the files with matching patterns extracted from zip

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
        output = """Document():\n
        Doc id: {0}\n
        Text: {1} {2}\n""".format(self.doc_id, self.text[:100], "...")
        if self.ngrams:
            output += """N-grams: {0} {2}\n
        N-gram freqs: {1} {2}""".format(self.ngrams[:5],
                                        str(self.ngram_freq)[:100], "...")
        return output
    
    
    def preprocess_document(self, word_ngrams):
        """Strip punctuation when word_ngrams is True,
        else return string"""
        self.word_ngrams = word_ngrams
        strng = self.text
        #strng = strng.lower() - 
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
    documents and to summarise by defined author.
    """
    
    def __init__(self):
        self.documents = {}
        self.summary = {}
        self.doc_count = 0
        self.author_docs = {}
 
    def __str__(self):
        output = "Corpus()\nAuthor \t\tNumber of documents"
        total = 0
        for k in self.author_docs.keys():
            count = len(self.author_docs[k])
            output += "\n{0}: \t\t{1}".format(k,
                       str(count))
            total += count
        output += "\nTotal: \t\t{0}".format(total)
        if self.summary:
            output += self.print_summary()
        return output

    def load_corpus(self, path= None, exclusion_list=None):    
        """Returns a Corpus of Document objects based sample texts.
        Variables:
        path : path to folder of files
        exclusion_list: a list of files to be excluded from inclusion
        in corpus."""

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
                    counts[k]['frequency'].append(doc.get(k, 0))
                    counts[k]['total_freq'] += doc.get(k, 0)
                    counts[k]['num_ngrams'].append(total_ngrams)
                else:
                    counts[k] = {'frequency': [doc.get(k, 0)], 
                                "total_freq": doc.get(k, 0),
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
    
    def print_summary(self):
        """Outputs results of summary method for standard output."""
        output = "\n\n"
        for author in self.summary.keys(): 
            output += "Author: {0}\n---------\n".format(author)
            output += "ngram,\t\t av_occurence,\t\tstd_deviation\n"
            for k in self.summary[author].keys():
                output += ('"{0}",\t\t{1},\t\t{2}\n'.format(k, 
                           self.summary[author][k][0], 
                           self.summary[author][k][1]))
        return output
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
    return sums ** .5



#sample usage

z = zipfile.ZipFile("texts.zip")
z.extractall()

corpus = Corpus()
#Exclusion_list is a list of filenames to ignore from loaded zipfile
corpus.load_corpus(exclusion_list=["readme.txt"])
#Set the model to 4-char-grams
corpus.set_model(4, False)

#Return a dict of the most common num ngrams for an author
#The author name is taken to be the first letter of the filename
results_a = corpus.summarise('A', num=20)
results_b = corpus.summarise('B', num=20)
results_c = corpus.summarise('C', num=20)


#Eyeball the output for the corpus
print(corpus) #See sample output below

"""Looking over differences between the average ngram occurences for C, the 
mystery document, and the two labelled collections, it would appear there
is more commonality between Author B than Author A. The best parameters
would appear to be for two-word ngrams, and four-character ngrams.

A second method involved calculating the Eucldiean distance between the 
average occurences of a set of the most-frequently occurring ngrams bewteen
one of the sample collections and the single document.

The distance was calculated with a model which created n-grams of up to 20
words or characters in length. 

In 10 separate tests where Euclidean distances from C were both
non-zero, A was judged closer to C 2 times, while 
B was ranked closer on 8 occasions.

Conclusion: The document 'C' appears on evidence provided by ngram analysis
to have been written by author 'B'.

"""


print("""Calculating Euclidean distances average occurence of ngrams in C and
between collections A and B. Nested loop will run over n-length ngrams between
1 and 20, and run over word and character ngrams.""")


results = {"A": 0, "B": 0}
non_zero_tests = 0

for boolean in [True, False]:
    for n in range(1, 21):
        corpus.set_model(n, boolean) 
        
        results_a = corpus.summarise('A', 20)
        results_b = corpus.summarise('B', 20)
        results_c = corpus.summarise('C', 20)
        
        distancea_c = compute_distance(results_a, results_c)
        distanceb_c = compute_distance(results_b, results_c)
        
        if (distancea_c and distanceb_c) == 0:
            break
        non_zero_tests += 1
        if distancea_c < distanceb_c:
            results["A"] += 1
        else:
            results["B"] += 1
        
        print(str(n)+"-length", "Word ngrams" if boolean else "Char ngrams")
        print("Sample ngram: ", corpus.documents[0].ngrams[1])
        print("A to C: ", round(distancea_c, 2))
        print("B to C: ", round(distanceb_c, 2), "\n")
        



print("""In {0} separate tests where Euclidean distances from C were both
non-zero, A was judged closer to C {1} times, while 
B was ranked closer on {2} occasions.
        """.format(non_zero_tests, results['A'], results['B']))


"""
SAMPLE OUTPUT
-------------
Corpus()
Author          Number of documents
A:              6
B:              6
C:              1
Total:          13

Author: A
---------
ngram,           av_occurence,          std_deviation
"_, t, h, e",           81.67,          17.37
"t, h, e, _",           69.0,           14.51
"a, n, d, _",           48.0,           12.27
"_, a, n, d",           45.83,          12.28
"_, t, o, _",           41.17,          8.03
"_, o, f, _",           40.17,          6.31
"_, y, o, u",           33.17,          6.91
"h, a, t, _",           31.0,           8.27
"i, n, g, _",           30.0,           4.76
",, _, a, n",           29.17,          10.35
"_, t, h, a",           27.5,           9.22
"t, h, a, t",           25.67,          8.4
"", _, _, "",           23.33,          16.07
"h, i, s, _",           23.0,           8.54
"_, i, n, _",           22.33,          4.78
"_, w, a, s",           21.0,           9.92
"w, a, s, _",           19.5,           9.18
"., ", _, _",           19.33,          12.15
"t, h, e, r",           19.0,           10.13
"_, f, o, r",           19.0,           7.55
Author: B
---------
ngram,           av_occurence,          std_deviation
"_, t, h, e",           138.67,         16.02
"t, h, e, _",           116.33,         18.99
"a, n, d, _",           71.17,          6.28
"_, a, n, d",           69.17,          6.64
"_, o, f, _",           49.67,          7.61
"_, t, o, _",           39.0,           7.79
"_, w, a, s",           37.67,          8.65
"i, n, g, _",           37.0,           11.6
"w, a, s, _",           36.5,           8.85
",, _, a, n",           33.33,          7.95
"h, a, t, _",           31.5,           7.34
"d, _, t, h",           30.83,          3.34
"n, _, t, h",           30.33,          7.09
"_, t, h, a",           29.5,           8.3
"_, i, n, _",           28.83,          6.36
"t, h, a, t",           27.33,          6.94
"h, i, s, _",           26.83,          10.07
"e, r, e, _",           24.67,          4.99
"_, T, h, e",           23.0,           9.07
"f, _, t, h",           21.33,          5.15
Author: C
---------
ngram,           av_occurence,          std_deviation
"_, t, h, e",           119.0,          0.0
"t, h, e, _",           94.0,           0.0
"a, n, d, _",           71.0,           0.0
"_, a, n, d",           62.0,           0.0
"_, t, o, _",           48.0,           0.0
"_, o, f, _",           47.0,           0.0
",, _, a, n",           36.0,           0.0
"i, n, g, _",           35.0,           0.0
"_, y, o, u",           32.0,           0.0
"n, _, t, h",           27.0,           0.0
"t, h, e, r",           25.0,           0.0
"_, t, h, a",           23.0,           0.0
"_, i, n, _",           23.0,           0.0
"y, o, u, _",           23.0,           0.0
"h, a, t, _",           22.0,           0.0
"f, _, t, h",           21.0,           0.0
"_, a, s, _",           20.0,           0.0
"_, w, i, t",           20.0,           0.0
"w, i, t, h",           20.0,           0.0
"h, e, r, e",           20.0,           0.0

Calculating Euclidean distances average occurence of ngrams in C and
between collections A and B. Nested loop will run over n-length ngrams between
1 and 20, and run over word and character ngrams.
1-length Word ngrams
Sample ngram:  certain
A to C:  43.91
B to C:  51.62 

2-length Word ngrams
Sample ngram:  certain, selection
A to C:  9.13
B to C:  8.05 

1-length Char ngrams
Sample ngram:  _
A to C:  272.14
B to C:  112.36 

2-length Char ngrams
Sample ngram:  _, c
A to C:  118.56
B to C:  59.83 

3-length Char ngrams
Sample ngram:  _, c, e
A to C:  79.38
B to C:  51.49 

4-length Char ngrams
Sample ngram:  _, c, e, r
A to C:  58.62
B to C:  34.63 

5-length Char ngrams
Sample ngram:  _, c, e, r, t
A to C:  39.73
B to C:  33.18 

6-length Char ngrams
Sample ngram:  _, c, e, r, t, a
A to C:  16.24
B to C:  14.88 

7-length Char ngrams
Sample ngram:  _, c, e, r, t, a, i
A to C:  6.91
B to C:  7.7 

8-length Char ngrams
Sample ngram:  _, c, e, r, t, a, i, n
A to C:  6.96
B to C:  5.2 

In 10 separate tests where Euclidean distances from C were both
non-zero, A was judged closer to C 2 times, while 
B was ranked closer on 8 occasions.
        
"""