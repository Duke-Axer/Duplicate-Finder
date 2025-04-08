"""Zawiera wszystkie klasy i metody do analizy podobieństwa"""

import os
import batch
import numpy as np
import settings


from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input

if tf.config.list_physical_devices('GPU'):
    print("GPU dostępne!")


class Similarity():
    
    def __init__(self, batch_features=np.empty((100, 2048), dtype=np.float32)  ):
        
        self.batch_features = batch_features
        """Zawiera tablicę numpy z predykcją cech dla wielu obrazów"""
        self.similarity_matrix = np.array([], np.dtype('float32'))
        """macierz podobieństwa"""

    @staticmethod
    def images_to_vectors(batch_patchs):
        """Funkcja do konwersji zbioru obrazów na wektory cech w partiach"""
        images_array = []
        imgs_data = []
        
        # Ładowanie obrazów i przygotowanie ich w partiach
        var =0
        for img_info in batch_patchs:
            try:
                img = image.load_img(img_info['path'], target_size=(224, 224))  # Zmiana rozmiaru obrazu
            except OSError:
                print("Błąd ładowania pliku: ", img_info)
            
            images_array.append(image.img_to_array(img)) # Konwersja obrazu do tablicy NumPy
            imgs_data.append((img_info['path'], 1, 0, var))
            
            var+=1
        images_info = np.array(imgs_data, dtype=settings.dtype_good)

        
        images_array = np.array(images_array)
        images_array = preprocess_input(images_array)  # Normalizacja obrazów

        # Predykcja cech dla wszystkich obrazów w partii
        model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        batch_features = model.predict(images_array)  # Predykcja cech
        return batch_features, images_info


    def create_matrix(self, batch_features_2= np.array([], np.dtype("float32"))):
        """Tworzy macierz podobieństwa"""
        if batch_features_2.size == 0:
            self.similarity_matrix = cosine_similarity(self.batch_features)
        else:
            self.similarity_matrix = cosine_similarity(self.batch_features, batch_features_2)

    def compare(self):
        """Sprawdza, które image są do siebie podobne"""
        similar_images = []
        for i in range(len(self.similarity_matrix)):
            for j in range(i + 1, len(self.similarity_matrix)):
                if self.similarity_matrix[i][j] >= settings.Config.similarity:
                    similar_images.append((i+1,j+1,self.similarity_matrix[i, j]))
        
        return self.improve_compare_return(similar_images)
    
    def improve_compare_return(self, similarities):
        """Zwraca informacje bez duplikatów"""
        similar_images = {}

        # Zbieranie danych w odpowiedni format, unikając powtórzeń
        for img1, img2, sim in similarities:
            if img1 not in similar_images:
                similar_images[img1] = []
            similar_images[img1].append((img2, sim))

            # Dla img2 sprawdzamy, czy jest już w podobnych obrazach img1
            if img2 not in similar_images:
                similar_images[img2] = []
            similar_images[img2].append((img1, sim))

        # Wyświetlanie wyników z połączeniem podobieństw
        shown_images = set()  # Zbiór do śledzenia, które obrazy zostały już wyświetlone

        list_of_similary = []
        for img, similar in similar_images.items():
            one = []
            if img not in shown_images:
                one.append(img)
                # Dodajemy do listy każdy wynik, nie sortując
                for img2, sim in similar:
                    one.append((img2, float(sim)))
                    shown_images.add(img2)
                list_of_similary.append(one)
                shown_images.add(img)
        return list_of_similary

   