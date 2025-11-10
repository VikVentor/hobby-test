from arduino.app_utils import *
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import os
import json

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

paused = False
MAP_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "label_map.json")
print("Saving to:", os.path.abspath(MAP_FILE))

label_map = {}

try:
    with open(MAP_FILE, "r") as f:
        saved_map = json.load(f)
        for k in saved_map:
            label_map[k.lower()] = saved_map[k]
except FileNotFoundError:
    pass

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

def update_map(data: dict):
    label = data.get("label")
    pos = data.get("pos")
    if not label or not pos:
        return
    label = label.lower()
    label_map[label] = int(pos)
    with open(MAP_FILE, "w") as f:
        json.dump(label_map, f, indent=2)
    print(f"mapping updated and saved: {label} -> {pos}")

ui.on_message("update_map", lambda sid, data: update_map(data))

def send_detections_to_ui(detections: dict):
    global paused
    if paused:
        return

    for key, value in detections.items():
        key_l = key.lower()
        ui.send_message("detection", {
            "content": key,
            "confidence": value.get("confidence"),
            "timestamp": datetime.now(UTC).isoformat()
        })

        if value.get("confidence") * 100 > 85 and key_l in label_map:
            paused = True
            Bridge.notify("stepper", label_map[key_l])

def resume(val: int):
    global paused
    if val == 0:
        paused = False

Bridge.provide("ack", resume)
detection_stream.on_detect_all(send_detections_to_ui)

def add_label(data):
    label = data.get("label")
    if not label:
        return
    label = label.lower()
    if label not in label_map:
        label_map[label] = 1
        with open(MAP_FILE, "w") as f:
            json.dump(label_map, f, indent=2)
        print(f"Added new label: {label}")

def remove_label(data):
    label = data.get("label")
    if not label:
        return
    label = label.lower()
    if label in label_map:
        del label_map[label]
        with open(MAP_FILE, "w") as f:
            json.dump(label_map, f, indent=2)
        print(f"Removed label: {label}")

ui.on_message("add_label", lambda sid, data: add_label(data))
ui.on_message("remove_label", lambda sid, data: remove_label(data))

App.run()
