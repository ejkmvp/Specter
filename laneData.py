import cv2
import numpy as np
#"""
class LaneData:
    # coords are in format [x, y] in the order bottomLeft, bottomRight, topLeft, topRight
    trans = None
    reverseTrans = None
    slope = None
    scanListStartPos = None
    def __init__(self, imageCoords):
        self.trans = cv2.getPerspectiveTransform(np.float32([imageCoords[0], imageCoords[1], imageCoords[2], imageCoords[3]]), np.float32([[0, 720], [42, 720], [0, 0], [42, 0]]))
        self.reverseTrans = cv2.getPerspectiveTransform(np.float32([[0, 720], [42, 720], [0, 0], [42, 0]]), np.float32([imageCoords[0], imageCoords[1], imageCoords[2], imageCoords[3]]))
        self.imageCoords = imageCoords

        #prepare scanline location
        #use coordinates at base of lane to get slope
        #TODO - write this code to account for multiple camera angle possibilities

        self.slope = (imageCoords[1][1] - imageCoords[0][1]) / (imageCoords[1][0] - imageCoords[0][0])
        #put scanline 20 feet
        self.scanLineStartPos = self.getReversePosition(0, 20).reverse()
        self.scanLineEndX = self.getReversePosition(42, 20)[1]




        #self.trans = cv2.getPerspectiveTransform(np.float32([[844,672], [1267,602], [336,94], [407,95]]), np.float32([[0, 720], [42, 720], [0, 0], [42, 0]]))


    def getRealPosition(self, coords):
        #coord format is [] idk tbh
        if self.trans is None:
            return [0, 0]
        newX = (self.trans[0][0]*coords[0] + self.trans[0][1]*coords[1] + self.trans[0][2])/(self.trans[2][0]*coords[0] + self.trans[2][1]*coords[1] + self.trans[2][2])
        newY = (self.trans[1][0] * coords[0] + self.trans[1][1] * coords[1] + self.trans[1][2]) / (self.trans[2][0] * coords[0] + self.trans[2][1] * coords[1] + self.trans[2][2])
        return [newX, newY]

    def getReversePosition(self, coords):
        #coord format is [x, y]
        if self.reverseTrans is None:
            return [0, 0]
        newX = (self.reverseTrans[0][0]*coords[0] + self.reverseTrans[0][1]*coords[1] + self.reverseTrans[0][2])/(self.reverseTrans[2][0]*coords[0] + self.reverseTrans[2][1]*coords[1] + self.reverseTrans[2][2])
        newY = (self.reverseTrans[1][0] * coords[0] + self.reverseTrans[1][1] * coords[1] + self.reverseTrans[1][2]) / (self.reverseTrans[2][0] * coords[0] + self.reverseTrans[2][1] * coords[1] + self.reverseTrans[2][2])
        return [newX, newY]

    def scanLine(self, image):
        #returns in [x, y] format or -1 if no ball was found
        #TODO account for the slope being greater than 1
        #TODO account for different camera angles
        #TODO make the scan area more than 1 pixel wide
        reverseSlope = int(1/self.slope)
        scanPos = self.scanLineStartPos
        xTotal = 0
        xCount = 0
        finished = 0 # nasty way to escape form multiple loops without separate methods
        #scan the image and populate xTotal and xCount
        while True:
            for x in range(reverseSlope):
                # check if we've reached the end of the lane
                if scanPos[0] + x > self.scanLineEndX:
                    finished = 1
                    break
                #check if the pixel is white
                if image[scanPos[1]][scanPos[0] + x] != 0:
                    xTotal += scanPos[0] + x
                    xCount += 1
            if finished:
                break
            scanPos[1] -= 1

        #check if any white pixels were found at all
        #TODO use a (clean slate) shot to adjust this minimum white pixel check
        if xCount <= 0: #this may be adjusted to account for noise
            return -1
        centerXPos = int(xTotal/xCount)

        #TODO account for the difference in y coord when returning the center coord
        return [centerXPos, self.scanLineStartPos[1]]


    def scanSegment(self, image):




        pass
#"""




if __name__ == "__main__":
    image = cv2.imread("detectionImage.png")
    #image = image[80:][:]

    #cv2.circle(image, (844, 672), 12, (255, 255, 255), -1)
    #cv2.circle(image, (1267, 602), 12, (255, 255, 255), -1)
    #cv2.circle(image, (336, 94), 12, (255, 255, 255), -1)
    #cv2.circle(image, (407, 95), 12, (255, 255, 255), -1)


    trans = cv2.getPerspectiveTransform(np.float32([[844,672], [1267,602], [336,94], [407,95]]), np.float32([[0, 720], [42, 720], [0, 0], [42, 0]]))
    out = cv2.warpPerspective(image, trans, (42, 720))
    testLane = LaneData(np.float32([[844,672], [1267,602], [336,94], [407,95]]))
    reverseCoords = testLane.getReversePosition([20, 519])
    print(reverseCoords)
    cv2.circle(image, (int(reverseCoords[0]), int(reverseCoords[1])), 6, (255, 255, 255), -1)
    cv2.circle(out, (20, 519), 6, (255, 255, 255), -1)
    cv2.imshow("Image", out)
    cv2.imshow("Image1", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

