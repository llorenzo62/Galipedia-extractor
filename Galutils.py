import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from collections import Counter, namedtuple
from pathlib import Path
import re,os
import pickle
import spacy

document=namedtuple('document',['title','category','user','text'])


#transpose a list of lists
transpose = lambda x: list(zip(*x))

#alphabetical chars
alphabet='A-ZÁÂÉÊÍÎÓÔÚÛÜÑÇ'
alphabet+=alphabet.lower()

def alpha_text(text,patt=''):
    '''
    removes any characters from the text that are not in
      alphabet+patt
    patt allows spaces, hyphens, or any other
      characters to be preserved from removal
    '''
    patt=alphabet+patt
    return re.sub(r'[^{}]'.format(patt),'',text)


def unravel(lst):
    '''
    Unravel an iterable of iterables up to any level
    lst: a list or set or tuple of lists/sets/tuples
    returns all values in one list
    '''
    ulst=[]
    for item in lst:
        if type(item) in [list,set,tuple]:
            ulst+=unravel(item)
        else:
            ulst.append(item)
    return ulst

def vectorice(iterable_list,thread_function,max_workers=None):

    '''
    given an iterable list with data, and a thread_function for process it
    set up a Pool for vectorice the function and returns the bunches in answer.
    max_workers stands for the number of threads launched.
    If max_workers is None (or not an integer) it is set to the number of CPUs detected
    '''

    from multiprocessing.pool import Pool

    max_workers=max_workers if isinstance(max_workers,int) else os.cpu_count()

    lR=list(range(0,len(iterable_list),len(iterable_list)//max_workers))
    params=[iterable_list[lR[i]:lR[i+1]] for i in range(len(lR)-2)]
    params.append(iterable_list[lR[-2]:])

    pool=Pool()
    answer=pool.map(thread_function,params)
    del pool

    return answer

def any_in(txt,pttrn=[':','.jpg','.png','*[']):
    '''returns True if any of pttr is in txt'''
    for pt in pttrn:
        if pt in txt:
            return True
    return False

def basic_stats(vals):
    '''
    basic statistics for a list of values
    returns a dictionary with the computed statistics
    '''

    columns=['mean','std','min','max','Sh','Q25','Q50','Q75']

    if not vals:
        return {key:val for key,val in zip(columns,[0]*len(columns))}

    vals=np.array(vals)
    columns=['mean','std','min','max','Sh','Q25','Q50','Q75']
    Sh=np.array(list(Counter(vals).values()))
    Sh=Sh/Sh.sum()
    res=[vals.mean(),vals.std(),vals.min(),vals.max(),-(Sh*np.log(Sh)).sum()]
    res+=list(np.quantile(vals,[0.25,0.5,0.75]))
    return {key:val for key,val in zip(columns,res)}

def list_product(s):
    '''
    returns the product of all values in a list
    '''
    if not s:
        return 0
    res=1
    for i in s:
        res*=i
    return res

def pickle_var(path,var=None):
    '''
    wrapper for pickle
    path is a path to a file
    if var is None is supposed you want load a pickled file so it returns
     pickle load
    else is supposed you want dump var to file
    '''
    #complex types as np.array or pandas DataFrame don't allow a simple comparison with None
    if type(var)==type(None):
         with open(path,'rb') as fich:
            return pickle.load(fich)

    else:
        with open(path,'wb') as fich:
            pickle.dump(var,fich)


def update_dict(base,upd):
    '''
    updates base dict with upd dict
    the update adds the key:value from upd to base if key is not in base
    if key exists in base then the update is key:(base value+upd value)
    '''
    for key,val in upd.items():
        base[key]=base.get(key,0)+val
    return base


def sent_tok(text,ends='[\?\!\*\#]',abrev=[('a.C.', 'aC.'),
                                            ('d.C.','dC.'),
                                            ('(n.','(nado en'),
                                            ('(m.','(morto en'),
                                            ('hab.','habitantes'),
                                            ('(ca.','circa'),
                                            ('(c.','(circa'),
                                            (' No. ',' nº '),
                                            (' op. ',' opus '),
                                            (' b.d. ',' banda deseñada '),
                                            (' || ',' # '),
                                          ]):
    '''
    custom sentence tokenizer
    '''


    def insert_EOL(txt,spans,post=False):
        '''
        insert an End of Line at the points in spans lists
        the spans list is a list of tuples [(start_chunk0, end_chunk0),....]
        chunk is a chunk of text between two insert_EOL
        '''
        ini0=fin=0
        sent=''
        for span in spans:
            ini,fin=span.span()
            ini=ini+1

            fin=fin+1 if post else fin-1

            sent+=txt[ini0:ini]+'\n'
            ini0=fin
        sent+=item[fin:] if fin else txt
        return sent

    if type(text)!=list:
        text=[text]
    res=[]
    for item in text:
        #preserve some common abreviatures
        for pat,rpl in abrev:
            item=item.replace(pat,rpl)

        #ellipsis can be tricky - could or be, or not, EOL without any other symbols
        sent=insert_EOL(item,re.finditer(r'… ?[A-ZÁÂÉÊÍÎÓÔÚÛÜÑÇ¿¡]',item),False)
        #preserve acronyms

        sent=insert_EOL(sent, re.finditer(r'\.\W+[A-ZÁÂÉÊÍÎÓÔÚÛÜÑÇ¿¡]',sent),False)
        sent=sent.replace('--','\n')
        sent=re.sub(r'={2,200}','\n',sent)

        res.append(re.sub(ends,'\n',sent).split('\n'))

    return ([clean for item in unravel(res) if (clean:=item.strip())])


class corpuscle():
    '''
    class for summarize a corpus and work with a language model
    params:
        lang: str, libpath.Path or spacy model for corpus language.
            Warning: Pickle floret models are unreliable, so it is advisable to reload corpuscle.lang with
            corpuscle.lang= spacy.load('path to model')
            using the class method set_lang which accepts a path to a spacy model

        bow: Bag of Words, dictionary {token:frequency}

        lemma: Bag of lemmas as lemmatized by the language model "lang" {lemma:frequency}

        tfidf: dictionary with {lemma:tfidf}

        propn: dictionary with Proper Nouns

        ptmc: Pandas Dataframe with the transition frequencies from one POS tag (row) to another POS tag  (column). The first row is "start", the start of the sentence and the first column is "end", the end of sentence.

        pp: Pandas DataFrame with the POS frequencies (columns) for each lemma (rows)
    methods:
        value: returns the tfidf sum. Can work with one sentence (returns a    number)  or a list of sentences (returns a list of numbers)
            sent: a string or a spacy Doc. If a string, "lang" is applied.
            exclude: list for explicit exclude tfidf keys (such stopwords)

        model_predict: given one sentence (str) returns a list of tuples [(token0,POS0,lemma0),...]. Each tuple contains (token, POS tagging, lemma) as given by "lang"
            sent: A preprocessed string with one sentence
            pos_exclude: A list of POS to exclude from result

        FreqPos: the frequencies of each POS tag for lemma0

        TransitionFreq: the frequencies of transition from and to pos
    '''
    def __init__(self,lang, bow=None, lemma=None, tfidf=None, propn=None, ptmc=None,pp=None):

        if type(lang) in [str,type(Path.cwd())]:
            self.set_lang(lang)
        else:
            self.lang=lang #spacy model associated
        self.bow=bow # BOW of corpus, dict
        self.lemma=lemma # BOW after lemmatization, dict
        self.tfidf=tfidf # tfidf for lemmas, dict
        self.propn=propn # tokens tagged as PROPN in corpuscle, dict
        self.ptmc=ptmc # markov transition matrix between POS tags, panda dataframe
        self.pp=pp # lemma POS frecuencie, panda dataframe

    def set_lang(self,path_to_model):
        self.lang=spacy.load(path_to_model)

    def value(self,sent,exclude=[]):
        '''
        exclude: list with POS tags to be excluded in computation
        '''

        keys=[key for key in self.tfidf if not key in exclude]

        if type(sent)==spacy.tokens.doc.Doc:

            return sum([self.tfidf[item.lemma_] if item.lemma_ in keys else 0 for item in sent])
        if type(sent)==str:
            return sum([self.tfidf[item.lemma_] if item.lemma_ in keys else 0 for item in self.lang(sent)])
        if type(sent)==list:
            if type(sent[0])==spacy.tokens.doc.Doc:
                res=[]
                for s in sent:
                    res.append(sum([self.tfidf[item.lemma_] if item.lemma_ in keys else 0 for item in s]))
                return  res
            elif type(sent[0]==str):
                res=[]
                for s in sent:
                     res.append(sum([self.tfidf[item.lemma_] if item.lemma_ in keys else 0 for item in self.lang(s)]))
                return res

    def model_predict(self,sent,pos_exclude=[]):
        if type(sent) == str:
            return [(i.text,i.pos_,i.lemma_) for i in self.lang(sent) if not i.pos_ in pos_exclude]
        elif type(sent)==list:
            res=[]
            for s in sent:
                res.append([(i.text,i.pos_,i.lemma_) for i in self.lang(s)])
            return res

    def FreqPos(self,lemma):
        '''
        returns relative freqs of POS tag assigned to lemma
        '''

        if type(self.pp)!=type(None) and lemma in self.pp.index:
            return self.pp.loc[lemma]


    def TransitionFreq(self, pos):
        '''
        returns a list with two Pandas' Series:
        the transition relative freqs from pos to any POS (pos--> POS[i])
        and the transition freqs from any POS to pos (POS[i]-->pos) or None if pos doesn't exists in row or column
        '''
        if type(self.ptmc)!=type(None):
            frompos=topos=None
            if pos in self.ptmc.columns:
                topos=self.ptmc[pos]
            if pos in self.ptmc.index:
                frompos=self.ptmc.loc[pos,:]
            return [frompos,topos]


def process_corpus(all_toks,exclude_pos=['PROPN','X','SYM','PUNCT'],MIN_DF=3):
    '''
    given a list with lists of tuples [[(token00,POS00,lemma00),...],[(token10,POS10,lemma10),...],...]
    so the len of the list is then number of sentences and the len of each inner list is the number of token of each sentence.
    returns the dictionaries:
        bow: Bag of words
        lemma: Bag of lemmas
        tfidf: tfidf values for lemmas
        propn: Bag of proper nouns, tokens with POS="PROPN"
    exclude_pos: list of POS to exclude from bow, lemma and tfidf
    MIN_DF: minimum document frequency to be in tfidf
    '''

    bow={}
    lemma={}
    df={}
    propn={}

    for s in all_toks:
        toks,pos,lem=transpose(s)
        bow=update_dict(bow,Counter([item for i,item in enumerate(toks) if not pos[i] in exclude_pos]))
        free_lem=[item.lower() for i,item in enumerate(lem) if not pos[i] in exclude_pos]
        lemma=update_dict(lemma,Counter(free_lem))
        df=update_dict(df,{k:1 for k in free_lem})
        propn=update_dict(propn,Counter([item for i,item in enumerate(toks) if pos[i]=='PROPN']))

    df={key:val for key,val in df.items() if val>MIN_DF and len(alpha_text(key))==len(key)}
    lemma={key:val for key,val in lemma.items() if key in df.keys() and len(alpha_text(key))==len(key)}
    bow={key:val for key, val in bow.items() if len(alpha_text(key))==len(key)}

    #### Normalize

    total=sum(list(bow.values()))
    bow={key:val/total for key,val in bow.items()}
    total=sum(list(lemma.values()))
    lemma={key:val/total for key,val in lemma.items()}
    total=len(all_toks)
    idf={key:np.log10(total/val) for key,val in df.items()}
    tfidf={key:val*lemma[key] for key,val in idf.items()}

    return bow,lemma,tfidf,propn
