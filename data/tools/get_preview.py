import cv2
from random import randint


def get_preview(video_file) -> str:
    """Возвращает название временного файла с случайным кадром из видео"""
    cap = cv2.VideoCapture(video_file)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    msecs = int(frames * fps)
    cap.set(cv2.CAP_PROP_POS_MSEC, randint(1000, msecs - 1))  # проблема где-то тут
    success, image = cap.read()
    if success:
        name = f'{randint(1, msecs)}.jpg'
        cv2.imwrite(name, image)
        cv2.waitKey()
        return name
