import cv2
import numpy as np
import os
import base64
import json
import joblib
from wavelet import w2d

__classfier_name_to_number = {}
__classfier_number_to_name = {}

__model = None
# Set the working directory to the directory where the script is located
os.chdir(os.path.dirname(__file__))
# Now you can access files in the same directory with relative paths


def classify_image(image_base64_data, file_path=None):

    imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)
    result = []
    for img in imgs:
        scalled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img, 'db1', 5)
        scalled_img_har = cv2.resize(img_har, (32, 32))
        combined_img = np.vstack((scalled_raw_img.reshape(32*32*3, 1), scalled_img_har.reshape(32*32, 1)))

        len_image_array = 32*32*3 + 32*32

        final = combined_img.reshape(1, len_image_array).astype(float)

        result.append({
            'class': class_number_to_name(__model.predict(final)[0]),
            'class_probability': np.around(__model.predict_proba(final)[0]*100, 2).tolist(),
            'class_dictionary': __classfier_name_to_number
        })

    return result


def load_saved_artifacts():

    print("loading saved artifacts...start")
    global __classfier_name_to_number
    global __classfier_number_to_name
    with open("./artifacts/class_dictonary.json", 'r') as f:
        __classfier_name_to_number = json.load(f)
        __classfier_number_to_name = {v: k for k, v in __classfier_name_to_number.items()}

    global __model
    if __model is None:
        with open('../server/artifacts/sport_person_model.pkl', 'rb') as f:
            __model = joblib.load(f)
    print("loading saved artifacts...done")


def get_cv2_image_from_base64_string(b64str):
    encoded_data = b64str.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eyes_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    if image_path:
        if os.path.exists(image_path):
            img = cv2.imread(image_path)
        else:
            raise FileNotFoundError(f"The specified image path '{image_path}' does not exist.")
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    cropped_faces = []

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eyes_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 2:
            cropped_faces.append(roi_color)
    return cropped_faces


def class_number_to_name(class_number):
    return __classfier_number_to_name[class_number]


def class_name_to_number(class_name):
    return __classfier_name_to_number[class_name]


def get_b64_test_image_virat():
    with open("b64.txt") as f:
        return f.read()


if __name__ == "__main__":
    print("Starting Python Flask Server For Sports Person Classifier")
    load_saved_artifacts()
    # print(classify_image(get_b64_test_image_virat()),None)
    # print(classify_image(get_b64_test_image_virat()))

    # print(classify_image(None, "./test_images/test1.jpg"))
    # print(classify_image(None, "./test_images/test2.jpg"))
    # print(classify_image(None, "./test_images/test3.jpg"))
    # print(classify_image(None, "./test_images/test4.jpg"))
    # print(classify_image(None, "./test_images/test5.jpg"))
    # print(classify_image(None, "./test_images/test6.jpg"))
    print(classify_image(None, "./test_images/test7.jpg"))
