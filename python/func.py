#%% Importing needed packages
import pandas as pd
import re

#
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer

#
from nltk import word_tokenize
from nltk.stem.isri import ISRIStemmer
from farasa.stemmer import FarasaStemmer
from nltk.stem import PorterStemmer

from wordcloud import WordCloud
import arabic_reshaper 
from bidi.algorithm import get_display

# %% Cleaning functions
def combine(list_of_text):

    '''Takes a list of text and combines them into one large chunk of text.'''
    combined_text = ' '.join(list_of_text)
    return combined_text

def word_count(text):
    return len(text.split())

def cleaning(verse):
    # for the Arabic version
    verse = re.sub("[ًًٌٌٍٍَُِّّْٰٓٓ]","",verse)
    verse = re.sub("[آ]","ا",verse)

    # for the English transelation
    verse = verse.lower()
    verse = re.sub("\[.*?\]","",verse)
    verse = re.sub("[(0-9)]","",verse)
    verse = re.sub("[-.,;:]","",verse)
    verse = re.sub("  "," ",verse)
    verse = verse.strip()

    return verse

def remove_basmalah(first_aya):
    first_aya = re.sub("بسم الله الرحمن الرحيم ", "", first_aya)
    
    return first_aya

# creating a function to add a basmalah at the begining of each chapter with verse_num = 0
def add_basmalah(quran, language):
    
    """This function will insert a 'basmalah' at the start of each chapter with verse_num = 0"""

    if language == "A":
        b = "بسم الله الرحمن الرحيم"
    elif language == "E":
        b = "in the name of allāh the entirely merciful the especially merciful"
    else:
        print("invalide value or language; 'A' for Arabic or 'E' for English")
    
    a = list(quran[quran.verse_num == 1].index)
    a.remove(0)
    
    for chapter, i in enumerate(a):
        quran.loc[i-0.5] = {"chapter_num":chapter + 2,"verse_num":0,"verse":b}
    
    quran.iloc[0].verse = b

    quran = quran.drop(index= quran[(quran.chapter_num == 9) & (quran.verse_num == 0)].index)
    quran = quran.sort_index().reset_index(drop= True)
    return quran

# %%
def word_cloud_generater(text,stopwords_list):
    # import arabic_reshaper 
    # from bidi.algorithm import get_display
    # from wordcloud import WordCloud

    stw=[]
    for i in stopwords_list:
        i = arabic_reshaper.reshape(i)
        i = get_display(i)
        stw.append(i)


    wc = WordCloud(stopwords=stw, background_color="white", colormap="Dark2",
               max_font_size=150, random_state=42, font_path="../font/times.ttf"
               )

    text = arabic_reshaper.reshape(text)
    text = get_display(text) 

    wc.generate(text)
    return(wc)
# %% Search engine
def stories_tag(quran,dicti):
    """tag the verses that are included in 'dicti'."""
    for tag, chapters_dict in dicti.items():
        for chapter, verses in chapters_dict.items():
            for i,sett in enumerate( quran[(quran.chapter_num == chapter) & (quran.verse_num.isin(verses))].tags):
                try:
                    quran.iloc[i]["tags"] = sett.add(tag)
                except:
                    quran.iloc[i]["tags"] = set({tag})

def tag_by_words_appearance(quran,tags_dictionary, stem= False):
    """tag each verse acording to the apearance of words"""

    if stem:

        for tag, lst in tags_dictionary.items():
            g = []
            for i in lst:
                g.append(FarasaStemmer().stem(i))
                if (i not in g):
                    g.append(i)
            tags_dictionary[tag] = g 
    
    for i in range(quran.shape[0]):
        for tag, lst in tags_dictionary.items():
            for word in lst:
                if bool(re.search(word, quran.verse.iloc[i])):
                    quran.tags.iloc[i].add(tag)
                    break


def search(quran,text, stem= False):
    
    resulted_columns = ["chapter_num", "verse_num", "verse", "tags"]
    df = pd.DataFrame(columns=resulted_columns)
    #c = 0
    
    
    words_lst = text.split()
    
    # do the stemming only once because it takes time
    if stem:
        # stemming the text
        stemed_text=FarasaStemmer().stem(text)
        
        # stemming the search words
        stemed_lst=[FarasaStemmer().stem(i) for i in words_lst]
    
    
    
    # searching for the complite text
    for i in range(quran.shape[0]):
        # check if the text matches a tag of the ith verse
        if (text in quran.tags.iloc[i]):
            df.loc[i] =  quran[resulted_columns].iloc[i]

        # check if the text appear in the ith verse
        if bool(re.search(text, quran.verse.iloc[i])):
            df.loc[i]= quran[resulted_columns].iloc[i]
            #c = c + 1 
        
        # are we searching for a stemmed version of the text    
        if stem:
            # check if stemmed text matches a tag of the ith verse
            if (stemed_text in quran.tags.iloc[i]):
                df.loc[i] =  quran[resulted_columns].iloc[i]

            # check if stemmed text appear in the ith verse
            if bool(re.search(stemed_text, quran.verse.iloc[i])):
                df.loc[i]= quran[resulted_columns].iloc[i]
                #c = c + 1 



    # looping over the verses of the Quran
    for i in range(quran.shape[0]):
        
        # looping over the search words
        for word in words_lst:

            # check if a search word matches a tag of the ith verse
            if (word in quran.tags.iloc[i]):
                df.loc[i] =  quran[resulted_columns].iloc[i]

            # check if a search word appear in the ith verse
            if bool(re.search(word, quran.verse.iloc[i])):
                df.loc[i]= quran[resulted_columns].iloc[i]
                #c = c + 1 
        
        # are we searching for a stemmed version of the search words.    
        if stem:
            
            # looping over the stemmed search words
            for word in stemed_lst:       
                
                # check if a stemmed search word matches a tag of the ith verse
                if (word in quran.tags.iloc[i]):
                    df.loc[i] =  quran[resulted_columns].iloc[i]

                # check if a stemmed search word appear in the ith verse
                if bool(re.search(word, quran.verse.iloc[i])):
                    df.loc[i]= quran[resulted_columns].iloc[i]
                    #c = c + 1

    try:
        df.drop_duplicates(inplace=True)
    except:
        pass
    
    return df


