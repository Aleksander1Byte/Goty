import cv2
from random import randint


def get_preview(video_file) -> str:
    """Возвращает название временного файла"""
    cap = cv2.VideoCapture(video_file)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    msecs = int(frames * fps)
    cap.set(cv2.CAP_PROP_POS_MSEC, randint(0, msecs))
    success, image = cap.read()
    if success:
        cv2.imwrite('temp_img.jpg', image)
        cv2.waitKey()
        return 'temp_img.jpg'
