import cv2
import mediapipe as mp
import pyautogui
import numpy as np


def initialize_face_mesh():
    mp_face_mesh = mp.solutions.face_mesh
    return mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

def get_screen_size():
    return pyautogui.size()

def euclidean_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def detect_face_landmarks(face_mesh, frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return face_mesh.process(rgb_frame)

def process_face_landmarks(face, w, h, screen_width, screen_height, frame):
    right_eye_landmarks = [33, 160, 158, 133, 153, 144]
    eye_points = [(int(face.landmark[l].x * w), int(face.landmark[l].y * h)) for l in right_eye_landmarks]
    
    for i in range(len(eye_points)):
        cv2.line(frame, eye_points[i], eye_points[(i + 1) % len(eye_points)], (0, 255, 0), 1)

    left_eye_landmarks = [362, 385, 387, 263, 373, 380]
    left_eye_points = [(int(face.landmark[l].x * w), int(face.landmark[l].y * h)) for l in left_eye_landmarks]
    for i in range(len(left_eye_points)):
        cv2.line(frame, left_eye_points[i], left_eye_points[(i + 1) % len(left_eye_points)], (0, 255, 0), 1)
    
    upper_lid = (int(face.landmark[159].x * w), int(face.landmark[159].y * h))
    lower_lid = (int(face.landmark[145].x * w), int(face.landmark[145].y * h))
    
    if euclidean_distance(upper_lid, lower_lid) < 5:
        pyautogui.click()
    


    nose_x, nose_y = int(face.landmark[4].x * w), int(face.landmark[4].y * h)
    screen_x = np.interp(nose_x, (0+w/4, w-w/4), (0, screen_width))
    screen_y = np.interp(nose_y, (0+h/4, h-h/4), (0, screen_height))
    pyautogui.moveTo(screen_x, screen_y, duration=0.05)
    
    return nose_x, nose_y

def main():
    face_mesh = initialize_face_mesh()
    screen_width, screen_height = get_screen_size()
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        results = detect_face_landmarks(face_mesh, frame)
        
        if results.multi_face_landmarks:
            for face in results.multi_face_landmarks:
                nose_x, nose_y = process_face_landmarks(face, w, h, screen_width, screen_height, frame)
                cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 0), -1)
                
        cv2.imshow("Face Mouse Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()