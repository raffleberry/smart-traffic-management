PORT = "ttyACM0"
import os

os.system("sudo chmod 777 /dev/"+PORT)
import tensorflow as tf
import threading
import requests
import copy
import csv
import cv2
import json
import time
import base64
import numpy as np
import base64
import re
import subprocess
from utils import visualization_utils as vis_util
import pyimgur
from serial import Serial

LIGHT_THRESHOLD = 10
TIMEOUT_THRESHOLD = 30
THRESHOLD = 2
CLIENT_ID = "7e638d0dd1b4caa"
PATH = "Nishant.png"
x=Serial('/dev/' + PORT,9600)

last_light_color = 'r'
last_light_change = 0.0
last_uploaded = 0.0

def other():
    global last_uploaded
    last_uploaded = time.time()
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded = im.upload_image(PATH, title="Uploaded with PyImgur")

    header = {"Content-Type": "application/json; charset=utf-8",
            "Authorization": "Basic MjQyYzEyNzQtNDcxYi00MDJmLTg1YjktYjFkOTM2MWRmODQx"}
    print("img link : " + uploaded.link)
    payload = {"app_id": "009fe070-cc94-450e-9762-4ff5f3ce1cd7",
            "included_segments": ["All"],
            "contents": {"en": "Mishap at camera 1"},
            "big_picture": uploaded.link }
    
    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))


def light_change(arg):
    if arg != 'g':
        last_light_change = time.time()
    x.write(arg)

client_id = '7e638d0dd1b4caa'
headers = {"Authorization": client_id} 
url = "https://api.imgur.com/3/upload"

# Variables
total_passed_vehicle = 0  # using it to count vehicles

def object_counting(input_video, detection_graph, category_index, is_color_recognition_enabled, fps, width, height):
        #initialize .csv
        with open('object_counting_report.csv', 'w') as f:
                writer = csv.writer(f)  
                csv_line = "Object Type, Object Color, Object Movement Direction, Object Speed (km/h)"                 
                writer.writerows([csv_line.split(',')])

        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #output_movie = cv2.VideoWriter('the_output.avi', fourcc, fps, (width, height))

        # input video
        cap = cv2.VideoCapture(input_video)

        total_passed_vehicle = 0
        speed = "waiting..."
        direction = "waiting..."
        size = "waiting..."
        color = "waiting..."
        counting_mode = "..."
        width_heigh_taken = True
        height = 0
        width = 0
        with detection_graph.as_default():
          with tf.Session(graph=detection_graph) as sess:
            # Definite input and output Tensors for detection_graph
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            # for all the frames that are extracted from input video
            last_light_color = 'g'
            light_change('g')

            last_light_change = time.time()
            while(cap.isOpened()):
                ret, frame = cap.read()                

                if not  ret:
                    print("end of the video file...")
                    break
                clean_frame = copy.deepcopy(frame)
                input_frame = frame

                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(input_frame, axis=0)

                # Actual detection.
                (boxes, scores, classes, num) = sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})

                # insert information text to video frame
                font = cv2.FONT_HERSHEY_SIMPLEX

                # Visualization of the results of a detection.        
                counter, csv_line, counting_mode = vis_util.visualize_boxes_and_labels_on_image_array(cap.get(1),
                                                                                                      input_frame,
                                                                                                      1,
                                                                                                      is_color_recognition_enabled,
                                                                                                      np.squeeze(boxes),
                                                                                                      np.squeeze(classes).astype(np.int32),
                                                                                                      np.squeeze(scores),
                                                                                                      category_index,
                                                                                                      use_normalized_coordinates=True,
                                                                                                      line_thickness=4)
                if(len(counting_mode) == 0):
                    cv2.putText(input_frame, "...", (10, 35), font, 0.8, (0,255,255),2,cv2.FONT_HERSHEY_SIMPLEX)
                else:
                    cv2.putText(input_frame, counting_mode, (10, 35), font, 0.8, (0,255,255),2,cv2.FONT_HERSHEY_SIMPLEX)
                feg = re.findall("\d", str(re.findall("'person:': \d", counting_mode)))
                if len(feg) != 0 and time.time() - last_uploaded >= TIMEOUT_THRESHOLD:
                    feg = int(feg[0])
                    if(feg >= THRESHOLD):
                        cv2.imwrite("Nishant.png", clean_frame)
                        threading.Thread(target=other).start()
                #output_movie.write(input_frame)
                #print ("writing frame")

                feg1 = re.findall("\d", str(re.findall("'car:': \d", counting_mode)))
                ## Not yellow code
                
                if last_light_color == 'g':
                    if time.time() - last_light_change >= LIGHT_THRESHOLD or (len(feg1) >= 1 and int(feg1[0]) < 3):
                        if time.time() - last_light_change >= 4:   
                            light_change('r')
                            last_light_color = 'r'
                            last_light_change = time.time()
                elif last_light_color == 'r':
                    if (len(feg1) >= 1) and (int(feg1[0]) > 2) and time.time():
                        light_change('g')
                        last_light_color = 'g'
                ##
                
                ## Yello code
#                   TODO
                ##
                cv2.imshow('object counting',input_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                if(csv_line != "not_available"):
                        with open('traffic_measurement.csv', 'a') as f:
                                writer = csv.writer(f)                          
                                size, direction = csv_line.split(',')                                             
                                writer.writerows([csv_line.split(',')])         

            cap.release()
            cv2.destroyAllWindows()

