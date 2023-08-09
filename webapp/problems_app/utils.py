from .models import Problems

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import BertTokenizer, BertModel
import torch


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')


def give_sol(problem):
    try:
        sol = Problems.objects.get(problem_content_text=problem).solution_content_text
    except Problems.DoesNotExist:
        sol = ""
    return sol


def give_embeddings(sen):
    inputs = tokenizer(sen, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    # print(embeddings)
    # print()
    return embeddings


def similar_problems(problem, n):

    def give_similarity_old(sen1, sen2):

        # Convert the texts into TF-IDF vectors
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([sen1, sen2])

        # Calculate the cosine similarity between the vectors
        similarity = cosine_similarity(vectors)
        return np.min(similarity)

    def give_similarity(sen1, sen2):
        return cosine_similarity(give_embeddings(sen1), give_embeddings(sen2))[0][0]

    similarities = []
    p_list = Problems.objects.all()

    for i in range(len(p_list)):
        s = give_similarity(problem, p_list[i].problem_content_text)
        # print(f"{p_list[i].problem_content_text} -> {s}")
        similarities.append(s)
    indexes = sorted(range(len(similarities)), key=lambda x: similarities[x], reverse=True)[:n]
    return np.array(list(map(lambda x: x.problem_content_text, p_list)))[indexes]
