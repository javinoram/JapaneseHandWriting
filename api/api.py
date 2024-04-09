from flask import Flask, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import tensorflow as tf
from PIL import Image
import cv2


#Function to modify the image to be used for the neural network
def pre_processing_images(img, size):
    #Take the array into an image
    image = Image.fromarray(img.astype(np.uint8))

    #Resize the image into 28x28 pixels for the NNM
    image = image.resize(size)
    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)

    #Return the image into the correct format
    return image_array

#Function to evaluate the image
def evaluate(img, model, tipo, size):
    post_image = pre_processing_images(img, size)
    y = model.predict( post_image )
    return (pd.read_csv(f'model/{tipo}/k49_classmap.csv'))['char'][ y.argmax(axis=1)[0] ]

#Function to separate images
def split_images(img):
    final_images = []

    #Read the file and transform it into a array
    nparr = np.frombuffer(img.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    #Process the image into a binary one
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    #Set some tolerance to recognice special symbols
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(binary, kernel, iterations=5)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Cut each character and stored into the list
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        roi = binary[y:y+h, x:x+w]
        final_images.append(roi)
    return final_images
    



#APP base
app = Flask(__name__)
CORS(app) 


#API route for japanese predictor
@app.route("/japanese", methods=['POST'])
def prediccion_japanese():
    if request.method == 'POST':
        try:
            #Get the image from the request
            img = request.files['image']
            #Split the word in the image into different characters
            list_img = split_images( img )
            #Open the NNM to predict the characters 
            model = tf.keras.models.load_model('model/japanese/japanesemodel.keras')
            #Prediction of each character and save it into a string
            prediction = ""
            for img in list_img:
                pred = evaluate(img, model, "japanese", (28,28))
                prediction = prediction + pred

            return {'result': prediction, 'error': ''}
        except:
            return {'result': None, 'error': 'Error in the process'}


#API route for korean predictor
@app.route("/korean", methods=['POST'])
def prediccion_korean():
    if request.method == 'POST':
        try:
            #Get the image from the request
            img = request.files['image']

            #Split the word in the image into different characters
            list_img = split_images( img )

            #Open the NNM to predict the characters 
            model = tf.keras.models.load_model('model/korean/koreanmodel.keras')

            #Prediction of each character and save it into a string
            prediction = ""
            for img in list_img:
                pred = evaluate(img, model, "korean", (28,28))
                prediction = prediction + pred

            return {'result': prediction, 'error': ''}
        except:
            return {'result': None, 'error': 'Error in the process'}
        

#API route for russian predictor
@app.route("/russian", methods=['POST'])
def prediccion_russian():
    if request.method == 'POST':
        try:
            #Get the image from the request
            img = request.files['image']

            #Split the word in the image into different characters
            list_img = split_images( img )

            #Open the NNM to predict the characters 
            model = tf.keras.models.load_model('model/russian/russianmodel.keras')

            #Prediction of each character and save it into a string
            prediction = ""
            for img in list_img:
                pred = evaluate(img, model, "russian", (28,28))
                prediction = prediction + pred

            return {'result': prediction, 'error': ''}
        except:
            return {'result': None, 'error': 'Error in the process'}

if __name__ == '__main__':
    app.run(debug=False)