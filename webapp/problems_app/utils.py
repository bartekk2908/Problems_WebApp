from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
from transformers import BertTokenizer, BertModel
import torch
import cv2


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
