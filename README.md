# Quranic search engine

## main goal
building a search engine on the Quran that allow us to:\
- find specific verses even if the search word's pronunes are incorrect.
- find all verses about a specific concept.
- collect acattered quranic stories together.
- allow both Arabic and English search.

## Cleaning The Data
- usual issues with text data (removing numbers, punctuation, diacritics ...)
    + re package was used to deal with this problem.
- Basmalah issue:
    + at the arabic version there was an extra basmalah attached to each first verse in each chapter.\
    while the english version has no extra basmalah's.
        - so I removed the extra basmalahs and added a basmalah before the first verse in each chapter with verse number = 0
 
 ## EDAs
 - mainly I compared between makki chapters and madani chapters.
 
 ## Search engine
 to achive the goals mentioned above we need to:
 - stem each verse and stem the search word befor searching
    + The Arabic version was stemmed by Farasa stemmer.
    + The English version was stemmed by nltk stemmer namly PorterStemmer
 - tag all verses discussing a specific concept by a tag, then search by tag to get all these verses.
    + almost manually, firstly by names. For example, if the verse contains "messiah", "son of mary" or "jesus" it will be tagged by "jesus".
    + another approach is to look up (either by graping a quran or otherwise) what verses are discussing Moses stories (for example), note them and then tag them.
  
 

## The Data
There are 2 data files we are dealing with, one is the arabic Quran\
and the other one is an English translated version of the Quran.

each data file has three important features:\
1- The number of the chapter (Surah).\
2- The number of the verse within (Ayah) the chapter.\
3-  the verse either in Arabic or in english.

### dara sources
1. The Arabic Data:\
  Tanzil Quran Text (Simple, Version 1.1)\
  Copyright (C) 2007-2022 Tanzil Project\
  License: Creative Commons Attribution 3.0\
  This copy of the Quran text is carefully produced, highly\
  verified and continuously monitored by a group of specialists\
  at Tanzil Project.\
  Please check updates at: http://tanzil.net/updates/

2. English transelation version:\
  Saheeh International translation from\
  https://quranenc.com/en/browse/english_saheeh
