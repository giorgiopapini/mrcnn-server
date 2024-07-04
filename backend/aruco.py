import cv2
import numpy as np
from custom.functions import get_img_from_file

def get_pixel_cm_ratio(aruco_perim_cm: float, image) -> float:
    real_img = get_img_from_file(image)

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
    parameters =  cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    corners, _, _ = detector.detectMarkers(real_img)
    internal_corners = np.int0(corners)
    #cv2.polylines(real_img, internal_corners, True, (0, 255, 0), 2)
    aruco_perim_pixel: float = cv2.arcLength(corners[0], True)
    #cv2.imshow("aruco_detected", real_img)
    #cv2.waitKey(0)

    return aruco_perim_pixel / aruco_perim_cm
