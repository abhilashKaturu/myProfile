import numpy as np
import face_recognition as fr
import cv2

video_capture = cv2.VideoCapture(0)

abhi_image = fr.load_image_file("me.PNG")
abhi_face_encoding = fr.face_encodings(abhi_image)[0]

lokesh_image = fr.load_image_file("lokesh.PNG")
lokesh_face_encoding = fr.face_encodings(lokesh_image)[0]

siri_image = fr.load_image_file("siri.PNG")
siri_face_encoding = fr.face_encodings(siri_image)[0]

mom_image = fr.load_image_file("anusha.PNG")
mom_face_encoding = fr.face_encodings(mom_image)[0]


known_face_encondings = [lokesh_face_encoding, siri_face_encoding, mom_face_encoding, abhi_face_encoding]
known_face_names = ["Lokesh", "Siri", "Anusha", "Abhi"]

while True:
    ret, frame = video_capture.read()

    rgb_frame = frame[:, :, ::-1]

    face_locations = fr.face_locations(rgb_frame)
    face_encodings = fr.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

        matches = fr.compare_faces(known_face_encondings, face_encoding)

        name = "Unknown"

        face_distances = fr.face_distance(known_face_encondings, face_encoding)

        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(frame, (left, bottom - 35),
                      (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    font, 0.5, (255, 255, 255), 1)

    cv2.imshow('Webcam_facerecognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
