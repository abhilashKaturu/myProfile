import cv2
import numpy as np
import face_recognition as fr
import os
import datetime
import csv
import pyrebase

#Basically get all images from images folder into a list myList
path = 'images'
images = []
imgNames = []
myList = os.listdir(path)

for i in myList:
    curImg = cv2.imread(f'{path}/{i}')
    #appends the img object to the images list
    images.append(curImg)
    #appends the name of the person to the imgNames list
    imgNames.append(os.path.splitext(i)[0])

print(imgNames)




def findEncodings(images):
    '''
    Creates face encodings for all the image objects in the parameter's list
    '''
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = fr.face_encodings(img)[0]
        encodeList.append(encode)
    
    return encodeList

def addToFire():
    #if there are 2 attendance files, upload the older one to firebase and delete it
    myL = os.listdir()
    
    #if there are not two sheets in the attendence_sheets folder ignore
    if not len(myL)>3:
        return
    
    myL.sort()

    toRemove = myL.pop(0)
    
    #cofigure firebase settings
    config = {
        "apiKey": "AIzaSyAwNGIqhT-gEGTGqx0AWTOIE0HwGv8lJOI",
        'authDomain': "face-recognition-f9743.firebaseapp.com",
        'databaseURL': "https://face-recognition-f9743-default-rtdb.firebaseio.com",
        'projectId': "face-recognition-f9743",
        'storageBucket': "face-recognition-f9743.appspot.com",
        'messagingSenderId': "525842819963",
        'appId': "1:525842819963:web:de347284d38f545c6aabde",
        'measurementId': "G-C74S1SSPFP"
    }

    #create object firebase, database, and storage
    firebase = pyrebase.initialize_app(config)

    database = firebase.database()
    storage = firebase.storage()

    #add a child to the storage in firebase storage
    storage.child(f"{toRemove}").put(toRemove)
    #get the url of where the file is stored in firebase storage
    url=storage.child(toRemove).get_url(None)

    #add date and the url to a new child in firebase db
    data = {"Date":toRemove[11:21], "Attendance File URL":url}
    database.child("Attendance Sheet Storage").push(data)

    #remove file from directory

    os.remove(f"{toRemove}")
    
    



def markAttendance(name):
    addToFire()
    try:
        with open(f'Attendance_{datetime.date.today()}.csv', 'r+') as f:
            myDataList = f.readlines()
            nameList = []
            #read the file
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            
            #add name if name not in list
            if (name not in nameList) and (name != "Unknown"):
                now = datetime.datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'{name}, {dtString}\n')
        
    except FileNotFoundError:
        
        with open(f'Attendance_{datetime.date.today()}.csv', 'w+') as f:
            writer = csv.writer(f)

            #write the header
            writer.writerow(['Name', 'Time'])

            #write the data
            now = datetime.datetime.now()
            dtString = now.strftime('%H:%M:%S')
            writer.writerow([name, dtString])

#call function to get a list of all face encodings
encodeListKnown = findEncodings(images)
print("Encodings Completed")

#capture webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    #another way of converting from BGR to RGB
    rgb_frame = frame[:, :, ::-1]

    face_locations = fr.face_locations(rgb_frame)
    face_encodings = fr.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

        matches = fr.compare_faces(encodeListKnown, face_encoding)

        name = "Unknown"

        #check "how far" the faces are from each other
        face_distances = fr.face_distance(encodeListKnown, face_encoding)

        #find the one with the lowest "distance"
        best_match_index = np.argmin(face_distances)
        # check if that face matches with the face on the webcam
        if matches[best_match_index]:
            name = imgNames[best_match_index]

        #draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(frame, (left, bottom - 35),
                      (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_SIMPLEX
        #put name
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    font, 0.5, (255, 255, 255), 1)
    
        #Mark the attendance
        markAttendance(name)

    cv2.imshow('Webcam_facerecognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



cv2.destroyAllWindows()
    


