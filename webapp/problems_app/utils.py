from .models import Problems

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def give_sol(problem):
    try:
        sol = Problems.objects.get(problem_content_text=problem).solution_content_text
    except Problems.DoesNotExist:
        sol = ""
    return sol


def similar_problems(problem, n):

    def give_similarity(sen1, sen2):

        # Convert the texts into TF-IDF vectors
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([sen1, sen2])

        # Calculate the cosine similarity between the vectors
        similarity = cosine_similarity(vectors)
        return np.min(similarity)

    similarities = []
    p_list = Problems.objects.all()

    for i in range(len(p_list)):
        s = give_similarity(problem, p_list[i].problem_content_text)
        print(s)
        similarities.append(s)
    indexes = sorted(range(len(similarities)), key=lambda x: similarities[x])[-n:]
    return np.array(list(map(lambda x: x.problem_content_text, p_list)))[indexes]
