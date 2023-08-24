from .models import Solutions, Images_features

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
import json
from bs4 import BeautifulSoup
import cv2
import base64
import re


model = BertModel.from_pretrained("dkleczek/bert-base-polish-cased-v1")
tokenizer = BertTokenizer.from_pretrained("dkleczek/bert-base-polish-cased-v1")


def get_prob_text(pk):
    try:
        prob = Solutions.objects.get(pk=pk).problem_content_text
    except Solutions.DoesNotExist:
        prob = ""
    return prob


def get_sol_text(pk):
    try:
        sol = Solutions.objects.get(pk=pk).solution_content_richtext
    except Solutions.DoesNotExist:
        sol = ""
    return sol


def get_p_id(pk):
    try:
        p_id = Solutions.objects.get(pk=pk).problem_id
        return p_id
    except Solutions.DoesNotExist:
        print("Nie można znaleźć problemu o tym pk.")
        return None


def give_text_embeddings(sen):
    # print(sen)
    inputs = tokenizer(sen, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    return embeddings


def get_similar_problems_text(n, query, pk=-1, limit=0.05):
    def give_similarity(emb1, emb2):
        return cosine_similarity(emb1, emb2)[0][0]

    similarities = []
    s_list = Solutions.objects.filter(is_newest=True).exclude(pk=pk)

    print()
    print("SIMILARITIES: ")
    print(f"Query: {query}")
    for i in range(len(s_list)):
        emb2 = np.array(json.loads(s_list[i].embeddings_json))
        s = give_similarity(give_text_embeddings(query), emb2)
        print(f"{s_list[i].problem_content_text} -> {s:.4f}")
        if s > limit:
            similarities.append(s)
    print("\n")
    indexes = sorted(range(len(similarities)), key=lambda x: similarities[x], reverse=True)[:n]
    return list(np.array(list(map(lambda x: x.pk, s_list)))[indexes])


def get_all_problems(sorting_by=None, direction='asc'):
    p_list = Solutions.objects.filter(is_newest=True)

    sort_types = {
        'name': {'asc': 'problem_content_text', 'desc': '-problem_content_text'},
        'date': {'asc': 'pub_date', 'desc': '-pub_date'},
    }

    try:
        p_list = p_list.order_by(sort_types[sorting_by][direction])
    except KeyError:
        p_list = p_list.order_by(sort_types["name"]["asc"])

    return np.array(list(map(lambda x: x.pk, p_list)))


def get_newest_problem(p_id):
    try:
        pk = Solutions.objects.get(problem_id=p_id, is_newest=True).pk
        return pk
    except Solutions.DoesNotExist:
        print("Nie można znaleźć problemu o tym id.")
        return None


def get_text_data(prob, sol):
    return prob + " " + BeautifulSoup(sol, 'html.parser').get_text().replace('\n', ' ')


def get_image_features(im):
    def histogram(image, mask):
        hist = cv2.calcHist([image], [0, 1, 2], mask, (8, 12, 3),
                            [0, 180, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        # return the histogram
        return hist

    im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    features = []
    (h, w) = im.shape[:2]
    (cX, cY) = (int(w * 0.5), int(h * 0.5))
    segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h), (0, cX, cY, h)]
    (axesX, axesY) = (int(w * 0.75) // 2, int(h * 0.75) // 2)
    ellipMask = np.zeros(im.shape[:2], dtype="uint8")
    cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)
    for (startX, endX, startY, endY) in segments:
        cornerMask = np.zeros(im.shape[:2], dtype="uint8")
        cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
        cornerMask = cv2.subtract(cornerMask, ellipMask)
        hist = histogram(im, cornerMask)
        features.extend(hist)
    hist = histogram(im, ellipMask)
    features.extend(hist)
    return np.array(features)


def save_images_features(richtext, problem):
    temp_dir = 'temp_dir/'
    images_data = BeautifulSoup(richtext, 'html.parser').find_all('img')
    for im_data in images_data:
        im_str = re.sub('^data:image/.+;base64,', '', im_data['src'])
        with open(temp_dir + 'image.png', 'wb') as f:
            f.write(base64.b64decode(im_str))
        im = cv2.imread(temp_dir + 'image.png')
        i = Images_features(problems_fk=problem, features_json=json.dumps(get_image_features(im).tolist()))
        i.save()


def get_similar_problems_images(n, image, limit=5.0):
    def chi2_distance(histA, histB, eps=1e-10):
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(histA, histB)])
        return d

    distances = []
    f_list = Images_features.objects.select_related('problems_fk').filter(problems_fk__is_newest=True)

    print()
    print("DIFFERENCES: ")
    for i in range(len(f_list)):
        features2 = json.loads(f_list[i].features_json)
        d = chi2_distance(get_image_features(image), features2)
        print(f"{f_list[i].problems_fk.pk} -> {d:.4f}")
        if d < limit:
            distances.append(d)
    print("\n")
    indexes = sorted(range(len(distances)), key=lambda x: distances[x], reverse=False)
    pkeys = np.array(list(map(lambda x: x.problems_fk.pk, f_list)))[indexes]

    seen = set()
    seen_add = seen.add
    pkeys = [x for x in pkeys if not (x in seen or seen_add(x))]

    return pkeys[:n]


def get_similar_problems_text_and_images(n, query, image, img_imp=5):

    m = len(get_all_problems())
    pkeys1 = get_similar_problems_text(m, query)
    pkeys2 = get_similar_problems_images(m, image, limit=3.0)
    print(pkeys1)
    print(pkeys2)

    weights = {}
    for pk in pkeys1:
        w1 = pkeys1.index(pk)
        try:
            w2 = pkeys2.index(pk)
        except ValueError:
            w2 = img_imp
        weights[pk] = w1 + w2
    print(weights)

    elo = [x for _, x in sorted(zip(list(weights.values()), list(weights.keys())), reverse=False)]
    print(elo)

    return elo[:n]
