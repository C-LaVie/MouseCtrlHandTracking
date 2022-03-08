from pynput.mouse import Button, Controller
import time
from win32api import GetSystemMetrics


def CoordCamToScreen(cx, cy, videoW, videoH):
    # This function will translate hte coordinate from video space to screen space
    # if ratio is 1, the raw data are correct, but if the video is bigger or more likely smaller than screen resolution
    # the mouse will move only around a small postion, so we can try to map the position to the screen
    # warning, bigger th eratio is, lesser the precision will be
    sreenW = GetSystemMetrics(0)
    screenH = GetSystemMetrics(1)
    ratioW = sreenW / videoW
    ratioH = screenH / videoH
    return int(cx*ratioW), int(cy*ratioH)


class MouseModule:
    def __init__(self, delay=5):
        self.mouse = Controller()
        # self.isClick = False
        self.isPress = False
        self.is2Click = False
        self.updateT = time.time_ns()
        self.threshold = delay * 1000000  # ms

    def Send2ClickInfo(self, cx, cy):
        if not self.is2Click:
            self.is2Click = True
            print(f"Click Detected: [{cx} , {cy}]")
            self.mouse.release(Button.left)
            self.mouse.click(Button.left, 2)

    def SendPressedInfo(self, cx, cy):
        if not self.isPress:
            self.isPress = True
            print(f"Click Detected: [{cx} , {cy}]")
            self.mouse.release(Button.left)
            self.mouse.press(Button.left)

    def SendReleaseInfo(self, cx, cy):
        if self.is2Click or self.isPress:
            self.is2Click = False
            self.isPress = False
            print(f"Click Release: [{cx} , {cy}]")
            self.mouse.release(Button.left)

    def SetPositionMouse(self, cx, cy):
        nowT = time.time_ns()
        if nowT - self.updateT > self.threshold:
            # Set pointer position
            self.updateT = nowT
            self.mouse.position = (cx, cy)
            # print("mouse moved to {0}".format(self.mouse.position))

