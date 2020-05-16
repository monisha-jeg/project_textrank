import os
from keyword_extraction import *


def precision(targets, outputs):
	targets_lower_case = [word.lower() for word in targets]
	total = float(len(outputs))
	correct = 0
	for word in outputs:
		if word in targets or word.lower() in targets_lower_case:
			correct += 1
	return correct/total



def recall(targets, outputs):
	outputs_lower_case = [word.lower() for word in outputs]
	total = float(len(targets))
	correct = 0
	for word in targets:
		if word in outputs or word.lower() in outputs_lower_case:
			correct += 1
	return correct/total

N = 10
sum_p = 0
sum_r = 0
sum_f = 0

count = 0
for file in os.listdir("Hulth2003/Test"):	
	if file.endswith(".abstr"):
		count += 1
		if count > N:
			break

		abstract_file = "Hulth2003/Test/" + file
		keyword_file = "Hulth2003/Test/" + file.replace("abstr", "uncontr")
		
		target_keywords = [word.strip() for word in 
		open(keyword_file,'r').read().replace('\n', ' ').replace('\t', ' ').split(';')]
		output_keywords = get_keywords(abstract_file)

		print(open(abstract_file, 'r').read())		
		print(target_keywords)
		print(output_keywords)

		#Get precision, recall and F-score measures
		p = precision(target_keywords, output_keywords)
		sum_p += p
		r = recall(target_keywords, output_keywords)
		sum_r += r
		print "Precision : ", p, "; Recall : ", r
		try:
			f = 2*p*r/(p+r)
			print "F-measure : ", f
			sum_f += f
		except:
			print "Cannot calculate F-measure"
		print("\n\n")

		
		
		


mean_p = sum_p/N
mean_r = sum_r/N
mean_f = sum_f/N

print "Mean Precision : ",  mean_p
print "Mean Recall : ", mean_r	
print "Mean F-Score : ", mean_f
		






