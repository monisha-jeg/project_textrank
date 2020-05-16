import numpy as np
import nltk, os, sys
from collections import Counter
from textrank import *
import string
from stopwords import *



#SYNTACTIC FILTERS
noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']
verb_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adj_tags = ['JJ', 'JJR', 'JJS']
syntactic_filter = noun_tags + adj_tags

#PARAMETERS
W = 4
#Set similarity to 1 for word embeddings, 2 for wordnet, 0 for none
similarity = 2
esa = False


#GOOGLE WORD EMBEDDINGS BASED SIMILARITY
# import gensim
# #LOAD MODEL
# model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
# def google_sim(word1, word2):
# 	return model.similarity(word1, word2)


#WORDNET BASED SIMILARITY
from nltk.corpus import wordnet
def wordnet_sim(word1, word2):
	max_sim = 0
	for syn1 in wordnet.synsets(word1):
		for syn2 in wordnet.synsets(word2):
			sim = syn1.wup_similarity(syn2)
			if sim != None:
				max_sim = max(max_sim, sim)
	if(max_sim == 0.0):
		return 0.01
	return max_sim



#ESA RELATED WORDS
def get_esa(word):	
	os.system("javac -cp \"descartes-0.2/bin/*\" descartes-0.2/ESA.java")
	os.system("java -cp \"descartes-0.2/bin/*\":\"descartes-0.2/.\" ESA \"descartes-0.2/index\" 10 \"" + word + "\" >  tmp");

	with open("tmp", 'r') as tmpfile:
		words = [line.strip() for line in tmpfile.readlines()[:-1]]
	return words


#TAKES FILENAME AS INPUT AND RETURNS LIST OF KEYWORDS
def get_keywords(data_file):
	data = (open(data_file, 'r').read()+".").replace("\n", " ")

	tokenized_data = nltk.word_tokenize(data)
	tokenized_data_no_punc = nltk.word_tokenize(data.translate(None, string.punctuation))
	tokenized_data_no_punc_no_stopwords = [word for word in tokenized_data_no_punc if (word.lower() not in stop_words and word not in stop_words)]
	tagged_data = nltk.pos_tag(tokenized_data)
	# print(tokenized_data, tagged_data)

	#Make vocab
	word_to_id = {}
	word_to_id_lower = {}
	vocab_size = 0
	for (word, pos) in tagged_data:
		if word in tokenized_data_no_punc_no_stopwords and pos in syntactic_filter:
			if word not in word_to_id and word.lower() not in word_to_id and word not in word_to_id_lower:		
				word_to_id[word] = vocab_size
				word_to_id_lower[word.lower()] = vocab_size
				vocab_size += 1				
	id_to_word = {word_id : word for (word, word_id) in word_to_id.iteritems()}
	#print(word_to_id)
	print(id_to_word)


	#Build Cooccurence Matrix
	word_graph = [[0 for i in range(vocab_size)] for j in range(vocab_size)]
	for i in range(len(tokenized_data_no_punc_no_stopwords)):
		word1 = tokenized_data_no_punc_no_stopwords[i]	

		for j in range(1, W):
			if(i+j < len(tokenized_data_no_punc_no_stopwords)):
				word2 = tokenized_data_no_punc_no_stopwords[i+j]
				if word1 in word_to_id and word2 in word_to_id:
					if similarity == 0:
						word_graph[word_to_id[word1]][word_to_id[word2]] = 1
					elif similarity == 1:
						word_graph[word_to_id[word1]][word_to_id[word2]] = google_sim(word1, word2)
					elif similarity == 2:
						word_graph[word_to_id[word1]][word_to_id[word2]] = wordnet_sim(word1, word2)

			else:
				break
		for j in range(1, W):
			if(i-j >= 0):
				word2 = tokenized_data_no_punc_no_stopwords[i-j]
				if word1 in word_to_id and word2 in word_to_id:
					if similarity == 0:
						word_graph[word_to_id[word1]][word_to_id[word2]] = 1
					elif similarity == 1:
						word_graph[word_to_id[word1]][word_to_id[word2]] = google_sim(word1, word2)
					elif similarity == 2:
						word_graph[word_to_id[word1]][word_to_id[word2]] = wordnet_sim(word1, word2)
			else:
				break



	word_graph = np.array(word_graph, dtype=np.dtype(float))
	#print(word_graph)
	#Normalize
	for index in range(vocab_size):
		row_sum = np.sum(word_graph[index])
		if row_sum != 0:
			word_graph[index] = word_graph[index] / row_sum
	#print(word_graph)


	#Apply textrank and get keywords
	ranks = text_rank(word_graph, vocab_size, 0.00001, 0.85)
	num_keywords = vocab_size/2
	rank_indices = np.argsort(ranks)[::-1][:num_keywords]
	keywords = [id_to_word[index] for index in rank_indices]
	#print(ranks, keywords)


	#Handle bigrams, trigrams and 4-grams
	words_to_remove = []
	for i in range(len(tokenized_data))[:-1]:
		word1 = tokenized_data[i]
		word2 = tokenized_data[i+1]
		if word1 in keywords and word2 in keywords:
			words_to_remove.extend([word1, word2])
			keywords.append(word1 + " " + word2)

	for i in range(len(tokenized_data))[:-2]:
		word1 = tokenized_data[i]
		word2 = tokenized_data[i+1]
		word3 = tokenized_data[i+2]
		if word1 in keywords and word2 in keywords and word3 in keywords:
			words_to_remove.extend([word1, word2, word3])
			keywords.append(word1 + " " + word2 + " " + word3)
		if word1 + " " + word2 in keywords and word3 in keywords:
			words_to_remove.extend([word1 + " " + word2, word3])
			keywords.append(word1 + " " + word2 + " " + word3)
		# if word1 in keywords and word2 in stop_words and word3 in keywords:
		# 	words_to_remove.extend([word1, word3])
		# 	keywords.append(word1 + " " + word2 + " " + word3)

	for i in range(len(tokenized_data))[:-3]:
		word1 = tokenized_data[i]
		word2 = tokenized_data[i+1]
		word3 = tokenized_data[i+2]
		word4 = tokenized_data[i+3]
		if word1 in keywords and word2 in keywords and word3 in keywords  and word4 in keywords:
				words_to_remove.extend([word1, word2, word3, word4])
				keywords.append(word1 + " " + word2 + " " + word3 + " " + word4)
		if word1 + " " + word2 + " " + word3 in keywords and word4 in keywords:
			words_to_remove.extend([word1 + " "  + word2 + " " + word3, word4])
			keywords.append(word1 + " " + word2 + " " + word3 + " " + word4)
		# if word1 in keywords and word2 in stop_words and word3 in stop_words  and word4 in keywords:
		# 		words_to_remove.extend([word1, word4])
		# 		keywords.append(word1 + " " + word2 + " " + word3 + " " + word4)
	for word in set(words_to_remove):
		keywords.remove(word)


	words_to_remove = []
	for word1 in keywords:
		for word2 in keywords:
			if word1 != word2 and word1 in word2:
				words_to_remove.append(word1)

	for word in set(words_to_remove):
		keywords.remove(word)


	if esa == True:
		
		esa_lists = []
		for keyword in set(keywords):
			esa_set = get_esa(keyword)
			esa_lists.append(esa_set)

		all_esa_words =  set().union(*esa_lists)
		for esa_word in all_esa_words:
			match_count = 0
			for esa_list in esa_lists:
				if esa_word in esa_list:
					match_count += 1
			if(match_count > 1):
				keywords.append(esa_word)

	
	return set(keywords)



# print(get_keywords("sample"))

