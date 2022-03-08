import enum
import cv2
import mediapipe as mp
import time
import numpy as np


# copy and rename from original mediapipe hand to use on module lib
class LmIndex(enum.IntEnum):
    """The 21 hand landmarks."""
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


# add vector function
def getVectLen(cx=[], cy=[]):
    x = np.array(cx)
    y = np.array(cy)
    dist_array = (x[:-1] - x[1:]) ** 2 + (y[:-1] - y[1:]) ** 2
    return np.sum(np.sqrt(dist_array))


class ChandDetector:
    def __init__(self, mode=False, maxHands=2, complexity=1, minDetectCon=0.5, minTrackCon=0.5):
        self.results = None
        self.mode = mode
        self.maxHands = maxHands
        self.complexity = complexity
        self.minDetectCon = minDetectCon
        self.minTrackCon = minTrackCon
        # init the media pipe hands module
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.complexity, self.minDetectCon, self.minTrackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, isDraw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # loop on the number of hands
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if isDraw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, isDrawId=True):
        # create the landmarks list to return
        lmList = []
        if self.results.multi_hand_landmarks:
            try:
                myHand = self.results.multi_hand_landmarks[handNo]
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = img.shape  # get img info
                    # convert the landmark x and y to the position in pixel on the img
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                    if isDrawId:
                        cv2.putText(img, str(int(id)), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
            except:
                print("findPosition: Error....")

        return lmList


def main():
    cap = cv2.VideoCapture(0)
    prevTime = 0
    CurTime = 0
    detector = ChandDetector()

    while True:
        success, img = cap.read()

        # class function call to test result
        img = detector.findHands(img, isDraw=False)
        lmList = detector.findPosition(img, isDrawId=False)

        # now we can retrieve the lm position on the img
        # to Test let draw line between top thumbs and top index
        if len(lmList):
            Id0, cx0, cy0 = lmList[LmIndex.THUMB_TIP]
            Id1, cx1, cy1 = lmList[LmIndex.INDEX_FINGER_TIP]
            cv2.line(img, (cx0, cy0), (cx1, cy1), (0, 0, 255), 5)
            # For fun we will get the line center value and display cursor
            cv2.circle(img, [abs(int((cx0 + cx1) / 2)), abs(int((cy0 + cy1) / 2))], 5, (0, 255, 0), 5, cv2.FILLED)

        # fps management to check performance
        CurTime = time.time()
        fps = 1 / (CurTime - prevTime)
        prevTime = CurTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 255), 3)

        cv2.imshow("WebCam Feed", img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
