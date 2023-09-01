from django.db import models
from ckeditor import fields
from .utils import *
from django.utils import timezone
from django.contrib.auth.models import User

import json
import base64
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import cv2


class Solution(models.Model):
    solution_id = models.IntegerField(default=None)
    problem_content_text = models.CharField(max_length=200)
    solution_content_richtext = fields.RichTextField(default="", max_length=10_000)
    pub_date = models.DateTimeField("date published")
    # embeddings_json = models.JSONField(default=None, null=True, blank=True)
    is_newest = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    eng_content = models.TextField()

    def __str__(self):
        return f"Solution_id: {self.solution_id}, " \
               f"Problem: {self.problem_content_text}, " \
               f"Publish Date: {self.pub_date}," \
               f"By: {self.user.username}"

    def save(self, *args, **kwargs):

        if not self.solution_id:
            last_record = Solution.objects.order_by('-solution_id').first()
            if last_record:
                self.solution_id = last_record.solution_id + 1
            else:
                self.solution_id = 1

        """
        if not self.embeddings_json:
            text_data = self.get_text_data()
            self.embeddings_json = json.dumps(give_text_embeddings(text_data).tolist())
        """

        if not self.pub_date:
            self.pub_date = timezone.now()

        if self.is_newest is None:
            self.is_newest = True
        if self.is_newest:
            self.is_newest = False
            try:
                old = Solution.objects.get(solution_id=self.solution_id, is_newest=True)
                old.is_newest = False
                old.save()
            except Solution.DoesNotExist:
                pass
            self.is_newest = True

        self.eng_content = self.get_text_data_eng()

        super(Solution, self).save(*args, **kwargs)

    def save_images_features(self):
        temp_dir = 'temp_dir/'
        images_data = richtext_to_img_base64(self.solution_content_richtext)
        for i in range(len(images_data)):
            with open(temp_dir + f'image.png', 'wb') as f:
                f.write(base64.b64decode(images_data[i]))
            im = cv2.imread(temp_dir + f'image.png')
            i = Image_feature(solution=self, features_json=json.dumps(get_image_features(im).tolist()))
            i.save()
            os.remove(temp_dir + "image.png")

    def get_text_data_eng(self):
        return translate_pl_to_en(str(self.problem_content_text) + " " +
                                  richtext_to_text(self.solution_content_richtext))


class Image_feature(models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
    features_json = models.JSONField(default=None)

    def __str__(self):
        return f"Key: {self.solution.pk}, "


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
    return object_list


def get_image_distances(image):
    def chi2_distance(histA, histB, eps=1e-10):
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(histA, histB)])
        return d

    distances = []
    f_list = Image_feature.objects.select_related('solution').filter(solution__is_newest=True)

    print()
    print("DIFFERENCES: ")
    for i in range(len(f_list)):
        features2 = json.loads(f_list[i].features_json)
        d = chi2_distance(get_image_features(image), features2)
        print(f"{f_list[i].solution.pk} -> {d:.4f}")
        distances.append(d)
    print("\n")
    pairs = sorted(zip(f_list, distances), key=lambda x: x[1], reverse=False)
    return pairs


def get_similar_problems_multiple_images(n, images, limit=5.0):
    all_pairs = []
    for im in images:
        pairs = get_image_distances(im)
        print_pks([x.solution for x, _ in pairs])
        all_pairs += pairs
    print_pks([x.solution for x, _ in all_pairs])
    seen = set()
    seen_add = seen.add
    pairs_non_dup = [(x, y) for x, y in all_pairs if y < limit and not (x in seen or seen_add(x))]
    return [x.solution for x, y in sorted(pairs_non_dup, reverse=False, key=lambda a: a[1])][:n]


def get_similar_problems_text_and_images(n, query, images, img_imp=5):

    m = len(get_all_solutions())
    objects1 = search_solutions(query, m)
    # objects1 = get_similar_problems_text(m, query)
    objects2 = get_similar_problems_multiple_images(m, images)
    print_pks(objects1)
    print_pks(objects2)

    weights = {}
    for obj in list(set(objects1 + objects2)):
        w1 = objects1.index(obj)
        try:
            w2 = objects2.index(obj)
        except ValueError:
            w2 = img_imp
        weights[obj] = w1 + w2
    return [x for _, x in sorted(zip(list(weights.values()), list(weights.keys())), reverse=False, key=lambda a: a[0])][:n]


def get_newest_solution(solution_id):
    return Solution.objects.get(solution_id=solution_id, is_newest=True)
