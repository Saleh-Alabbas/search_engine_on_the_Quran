#%% Importing needed packages
import re
import pandas as pd


#
from nltk.corpus import stopwords

#
from nltk import word_tokenize
from nltk.stem.isri import ISRIStemmer
from nltk.stem import PorterStemmer

from sklearn.feature_extraction.text import CountVectorizer
from farasa.stemmer import FarasaStemmer

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
    verse = re.sub("[-.\",';:]","",verse)
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


# adjusting our search function to be able to search by English.

def search(text,tashkil=False, stem= False, both_lang=False):
    
    # importing quran data.
    quran = pd.read_pickle("../pickle/tagged_quran.pkl")
    #===========setting up resultant columns and by which languge we search=================#
    
    if re.search("[A-Za-z]",text):
        #search in E_tags and English columns
        language="English"
        tags="E_tags"

        if both_lang:
            # return both languages
            if tashkil:
                # return English and Arabic with tashkil
                resulted_columns=["chapter","chapter_num", "verse_num", "tashkil", "English","E_tags"]
            else:
                # return English and Arabic without tashkil
                resulted_columns=["chapter","chapter_num", "verse_num", "verse", "English","E_tags"]
        else:
            # return only English
            resulted_columns= ["chapter_num", "verse_num", "English","E_tags"]
    
    else:
        # text is not English
        # search in Arabic tags and verses
        tags="tags"
        language="verse"
        
        if both_lang:
            # return both language
            if tashkil:
                # return English and Arabic with tashkil
                resulted_columns=["chapter","chapter_num", "verse_num", "tashkil", "English","tags"]
            else:
                # return English and Arabic without tashkil
                resulted_columns= ["chapter","chapter_num", "verse_num", "verse", "English","tags"]
        else: 
            # only Arabic

            if tashkil:
                # with tashkil
                resulted_columns= ["chapter","chapter_num", "verse_num", "tashkil","tags"]
            else:
                # without tashkil
                resulted_columns = ["chapter","chapter_num", "verse_num", "verse","tags"]
    
    df = pd.DataFrame(columns=resulted_columns)


    words_lst = text.split()

    # do the stemming only once because it takes time
    if stem & (language=="verse"):
        # stemming the text
        stemed_text=FarasaStemmer().stem(text)
        
        # stemming the search words
        stemed_lst=[FarasaStemmer().stem(i) for i in words_lst]
    elif stem & (language=="English"):
        return("there is no english stem search")
        


    #================SEARCHING: for search whole text===================#
    
    
    
    # searching for the complite text
    for i in range(quran.shape[0]):
        # check if the text matches a tag of the ith verse
        if (text in quran[tags].iloc[i]):
            df.loc[i] =  quran[resulted_columns].iloc[i]

        # check if the text appear in the ith verse
        if bool(re.search(text, quran[language].iloc[i])):
            df.loc[i]= quran[resulted_columns].iloc[i]

        
        # are we searching for a stemmed version of the text    
        if stem:
            # check if stemmed text matches a tag of the ith verse
            if (stemed_text in quran[tags].iloc[i]):
                df.loc[i] =  quran[resulted_columns].iloc[i]

            # check if stemmed text appear in the ith verse
            if bool(re.search(stemed_text, quran.stemmed.iloc[i])):
                df.loc[i]= quran[resulted_columns].iloc[i]



    #================SEARCHING: for individual search words===================#

    # looping over the verses of the Quran
    for i in range(quran.shape[0]):
        
        # looping over the search words
        for word in words_lst:

            # check if a search word matches a tag of the ith verse
            if (word in quran[tags].iloc[i]):
                df.loc[i] =  quran[resulted_columns].iloc[i]

            # check if a search word appear in the ith verse
            if bool(re.search(word, quran[language].iloc[i])):
                df.loc[i]= quran[resulted_columns].iloc[i]
 
        
        # are we searching for a stemmed version of the search words.    
        if stem:
            
            # looping over the stemmed search words
            for word in stemed_lst:       
                
                # check if a stemmed search word matches a tag of the ith verse
                if (word in quran[tags].iloc[i]):
                    df.loc[i] =  quran[resulted_columns].iloc[i]

                # check if a stemmed search word appear in the ith verse
                if bool(re.search(word, quran.stemmed.iloc[i])):
                    df.loc[i]= quran[resulted_columns].iloc[i]

    
    return df




# %%
