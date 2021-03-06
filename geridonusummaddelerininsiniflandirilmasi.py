# -*- coding: utf-8 -*-
"""GeriDonusumMaddelerininSiniflandirilmasi.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PgtvDWGeJ_-D3P1H6nvSTjsRYEetxhdU

# GERİ DÖNÜŞÜM MADDELERİNİN SINIFLANDIRILMASI
"""

'''
Ekip Üyeleri
Okan DEMİRKAN      okaandemirkan@gmail.com
Pınar YAHŞİ        pinarryahsi@gmail.com
Betül ÇETİN        bet.ctn@gmail.com
Ceren BÜLBÜL       cerenbulbul27@gmail.com
Süheyla KARAKAYA   suheylakarakaya765@gmail.com


Mentorlerimiz
Merve Ayyüce KIZRAK       http://www.ayyucekizrak.com/       ayyucekizrak@gmail.com
Yavuz KÖMEÇOĞLU           http://yavuzkomecoglu.com/         komecoglu.yavuz@gmail.com
'''

"""# Proje Tanımı


# Kütüphanelerin Tanımlanması
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import cv2
from imutils import paths
from sklearn.utils import shuffle
from tqdm import tqdm

from __future__ import print_function
import keras
from keras.datasets import mnist
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras. layers import Conv2D, MaxPooling2D, ZeroPadding2D,Convolution2D,GlobalAveragePooling2D
from keras import backend as K
from keras.optimizers import SGD
import matplotlib.pyplot as plt

from keras.applications.vgg16 import VGG16
from keras.applications.resnet50 import ResNet50
from keras.applications.mobilenet import MobileNet
from keras.callbacks import EarlyStopping, ModelCheckpoint,History

import tensorflow as tf
run_opts = tf.RunOptions(report_tensor_allocations_upon_oom = True)
from keras import models
from sklearn.utils import shuffle

from keras.preprocessing.image import ImageDataGenerator
import time

"""# Google Drive'ın Colab Üzerinde Kullanılabilir Hale Getirilmesi"""

from google.colab import drive
drive.mount('/content/gdrive')

"""# Colab Tarafından Sağlanan Donanımların Kontrolü"""

from tensorflow.python.client import device_lib
device_lib.list_local_devices()

"""# Train Setinin Drive'dan Alınması"""

target_size = (224, 224)

root = '/content/gdrive/My Drive/Colab Notebooks/'
 
full_dataset_path = root + 'verikumesi/train/'
labels = {'trash': 5, 'glass': 1, 'plastic': 4, 'cardboard': 0, 'paper': 3, 'metal': 2}

x_train = []
y_train = []

for label in labels:
  path = full_dataset_path + label
  
  full_dataset_imagePaths = sorted(list(paths.list_images(str(path))))
  
  print(label)
  
  for i in tqdm(range(len(full_dataset_imagePaths))):
    imagePath = full_dataset_imagePaths[i]

    #print(imagePath)
    img = cv2.imread(imagePath)
    #img = cv2.resize(img, target_size).flatten()
    img = cv2.resize(img, target_size)
    x_train.append(img)
    
    label = imagePath.split(os.path.sep)[-2]
    y_train.append(labels[label])
           
print("len", len(x_train))
print("shape", x_train[0].shape)
print("len y_train", len(y_train))

"""# Test Setinin Drive'dan Alınması"""

target_size = (224, 224)

root = '/content/gdrive/My Drive/Colab Notebooks/'
 
full_dataset_path = root + 'verikumesi/test/'
labels = {'trash': 5, 'glass': 1, 'plastic': 4, 'cardboard': 0, 'paper': 3, 'metal': 2}

x_test = []
y_test = []

for label in labels:
  path = full_dataset_path + label
  
  full_dataset_imagePaths = sorted(list(paths.list_images(str(path))))
  
  print(label)
  
  for i in tqdm(range(len(full_dataset_imagePaths))):
    imagePath = full_dataset_imagePaths[i]

    #print(imagePath)
    img = cv2.imread(imagePath)
    #img = cv2.resize(img, target_size).flatten()
    img = cv2.resize(img, target_size)
    x_test.append(img)
    
    label = imagePath.split(os.path.sep)[-2]
    y_test.append(labels[label])
           
print("len", len(x_test))
print("shape", x_test[0].shape)
print("len y_test", len(y_test))

"""# Ön Hazırlık"""

x_train = np.array(x_train)
x_test = np.array(x_test)

y_train= np.array(y_train)
y_test= np.array(y_test)

"""# Verilerin Normalize Edilmesi"""

x_train= x_train/255
x_test= x_test/255

"""# Veri Setinin Karıştırılması"""

x_train, y_train = shuffle(x_train, y_train)
x_test, y_test = shuffle(x_test, y_test)

"""# Data Augmentation"""

datagen = ImageDataGenerator(
    featurewise_center=True,
    featurewise_std_normalization=True,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True)

"""# Verilerin Modele Uygun Girdi Boyutuna Ayarlanması"""

batch_size = 32
num_classes = 6 
epochs = 20 # 100 epoch önerilir
img_rows, img_cols = 224, 224

if K.image_data_format() == 'channels_first':
    x_train = x_train.reshape(-1, 3, img_rows, img_cols)
    x_test = x_test.reshape(-1, 3, img_rows, img_cols)
    input_shape = (3, img_rows, img_cols)
else:
    x_train = x_train.reshape(-1, img_rows, img_cols, 3)
    x_test = x_test.reshape(-1, img_rows, img_cols, 3)
    input_shape = (img_rows, img_cols, 3)
    
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

"""# Öğrenmeme Durumunda Erken Durdurma"""

callbacks = [EarlyStopping(monitor='val_loss', patience=5),
             ModelCheckpoint(filepath='best_model.h5', monitor='val_loss', save_best_only=True)]

"""# ***CNN DENEMELERİ***

# MobileNet - Seçilen Mimari
"""

#Model
model = MobileNet(weights='imagenet', include_top=False)

x = GlobalAveragePooling2D(input_shape=model.output_shape[1:])(model.output)
x = Dense(6, activation='softmax', kernel_initializer='glorot_normal')(x)
model = models.Model(inputs=model.input, outputs=x)


# fine tune training for top layers
for layer in model.layers[:-1]:#[n_frozen_layers:]:
    layer.trainable=True

"""# VGG16"""

'''

model = VGG16(weights='imagenet', include_top=False)
model.summary()

x = GlobalAveragePooling2D(input_shape=model.output_shape[1:])(model.output)
x = Dense(6, activation='softmax', kernel_initializer='glorot_normal')(x)
model = Model(inputs=model.input, outputs=x)


# fine tune training for top layers
for layer in model.layers[:-1]:#[n_frozen_layers:]:
    layer.trainable=True
    
    
model.compile(optimizer=SGD(lr=1e-4, momentum=0.9, nesterov=True),
              loss='categorical_crossentropy',
              metrics=['accuracy'])
              
model.summary()
              
'''

"""# ResNet"""

'''

model = ResNet50(weights='imagenet',include_top=False, input_shape=(224, 224, 3),classes = 6)
x = GlobalAveragePooling2D(input_shape=model.output_shape[1:])(model.output)
x = Dense(6, activation='softmax', kernel_initializer='glorot_normal')(x)
model = models.Model(inputs=model.input, outputs=x)


# fine tune training for top layers
for layer in model.layers[:-1]:#[n_frozen_layers:]:
    layer.trainable=True


'''

"""# Modelin Görselleştirilmesi"""

model.compile(optimizer=SGD(lr=1e-4, momentum=0.9, nesterov=True),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

"""# Modelin Oluşturulması"""

history = model.fit_generator(datagen.flow(x_test, y_test,
                                          batch_size=batch_size),
                                          validation_data=(x_test, y_test),
                                          steps_per_epoch=len(x_train) // batch_size,
                                          epochs=epochs)

"""# Sonuçların Görselleştirilmesi"""

score = model.evaluate(x_test, y_test, verbose=0)
print('Test Loss:', score[0])
print('Test Accuracy:', score[1])

print(history.history.keys())
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
