from controller import Supervisor
from ultralytics import YOLO
import cv2

def detect(class_name: str, supervisor: Supervisor):
    camera = supervisor.getDevice('camera')
    if not camera: return False

    model  = YOLO('v8n2.pt')
    camera.saveImage('img.png', 50)
    img = cv2.imread('img.png')

    results = model.predict(source = img, conf = 0.5)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            c = box.cls
            if class_name.lower() == model.names[int(c)].lower():
                return True
    return False

