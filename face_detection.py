import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import time
from test_voice_comand import ouvir_comando, aplicar_zoom, retirar_zoom


# ==========================
# CONFIGURAÇÕES
# ==========================
BLINK_THRESHOLD = 5
MIN_BLINK_DURATION = 0.4
DOUBLE_CLICK_THRESHOLD = 0.5
SMOOTHING = 0.2      # menor = mais suave (0.1 a 0.3 ideal)
DEADZONE = 4         # pixels
previous_x = None
previous_y = None

# ==========================
# THREAD DE VOZ
# ==========================
comando_voz = ""

def thread_voz():
    global comando_voz
    while True:
        comando = ouvir_comando()
        if comando:
            comando_voz = comando


# ==========================
# DETECTOR DE PISCADA
# ==========================
class BlinkDetector:
    def __init__(self, threshold=5, min_duration=0.4):
        self.threshold = threshold
        self.min_duration = min_duration
        self.eye_closed = False
        self.blink_start_time = None
        self.last_click_time = None
        self.double_click_threshold = 0.5
        

    def update(self, distance):
        current_time = time.time()

        if distance < self.threshold:
            if not self.eye_closed:
                self.blink_start_time = current_time
                self.eye_closed = True
        else:
            if self.eye_closed:
                blink_duration = current_time - self.blink_start_time

                if blink_duration > self.min_duration:

                    # verifica se é duplo clique
                    if (
                        self.last_click_time is not None and
                        current_time - self.last_click_time < self.double_click_threshold
                    ):
                        pyautogui.doubleClick()
                        self.last_click_time = None  # reseta

                    if blink_duration > 1.0:
                        pyautogui.rightClick()
                    
                    else:
                        pyautogui.click()
                        self.last_click_time = current_time

                self.eye_closed = False


# ==========================
# FUNÇÕES AUXILIARES
# ==========================
def initialize_face_mesh():
    mp_face_mesh = mp.solutions.face_mesh
    return mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True
    )

def euclidean_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def move_mouse(nose, w, h, screen_width, screen_height):
    global previous_x, previous_y

    nose_x, nose_y = nose

    screen_x = np.interp(nose_x, (w/4, w-w/4), (0, screen_width))
    screen_y = np.interp(nose_y, (h/4, h-h/4), (0, screen_height))

    screen_x = max(1, min(screen_width - 1, screen_x))
    screen_y = max(1, min(screen_height - 1, screen_y))

    if previous_x is None:
        previous_x, previous_y = screen_x, screen_y

    smooth_x = previous_x + (screen_x - previous_x) * SMOOTHING
    smooth_y = previous_y + (screen_y - previous_y) * SMOOTHING

    if abs(smooth_x - previous_x) < DEADZONE and abs(smooth_y - previous_y) < DEADZONE:
        return

    pyautogui.moveTo(smooth_x, smooth_y)

    previous_x, previous_y = smooth_x, smooth_y



def extract_face_data(face, w, h):
    upper_lid = (int(face.landmark[159].x * w), int(face.landmark[159].y * h))
    lower_lid = (int(face.landmark[145].x * w), int(face.landmark[145].y * h))
    nose = (int(face.landmark[4].x * w), int(face.landmark[4].y * h))

    return upper_lid, lower_lid, nose


# ==========================
# MAIN
# ==========================
def main():
    global comando_voz

    blink_detector = BlinkDetector(BLINK_THRESHOLD, MIN_BLINK_DURATION)

    face_mesh = initialize_face_mesh()
    screen_width, screen_height = pyautogui.size()

    cap = cv2.VideoCapture(0)

    # inicia thread de voz
    t_voz = threading.Thread(target=thread_voz, daemon=True)
    t_voz.start()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        # ==========================
        # COMANDOS DE VOZ
        # ==========================
        if comando_voz == "aumenta":
            aplicar_zoom()
            comando_voz = ""

        elif comando_voz == "diminui":
            retirar_zoom()
            comando_voz = ""

        # ==========================
        # PROCESSAMENTO DO ROSTO
        # ==========================
        if results.multi_face_landmarks:
            for face in results.multi_face_landmarks:

                upper_lid, lower_lid, nose = extract_face_data(face, w, h)

                # distância da pálpebra
                distance = euclidean_distance(upper_lid, lower_lid)

                # atualizar detector de piscada
                blink_detector.update(distance)

                # mover mouse
                move_mouse(nose, w, h, screen_width, screen_height)

                # desenhar ponto no nariz
                cv2.circle(frame, nose, 5, (0, 255, 0), -1)

        cv2.imshow("Face Mouse Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()