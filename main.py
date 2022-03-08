import cv2
import time
import HandTrackingModule as htm
import MouseModule as mm


def main():
    mouse = mm.MouseModule()
    cap = cv2.VideoCapture(0)
    prevTime = 0
    CurTime = 0
    detector = htm.ChandDetector(minDetectCon=0.7)
    SendClick = False
    Send2Click = False

    # to store the veclen
    ratioList = []
    fingerRangeLimit = [25, 180]

    colorClicked = (0, 255, 0)
    colorNotClicked = (255, 0, 0)
    colorPressed = (0, 0, 255)

    def drawVideoMouse(image, cx, cy, color=(255, 255, 255), tck=1, lineLen=5):
        height, width = image.shape[:2]
        cv2.line(image, [max(cx - lineLen, 0), cy], [min(cx + lineLen, width), cy], color, tck)
        cv2.line(image, [cx, max(cy - lineLen, 0)], [cx, min(cy + lineLen, height)], color, tck)

    def funcDecision(inputValue, fingerRangeLimit=[0, 100]):
        temp = ((inputValue - fingerRangeLimit[0]) / ((fingerRangeLimit[1] - fingerRangeLimit[0])))
        if temp < 0:
            return 0
        elif temp > 1:
            return fingerRangeLimit[1]
        else:
            return round(temp * 100)

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)

        # class function call to test result
        img = detector.findHands(img, isDraw=False)
        lmList = detector.findPosition(img, isDrawId=False)

        # now we can retrieve the lm position on the img
        # to Test let draw line between top thumbs and top index
        if len(lmList):
            Id0, cx0, cy0 = lmList[htm.LmIndex.THUMB_TIP]
            Id1, cx1, cy1 = lmList[htm.LmIndex.INDEX_FINGER_TIP]
            # cv2.line(img, (cx0, cy0), (cx1, cy1), (0, 0, 255), 5)

            # add other landmark to normalize the value
            Id3, cx3, cy3 = lmList[htm.LmIndex.THUMB_MCP]
            Id4, cx4, cy4 = lmList[htm.LmIndex.INDEX_FINGER_MCP]
            # get the thumbs' lenght and index's lenght
            vecLenThumbs = htm.getVectLen([cx0, cx3], [cy0, cy3])
            vecLenIndex = htm.getVectLen([cx4, cx1], [cy4, cy1])

            # radius shall be proportional to the lenght or vector
            vecLen = htm.getVectLen([cx0, cx1], [cy0, cy1])
            normVecLen = (vecLen / (abs(vecLenThumbs + vecLenIndex) / 2)) * 100

            ratioList.append(normVecLen)
            if len(ratioList) > 4: ratioList.pop(0)
            ratioAverage = sum(ratioList) / len(ratioList)
            ratioAveragead = funcDecision(ratioAverage, fingerRangeLimit)
            radius = int((ratioAveragead / 5) + 1)
            # tickness = int((ratioAveragead/20) + 1)

            # move the mouse
            cmX, cmY = abs(int((cx0 + cx1) / 2)), abs(int((cy0 + cy1) / 2))
            ##########################################################
            height, width = img.shape[:2]
            sX, sY = mm.CoordCamToScreen(cmX, cmY, width, height)
            ##########################################################
            mouse.SetPositionMouse(cmX, cmY)

            # For fun we will get the line center value and display cursor
            if ratioAveragead > 80:
                # cv2.circle(img, [cmX, cmY], radius, colorNotClicked, 5,
                #            lineType=cv2.FILLED)
                drawVideoMouse(img, cmX, cmY, colorNotClicked, 3, radius)

                # if Send2Click == True or SendClick == True:
                #     # do send click
                #     Send2Click = False
                #     SendClick = False
                mouse.SendReleaseInfo(sX, sY)

            elif ratioAveragead > 45:
                # single click
                # cv2.circle(img, [cmX, cmY], radius, colorPressed, 5,
                #            lineType=cv2.FILLED)
                drawVideoMouse(img, cmX, cmY, colorPressed, 3, radius)
                # if SendClick == False:
                #     # do send click
                #     SendClick = True
                mouse.SendPressedInfo(sX, sY)

            else:
                # cv2.circle(img, [cmX, cmY], radius, colorClicked, 5,
                #             #            lineType=cv2.FILLED)
                drawVideoMouse(img, cmX, cmY, colorClicked, 3, radius)
                # if Send2Click == False:
                #     # do send click
                #     Send2Click = True
                mouse.Send2ClickInfo(sX, sY)
        else:
            mouse.SendReleaseInfo(0, 0)

        # fps management to check performance
        CurTime = time.time()
        fps = 1 / (CurTime - prevTime)
        prevTime = CurTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 255), 3)

        cv2.imshow("WebCam Feed", img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
