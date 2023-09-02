# This is a sample Python script.

import cv2
import numpy as np
from laneData import LaneData
import math

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def findAveragePos(image, lCoord, uCoord):
    #check that coords are within bounds
    lCoord[0] = lCoord[0] if lCoord[0] > 0 else 0
    lCoord[1] = lCoord[1] if lCoord[1] > 0 else 0
    uCoord[0] = uCoord[0] if uCoord[0] > 0 else 0
    uCoord[1] = uCoord[1] if uCoord[1] > 0 else 0
    lCoord[0] = lCoord[0] if lCoord[0] <= image.shape[0] else (image.shape[0] - 1)
    lCoord[1] = lCoord[1] if lCoord[1] <= image.shape[1] else (image.shape[1] - 1)
    uCoord[0] = uCoord[0] if uCoord[0] <= image.shape[0] else (image.shape[0] - 1)
    uCoord[1] = uCoord[1] if uCoord[1] <= image.shape[1] else (image.shape[1] - 1)
    xTotal = 0
    xCount = 0
    yTotal = 0
    yCount = 0
    for x in range(lCoord[0], uCoord[0]):
        for y in range(lCoord[1], uCoord[1]):
            if image[x][y] != 0:
                xTotal += x
                xCount += 1
                yTotal += y
                yCount += 1
    #check if any white pixels were even detected. if not, then just return (0, 0)
    if xCount == 0 or yCount == 0:
        return [0, 0]
    return [int(xTotal / xCount), int(yTotal / yCount)]

def getBottomPos(image, centerPosY, centerPosX):
    while True:
        #check if pixel below is black
        if image[centerPosY+1][centerPosX] == 0:
            #we have reached the bottom row of pixel
            break
        centerPosY += 1
    return (centerPosY, centerPosX)
    #dev = 1
    """
    while True:
        if not image[centerPosY][centerPosX+dev] != 0:
            rightBound = centerPosX+dev
            break
        dev += 1
    dev = 1
    while True:
        if not image[centerPosY][centerPosX - dev] != 0:
            leftBound = centerPosX-dev
            break
        dev += 1

    return (centerPosY, round((rightBound + leftBound)/2))
    """







if __name__ == '__main__':
    # setup coordinates
    # TODO - take coords as input instead of hardcoding them
    imageCoords = [[844, 672], [1267, 602], [336, 96], [407, 95]]
    # get adjusted coordinates for when the video is reformatted
    leftShift = imageCoords[2][0]
    upShift = imageCoords[3][1]
    # shift every coord by the left shift and the upshift
    adjustedCoords = [[imageCoords[0][0] - leftShift, imageCoords[0][1] - upShift],
                      [imageCoords[1][0] - leftShift, imageCoords[1][1] - upShift],
                      [imageCoords[2][0] - leftShift, imageCoords[2][1] - upShift],
                      [imageCoords[3][0] - leftShift, imageCoords[3][1] - upShift]]

    #Initialize the laneTracker
    #coords are in format [x, y] in the order bottomLeft, bottomRight, topLeft, topRight
    lane = LaneData(adjustedCoords)
    ballPos = []
    video = cv2.VideoCapture("videoTest.mp4")
    print(video.isOpened())
    lowerBound = [0, 0]
    upperBound = [0, 0]
    frameCount = 0
    searchArea = 1000
    #setup the video writer
    #out = cv2.VideoWriter('outpy4.avi', cv2.VideoWriter_fourcc(*"MJPG"), 10, (720, 1280))




    #new main video loop
    currentState = 1
    #1 is searching phase, 2 is tracking phase
    while video.isOpened():
        #coord order goes bottom left, bottom right, top left, top right
        #There are 2 different phases;
        #1. searching phase, check the designated "bar" for updates, once it is found, switch to tracking phase
        #2. tracking phase, follow ball untill it isnt detected. switch to searching phase after detection is lost
        #3. error phase, unrecoverable error
        if currentState == 1:
            #get image from feed
            ret, image = video.read()
            if not ret:
                print("image could not be grabbed from video feed.")
                currentState = 3
                break


            #crop image down to area around bowling lane to save time on conversion
            #for now, this assumes that the camera is placed to the left of the
            #TODO - add checks to determine which coordinate is the farthest in each direction
            image = image[imageCoords[3][1]:imageCoords[0][1]][imageCoords[2][0]:imageCoords[1][0]]

            #convert image with filter
            #TODO - adjust filter based on user input
            cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL, image)
            image2 = cv2.inRange(image, np.array([240, 100, 100]), np.array([270, 255, 255]))

            #scan accross search line
            detectedPos = lane.scanLine(image2)
            if detectedPos == -1:
                continue
            #define search area based on ball location and then shift to tracking phase
            lowerBound =




    #test loop
    while video.isOpened():

        frameCount += 1
        #open frame and check if image is available
        ret, image = video.read()
        if not ret:
            print('ret came back false')
            break

        #TEMP - skip the first few frames so we get the ball actually on the lane
        if frameCount < 20:
            continue

        #prepare image for processing
        image = image[80:][:]
        cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL, image)
        image2 = cv2.inRange(image, np.array([240, 100, 100]), np.array([270, 255, 255]))

        #find center pos of circle
        prevCenterPos = findAveragePos(image2, lowerBound, upperBound)
        while True:
            newCenterPos = findAveragePos(image2, [prevCenterPos[0] - searchArea, prevCenterPos[1] - searchArea], [prevCenterPos[1] + searchArea, prevCenterPos[1] + searchArea])

            if (abs(prevCenterPos[0] - newCenterPos[0]) < 1) and (abs(prevCenterPos[1] - newCenterPos[1]) < 1) and searchArea <= 100:
                break
            prevCenterPos = newCenterPos
            if searchArea > 100:
                searchArea = int(searchArea / 1.5)
        #store coordinates
        print(f'frame {frameCount} has been calculated')
        searchArea = 50
        lowerBound = [prevCenterPos[0] - 25, prevCenterPos[1] - 25]
        upperBound = [prevCenterPos[0] + 25, prevCenterPos[1] + 25]
        print(newCenterPos)
        bottomPosition = getBottomPos(image2, newCenterPos[0], newCenterPos[1])
        realPos = lane.getRealPosition((bottomPosition[1], bottomPosition[0] + 80))
        print(realPos)
        ballPos.append([frameCount, realPos[0], realPos[1]])

        if frameCount > 320:
        #show picture with coordinates and save to video out
            cv2.rectangle(image, (bottomPosition[1] - 5, bottomPosition[0] - 5), (bottomPosition[1] + 5, bottomPosition[0] + 5), (0, 0, 0), -1)
            cv2.imshow("Image", image2)
            cv2.imshow("Image1", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        #out.write(image)


    print(ballPos)
    video.release()
    #out.release()
