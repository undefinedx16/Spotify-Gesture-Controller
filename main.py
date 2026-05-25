import cv2
import mediapipe as mp
import keyboard as key
import time

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

prev_gesture = ""
hold_counter = 0
hold_threshold = 12

confirmed_gesture = ""
last_triggered = ""

last_volume_time = 0
volume_delay = 0.3
active_volume_gesture = ""

while True:

     ret, frame = cap.read()
     frame = cv2.flip(frame, 1)
     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
     result = hands.process(rgb)
     gesture = ""
     current_gesture = ""

     if result.multi_hand_landmarks:

          for hand in result.multi_hand_landmarks:

               mp_draw.draw_landmarks(frame,hand,mp_hands.HAND_CONNECTIONS)
               landmarks = hand.landmark
               fingers = []

               # Index
               if landmarks[8].y < landmarks[6].y:
                    fingers.append(1)
               else:
                    fingers.append(0)
               # Middle
               if landmarks[12].y < landmarks[10].y:
                    fingers.append(1)
               else:
                    fingers.append(0)
               # Ring
               if landmarks[16].y < landmarks[14].y:
                    fingers.append(1)
               else:
                    fingers.append(0)
               # Pinky
               if landmarks[20].y < landmarks[18].y:
                    fingers.append(1)
               else:
                    fingers.append(0)

               thumb_tip = landmarks[4].x
               thumb_base = landmarks[2].x


               if thumb_tip > thumb_base + 0.07:
                    current_gesture = "NEXT"

               elif thumb_tip < thumb_base - 0.07:
                    current_gesture = "PREV"
               else:
                    total_fingers = sum(fingers)
                    if total_fingers == 4:
                         current_gesture = "PLAY_PAUSE"
                    index_up = landmarks[8].y < landmarks[6].y
                    middle_up = landmarks[12].y < landmarks[10].y
                    if current_gesture == "":
                         if index_up and not middle_up:
                              current_gesture = "VOL_DOWN"
                         elif index_up and middle_up:
                              current_gesture = "VOL_UP"


               if current_gesture == prev_gesture and current_gesture != "":
                    hold_counter += 1
               else:
                    hold_counter = 0
                    prev_gesture = current_gesture


               if hold_counter >= hold_threshold:
                    confirmed_gesture = current_gesture
                    gesture = confirmed_gesture


               if confirmed_gesture == "VOL_UP":
                    active_volume_gesture = "VOL_UP"
               elif confirmed_gesture == "VOL_DOWN":
                    active_volume_gesture = "VOL_DOWN"
               else:
                    active_volume_gesture = ""


               if confirmed_gesture != "" and confirmed_gesture != last_triggered:

                    if confirmed_gesture == "PLAY_PAUSE":
                         key.send("play/pause media")

                    elif confirmed_gesture == "NEXT":
                         key.send("next track")

                    elif confirmed_gesture == "PREV":
                         key.send("previous track")
                    last_triggered = confirmed_gesture


               current_time = time.time()

               if active_volume_gesture == "VOL_UP":
                    if current_time - last_volume_time > volume_delay:

                         key.press_and_release("volume up")

                         last_volume_time = current_time

               elif active_volume_gesture == "VOL_DOWN":
                    if current_time - last_volume_time > volume_delay:

                         key.press_and_release("volume down")

                         last_volume_time = current_time


               h, w, _ = frame.shape

               x = int(landmarks[0].x * w)
               y = int(landmarks[0].y * h)

               if gesture != "":

                    cv2.putText(frame,
                              gesture,
                              (x, y - 20),
                              cv2.FONT_HERSHEY_SIMPLEX,
                              1,
                              (0, 255, 0),3
                              )

     cv2.imshow("Webcam Feed", frame)

     if cv2.waitKey(1) == 13:
          break

cap.release()
cv2.destroyAllWindows()