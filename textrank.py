import numpy as np


def text_rank(M, n, e, d):
	S = np.ones(n) / n

	while(1):
		S_new = (np.ones(n)/n)*(1 - d) + d * M.T.dot(S)
		#print(S_new*100)

		if abs((S_new - S)).sum() < e:
			break
		S = S_new
		
	return S_new




