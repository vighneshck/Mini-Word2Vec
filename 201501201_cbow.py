import torch
from torch.autograd import Variable
import math
import sys
import random

dtype = torch.cuda.FloatTensor

word_count = {}
context_len = 2
unk = '<UNK>'

SEED = 5
V = 1
emb_dim = 100
learning_rate = 0.025
no_of_epochs = 100

with open('./procorpus', 'r') as f:
    for line in f:
        words = line.strip().split()
        for word in words:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
                V += 1

print(V)
words = [unk] + sorted(word_count, key=word_count.get, reverse=True)
index = {word : i for i, word in enumerate(words)}

data = []
labels = []

with open('./procorpus', 'r') as f:
    for line in f:
        sent = line.strip().split()
        sent = [unk for i in range(context_len)] + sent + [unk for i in range(context_len)]
        sent = [index[word] for word in sent]
        for i in range(context_len, len(sent) - context_len):
        	data.append([sent[j] for j in range(i - context_len, i)] + [sent[j] for j in range(i + 1, i + 1 + context_len)])
        	labels.append(sent[i])

random.seed(SEED)
random.shuffle(data)
random.seed(SEED)
random.shuffle(labels)

print(len(data))
data = data[:10000]
labels = labels[:10000]

w1 = Variable(torch.randn(V, emb_dim).type(dtype), requires_grad=True)
w2 = Variable(torch.zeros(emb_dim, V).type(dtype), requires_grad=True)

print("started training")
for epoch in range(1, no_of_epochs + 1):
	print("epoch " + str(epoch))
	losses = []
	for i in range(len(data)):	
		sys.stdout.write("%f%%       \r" % (i * 100.0/len(data)))
		sys.stdout.flush()
		x = torch.zeros(2 * context_len + 1, V).type(dtype)
		for j in range(len(data[i])):
			x[j, data[i][j]] = 1
		x = Variable(x, requires_grad=False)

		h1 = x.mm(w1).sum(0).unsqueeze(0)
		
		softmax = torch.nn.Softmax(dim=1)
		output = softmax(h1.mm(w2))

		loss = -1.0 * torch.log(output[0, labels[i]])
		loss.backward()

		w1.data -= learning_rate * w1.grad.data
		w2.data -= learning_rate * w2.grad.data

		w1.grad.data.zero_()
		w2.grad.data.zero_()
		losses.append(loss.data[0])

	print("")
	print("loss: " + str(sum(losses) * 1.0/len(losses)))

with open('./cbow_vecs', 'w+') as f:
	f.write(','.join(words) + '\n')
	for i in range(V):
		f.write(','.join([str(x) for x in w1.data[i, :].cpu().numpy().tolist()]) + '\n')
