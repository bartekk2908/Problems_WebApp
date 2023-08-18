from .models import Problems

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
import json


model = BertModel.from_pretrained("dkleczek/bert-base-polish-cased-v1")
tokenizer = BertTokenizer.from_pretrained("dkleczek/bert-base-polish-cased-v1")


def give_prob(pk):
    try:
        sol = Problems.objects.get(pk=pk).problem_content_text
    except Problems.DoesNotExist:
        sol = ""
    return sol


def give_sol(pk):
    try:
        sol = Problems.objects.get(pk=pk).solution_content_richtext
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


def give_similar_problems(query, n):

    """
    def give_similarity_old(sen1, sen2):

        # Convert the texts into TF-IDF vectors
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([sen1, sen2])

        # Calculate the cosine similarity between the vectors
        similarity = cosine_similarity(vectors)
        return np.min(similarity)
    """

    def give_similarity(emb1, emb2):
        return cosine_similarity(emb1, emb2)[0][0]

    similarities = []
    p_list = Problems.objects.all()

    for i in range(len(p_list)):
        emb2 = np.array(json.loads(p_list[i].embeddings_json))
        s = give_similarity(give_embeddings(query), emb2)
        print(f"{p_list[i].problem_content_text} -> {s:.4f}")
        similarities.append(s)
    indexes = sorted(range(len(similarities)), key=lambda x: similarities[x], reverse=True)[:n]
    return np.array(list(map(lambda x: x.pk, p_list)))[indexes]


def give_all_problems(sorting_by=None, direction='asc'):
    p_list = Problems.objects.all()

    sort_types = {
        'name': {'asc': 'problem_content_text', 'desc': '-problem_content_text'},
        'date': {'asc': 'pub_date', 'desc': '-pub_date'},
    }

    try:
        p_list = p_list.order_by(sort_types[sorting_by][direction])
    except KeyError:
        p_list = p_list.order_by(sort_types["name"]["asc"])

    return np.array(list(map(lambda x: x.pk, p_list)))
