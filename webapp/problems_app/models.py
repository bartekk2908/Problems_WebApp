from django.db import models
from ckeditor import fields
from .utils import *
from django.utils import timezone
from django.contrib.auth.models import User

import json
import base64
import re
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from bs4 import BeautifulSoup
import cv2


class Solution(models.Model):
    problem_id = models.IntegerField(default=None)
    problem_content_text = models.CharField(max_length=200)
    solution_content_richtext = fields.RichTextField(default="")
    pub_date = models.DateTimeField("date published")
    embeddings_json = models.JSONField(default=None)
    is_newest = models.BooleanField()
    user_fk = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Problem_ID: {self.problem_id}, " \
               f"Problem: {self.problem_content_text}, " \
               f"Publish Date: {self.pub_date}," \
               f"By: {self.user_fk.username}"

    def save(self, *args, **kwargs):

        if not self.problem_id:
            last_record = Solution.objects.order_by('-problem_id').first()
            if last_record:
                self.problem_id = last_record.problem_id + 1
            else:
                self.problem_id = 1

        if not self.embeddings_json:
            text_data = self.get_text_data()
            print(text_data)
            self.embeddings_json = json.dumps(give_text_embeddings(text_data).tolist())

        if not self.pub_date:
            self.pub_date = timezone.now()

        print(self.is_newest)
        if self.is_newest is None:
            self.is_newest = True
        if self.is_newest:
            self.is_newest = False
            try:
                old = Solution.objects.get(problem_id=self.problem_id, is_newest=True)
                old.is_newest = False
                old.save()
            except Solution.DoesNotExist:
                pass
            self.is_newest = True

        self.save_images_features()

        super(Solution, self).save(*args, **kwargs)

    def save_images_features(self):
        temp_dir = 'temp_dir/'
        images_data = BeautifulSoup(self.solution_content_richtext, 'html.parser').find_all('img')
        for im_data in images_data:
            im_str = re.sub('^data:image/.+;base64,', '', im_data['src'])
            with open(temp_dir + 'image.png', 'wb') as f:
                f.write(base64.b64decode(im_str))
            im = cv2.imread(temp_dir + 'image.png')
            i = Image_feature(problems_fk=self, features_json=json.dumps(get_image_features(im).tolist()))
            i.save()

    def get_text_data(self):
        return (str(self.problem_content_text) + " " +
                BeautifulSoup(self.solution_content_richtext, 'html.parser').get_text().replace('\n', ' '))


class Image_feature(models.Model):
    problems_fk = models.ForeignKey(Solution, on_delete=models.CASCADE)
    features_json = models.JSONField(default=None)

    def __str__(self):
        return f"Key: {self.problems_fk.pk}, "


def get_all_solutions(sorting_by=None, direction='asc'):
    s_list = Solution.objects.filter(is_newest=True)

    sort_types = {
        'name': {'asc': 'problem_content_text', 'desc': '-problem_content_text'},
        'date': {'asc': 'pub_date', 'desc': '-pub_date'},
    }

    try:
        s_list = s_list.order_by(sort_types[sorting_by][direction])
    except KeyError:
        s_list = s_list.order_by(sort_types["name"]["asc"])

    return list(s_list)


def get_similar_problems_text(n, query, limit=0.05):
    def give_similarity(emb1, emb2):
        return cosine_similarity(emb1, emb2)[0][0]

    similarities = []
    s_list = Solution.objects.filter(is_newest=True)

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
    object_list = list(np.array(list(s_list))[indexes])
    print_pks(object_list)
    return object_list


def get_similar_problems_images(n, image, limit=5.0):
    def chi2_distance(histA, histB, eps=1e-10):
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(histA, histB)])
        return d

    distances = []
    f_list = Image_feature.objects.select_related('problems_fk').filter(problems_fk__is_newest=True)

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
    pkeys = np.array(list(map(lambda x: x.problems_fk, f_list)))[indexes]

    seen = set()
    seen_add = seen.add
    object_list = [x for x in pkeys if not (x in seen or seen_add(x))][:n]
    print_pks(object_list)
    return pkeys


def get_similar_problems_text_and_images(n, query, image, img_imp=5):

    m = len(get_all_solutions())
    objects1 = search_solutions(query, m)
    objects2 = get_similar_problems_images(m, image, limit=3.0)
    print_pks(objects1)
    print_pks(objects2)

    weights = {}
    for obj in objects1:
        w1 = objects1.index(obj)
        try:
            w2 = objects2.index(obj)
        except ValueError:
            w2 = img_imp
        weights[obj] = w1 + w2
    print(weights)

    elo = [x for _, x in sorted(zip(list(weights.values()), list(weights.keys())), reverse=False)][:n]
    print_pks(elo)

    return elo


def get_newest_solution(p_id):
    return Solution.objects.get(problem_id=p_id, is_newest=True)
