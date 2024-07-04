from io import BytesIO
import json
import cv2
import numpy as np
from custom.classes import CalibrationData
from custom.functions import get_img_from_file
from typing import Tuple
import json
import cv2


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def get_camera_data(api_key: str, images, chessboard_size: Tuple[int]) -> CalibrationData:
    extracted_images = [get_img_from_file(raw_img) for raw_img in images]
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((chessboard_size[0] *  chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

    obj_points = []
    image_points = []

    for img in extracted_images:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        if ret == True:
            obj_points.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            image_points.append(corners)
            cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)


    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, image_points, gray.shape[::-1], None, None)
    
    var = {}
    for variable in ['ret', 'mtx', 'dist', 'rvecs', 'tvecs']:
        var[variable] = eval(variable)

    json_str = json.dumps(var, cls=NumpyEncoder)
    json_dict = json.loads(json_str)

    data = CalibrationData(
        ret=json_dict["ret"],
        mtx=json_dict["mtx"],
        dist=json_dict["dist"],
        rvecs=json_dict["rvecs"],
        tvecs=json_dict["tvecs"]
    )
    return data


def get_undistorted_image_bytes(api_key: str, calibration_data: str, img):
    calib_obj = CalibrationData(**json.loads(calibration_data))

    real_img = get_img_from_file(img)
    h, w = real_img.shape[:2]

    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(np.array(calib_obj.mtx), np.array(calib_obj.dist), (w, h), 0, (w, h))
    dst = cv2.undistort(real_img, np.array(calib_obj.mtx), np.array(calib_obj.dist), None, new_camera_matrix)
    
    _, encoded_res = cv2.imencode(".png", dst)
    return BytesIO(encoded_res.tobytes())