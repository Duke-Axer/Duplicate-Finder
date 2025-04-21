"""Zawiera wszystkie klasy i metody do analizy podobieństwa"""

import os
import numpy as np
from scripts import settings
from scripts.batch import Batch

from sklearn.metrics.pairwise import cosine_similarity
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True #Ładuj uszkodzone pliki

class Similarity():
    """Klasa odpowiada za wykonanie predykcji cech, analizy podobieństwa itp."""
    _tensorflow_load = False
    image = None
    _tf = None
    preprocess_input = None
    _model = None
    
    def __init__(self, batch_obj: Batch):
        self.batch_features = batch_obj.batch_features
        """Zawiera tablicę numpy z predykcją cech dla wielu obrazów"""
        self.batch_type = batch_obj.type_batch
        """Zawiera informacje o typie serii"""
        self.batch_name = batch_obj.name
        """Zawiera informacje o nazwie serii"""
        self.similarity_matrix = np.array([], np.dtype('float32'))
        """Macierz podobieństwa"""

    @classmethod
    def _load_tensorflow(cls):
        """Ładuje biblioteki TensorFlow
        """
        if not cls._tensorflow_load:
            print('\r\033[32mTrwa ładowanie bibliotek tensorflow\033[0m')
            import tensorflow as tf
            if tf.config.list_physical_devices('GPU'):
                print("GPU dostępne!")
            from tensorflow.keras.preprocessing import image
            from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
            cls._tf = tf
            cls.image = image
            cls.preprocess_input = preprocess_input
            cls._tensorflow_load = True
            cls._model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
            
            @cls._tf.function
            @cls._tf.autograph.experimental.do_not_convert
            def predict_batch(images_array):
                """Predykcja cech dla wszystkich obrazów w partii"""
                return cls._model(images_array, training=False)
            cls.predict_batch = predict_batch
            print('\r\033[32mKoniec ładowania\033[0m')
        
    @classmethod
    def images_to_vectors(cls, batch_patchs):
        """Funkcja do konwersji zbioru obrazów na wektory cech w partiach
        
        :return np.array([]) batch_features: Cechy obrazów serii.
        :return np.array([]) images_info: Informacje o obrazach w serii.
        """
        cls._load_tensorflow()
        images_array = []
        imgs_data = []
        for var, img_info in enumerate(batch_patchs):
            img = cls.image.load_img(img_info['path'], target_size=(224, 224))
            images_array.append(cls.image.img_to_array(img))
            imgs_data.append((img_info['path'], 1, 0, var))

        images_info = np.array(imgs_data, dtype=settings.dtype_good)
        images_array = np.array(images_array)
        images_array = cls.preprocess_input(images_array)  # Normalizacja obrazów
        batch_features = cls.predict_batch(images_array)
        return batch_features, images_info
    
    def create_matrix(self, batch_2: Batch | None = None):
        """Tworzy macierz podobieństwa na podstawie jednej serii, gdy nie została przekazana druga seria w argumencie.
        Sprawdza, które image są do siebie podobne.
        
        :return: Zwraca np: [['b_n1', int(num_1) 'b_n2', int(num_2), sim], ...]
        """
        if batch_2 is None:
            batch_2_name = self.batch_name
            self.similarity_matrix = cosine_similarity(self.batch_features)
        else:
            batch_2_name = batch_2.name
            self.similarity_matrix = cosine_similarity(self.batch_features, batch_2.batch_features)
        similar_images = []
        for i in range(len(self.similarity_matrix)):
            for j in range(i + 1, len(self.similarity_matrix[i])):
                if self.similarity_matrix[i][j] >= settings.Config.similarity:
                    similar_images.append((self.batch_name, i, batch_2_name, j, self.similarity_matrix[i, j]))
        return similar_images   
