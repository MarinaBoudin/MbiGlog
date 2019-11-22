import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

import imageio
import numpy as np
import requests
from PIL import Image as PImage
from django.db import models
from django.db.models import QuerySet, Count
from keras.models import Model

from django.conf import settings as st


class Annotation(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class RankTaxon(Annotation):
    pass


class Taxon(models.Model):
    tax_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    sup_taxon = models.ForeignKey('Taxon', on_delete=models.SET_NULL, null=True)
    found_in_ncbi = models.BooleanField(default=True)
    rank = models.ForeignKey('RankTaxon', on_delete=models.PROTECT)
    id_generator = 10000000

    def save(self, *args, **kwargs):
        if self.tax_id is None:
            self.set_id_from_name()
        super(Taxon, self).save(*args, **kwargs)

    def set_id_from_name(self):
        tax_id = self.get_id_from_name(self.name)
        if tax_id:
            self.tax_id = tax_id
        else:
            tax_id = self.get_id_from_name(self.name.split()[0])
            if tax_id:
                self.tax_id = tax_id
            else:
                Taxon.id_generator += 1
                self.found_in_ncbi = False
                self.tax_id = Taxon.id_generator

    @staticmethod
    def get_id_from_name(name):
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&term={name}"
        root = ElementTree.fromstring(requests.get(url).content)
        if int(root.find('Count').text) > 0:
            return int(root.find('IdList').find('Id').text)

    def __str__(self):
        if self.sup_taxon is None:
            return self.name
        else:
            return "{} > {}".format(str(self.sup_taxon), self.name)


class Specie(Taxon):
    latin_name = models.CharField(max_length=50)
    vernacular_name = models.CharField(max_length=50)

    def __str__(self):
        return self.latin_name


class ContentImage(Annotation):
    pass


class TypeImage(Annotation):
    pass


class Image(models.Model):  # TODO Un parser sur notre jeux de données qui pourra populer la db
    image = models.ImageField(upload_to="images/")
    date = models.DateTimeField(auto_now_add=True)
    specie = models.ForeignKey('Specie', on_delete=models.SET_NULL, null=True)
    content = models.ForeignKey('ContentImage', on_delete=models.PROTECT)
    type = models.ForeignKey('TypeImage', on_delete=models.PROTECT)
    trustworthy = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.image.name} : {self.specie.name}'

    def preprocess(self):
        img = imageio.imread(self.image.path, pilmode='RGB')
        img = np.array(PImage.fromarray(img).resize((224, 224))).astype(np.float32)
        img[:, :, 0] -= 123.68
        img[:, :, 1] -= 116.779
        img[:, :, 2] -= 103.939
        img[:, :, [0, 1, 2]] = img[:, :, [2, 1, 0]]
        img = img.transpose((2, 0, 1))
        return np.expand_dims(img, axis=0)


class ImageClassifier(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    accuracy = models.DecimalField(max_digits=4, decimal_places=3)
    name = models.CharField(max_length=50)

    def classify(self, images: Iterable[Image]) -> Iterable[Specie]:
        raise NotImplementedError("Should implement classify")

    class Meta:
        abstract = True


class Optimizer(Annotation):
    pass


class Loss(Annotation):
    pass


sys.path.append(os.path.join(st.MEDIA_ROOT, 'models_scripts'))


class CNNArchitecture(models.Model):
    name = models.CharField(max_length=30)
    optimizer = models.ForeignKey('Optimizer', on_delete=models.PROTECT)
    loss = models.ForeignKey('Loss', on_delete=models.PROTECT)
    model_code = models.FileField(upload_to="models_scripts")

    def __str__(self):
        return self.name

    def _create_model(self) -> Model:
        code = import_module(Path(self.model_code.name).stem)
        return code.create_model()

    def compile(self) -> Model:
        nn_model = self._create_model()
        nn_model.compile(optimizer=self.optimizer.name, loss=self.loss.name, metrics=['accuracy'])
        return nn_model


class CNN(ImageClassifier):
    training_data = models.FilePathField(allow_folders=True, null=True)
    architecture = models.ForeignKey('CNNArchitecture', on_delete=models.PROTECT)
    available = models.BooleanField(default=False)
    classes = models.ManyToManyField(Specie, through="Class", related_name='+')
    training_images = models.ManyToManyField(Image, related_name="trained_cnn")
    nn_model = None
    train_images = None
    train_labels = None
    test_images = None
    test_labels = None

    def train(self, training_data=None):
        # TODO Deal with training data only if specified, otherwise use all available data
        #  (Maybe use filter kwargs instead of directly give training dataset)

        self.nn_model = self.architecture.compile()
        self.split_images(test_fraction=0.2)
        self.nn_model.fit(self.train_images, self.train_labels, epochs=10)
        _, self.accuracy = self.nn_model.evaluate(self.test_images, self.test_labels)
        self.training_data = os.path.join(st.MEDIA_ROOT, 'training_datas', f'{self.architecture.name}_'
                                                                        f'{self.date.year}_'
                                                                        f'{self.date.month}_'
                                                                        f'{self.date.day}_'
                                                                        f'{self.date.hour}')
        os.mkdir(self.training_data)
        self.nn_model.save(self.training_data)
        self.available = True

    def split_images(self, images: QuerySet = None, test_fraction: float = 0.2):
        if images is None:
            images = Image.objects.all()
        images = images.filter(trustworthy=True)

        images.values('specie__name').annotate(Count('specie')) # TODO A tester pas sûr du tout que ça marche mais permet de gérer un queryset en entrée à priori
        # for image in images:
        #     try:
        #         self.classes.get(specie=image.specie)
        #     except DoesNotExist:
        #         if images.filter(specie=image.specie)
        #         Class.objects.create(pos=id_class, specie=image.specie, cnn=self)
        # self.train_images = []
        # self.train_labels = []
        # self.test_images = []
        # self.test_labels = []
        # id_class = 1
        # for specie in Specie.objects.all():
        #     trustfull_class_images = specie.image_set.filter(trustworthy=True)
        #     nb_image = 0
        #     nb_occurency = trustfull_class_images.count()
        #     if nb_occurency > 10:
        #         Class.objects.create(pos=id_class, specie=specie, cnn=self)
        #         id_class += 1
        #         train_test_limit = nb_occurency * (1 - test_fraction)
        #         for image in trustfull_class_images:
        #             nb_image += 1
        #             if nb_image <= train_test_limit:
        #                 self.train_images.append(image)
        #                 self.train_labels.append(id_class)
        #             else:
        #                 self.test_images.append(image)
        #                 self.test_labels.append(id_class)
        #     else:
        #         Class

    def classify(self, images: Iterable[Image]):
        if not self.available:
            raise Exception('The CNN is not available yet')
        if self.nn_model is None:
            self.nn_model = self.architecture.compile()
            self.nn_model.load_weights(self.training_data)

        predictions = self.nn_model.predict(images)
        predictions.argmax()  # TODO extract max p for all given images and get Specie from here


class Class(models.Model):
    pos = models.IntegerField()
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE)
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE, null=True)
