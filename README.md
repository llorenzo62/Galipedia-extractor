# Galipedia-extractor

## Introduction
This project was born because there is no spacy model for my mother language, the Galician.

I thought it wasn't a big problem just because Spacy is highly trainable so I just needed a public corpus for this task. But this hope fails, I can't find any worthwhile public corpus for Galician language.

So, I was faced with a painful situation. I needed to create a corpus to train the model, but I am convinced that this is an impossible task for a one person team. So I decided to do a micro-training, train the model as a variant of Portuguese or Spanish (I haven't been able to decide which one gives better results yet) and only for POS-tagging and lemmatization.

The first job is to obtain a large and representative set of correct sentences in Galician. I think there are two main sources, Galipedia and official publications (DOGA, Boletíns provinciais, etc...). I think that as a source of living language, Galipedia has no rival.

This is the motivation of the following modules.

## Galipedia
Three Jupyter notebooks to download Galipedia dumps, process them, and get a set of sentences suitable for training the language model.

## spacy_3.4
I work with the latest stable version of spacy in a virtual environment. In this directory you can find a convenience script to set up system commands for training (_train_models.py_), as well as configuration files for the models I've been training.

## Model
Current results. Also the word vectors trained with __floret__ on the set of sentences extracted from Galipedia (about 50 M words) and prepared for use in both floret and default spacy models (in their Spanish and Portuguese variants).

## dataset
Current corpus of tagged sentences (POS and lemmas) for training.

## verify
Current corpus of labeled sentences (POS and lemma) to test for accuracy. For the model implemented in _Model_, __gl_lg__ is about 95% for POS labeling and about 93% for lemmatization.

There are also three convenient scripts:
* _Galutils.py_: Here are some of the functions and constants that are used in the other scripts.
* *manage_sentences_tk.py*: A Tk-based graphical interface for working with labeled sentences
* *work_sentences_tk.py*: A Tk-based graphical interface to display the model output in arbitrary sentences written on the input.
