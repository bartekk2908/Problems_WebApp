import numpy as np
from transformers import BertTokenizer, BertModel
import torch
import cv2
from haystack.query import SearchQuerySet, SQ
from bs4 import BeautifulSoup
import re


model = BertModel.from_pretrained("dkleczek/bert-base-polish-cased-v1")
tokenizer = BertTokenizer.from_pretrained("dkleczek/bert-base-polish-cased-v1")


def give_text_embeddings(sen):
    # print(sen)
    inputs = tokenizer(sen, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    return embeddings


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


def search_solutions(query, n):
    results = SearchQuerySet().all()
    or_statement = ""
    words = query.split()
    m = len(words)
    for i in range(m):
        or_statement += f'SQ(content=words[{i}])'
        if i == m - 1:
            break
        or_statement += " | "
    # print(or_statement)
    results = results.filter(eval(or_statement))
    if results:
        print()
        print("SCORE: ")
        print(f"Query: {query}")
        for result in results:
            print(f"{result.object.problem_content_text} -> {result.score:.4f}")
    else:
        print("NO RESULTS")

    object_list = [x.object for x in results[:n]]
    # print_pks(object_list)

    return object_list


def print_pks(object_list):
    pk_list = [x.pk for x in object_list]
    print(pk_list)
    return pk_list


def richtext_to_text(richtext):
    return BeautifulSoup(richtext, 'html.parser').get_text().replace('\n', ' ')


def richtext_to_img_base64(richtext):
    imgs = BeautifulSoup(richtext, 'html.parser').find_all('img')
    return [re.sub('^data:image/.+;base64,', '', x['src']) for x in imgs]
