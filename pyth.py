# SPDX-FileCopyrightText: Copyright (C) 2025 ARDUINO SA <http://www.arduino.cc>
#
# SPDX-License-Identifier: MPL-2.0

from arduino.app_utils import *
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import time
import json
import os

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

def handle_find(label):
    print(f"Find triggered for label: {label}")
    if label in label_map:
        print("sending ", label_map[label])
        Bridge.notify("stepper", label_map[label])

ui.on_message("find", lambda sid, data: handle_find(data["label"]))


paused = False

label_map_path = os.path.join(os.path.dirname(__file__), "..", "assets", "label_map.json")
print(label_map_path)
with open(label_map_path, "r") as f:
    label_map = json.load(f)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

def send_detections_to_ui(detections: dict):
    global paused
    if paused:
        return
    for key, value in detections.items():
        ui.send_message("detection", {
            "content": key,
            "confidence": value.get("confidence"),
            "timestamp": datetime.now(UTC).isoformat()
        })
        if value.get("confidence") * 100 > 85 and key in label_map:
            paused = True
            Bridge.notify("stepper", label_map[key])

def resume(val: int):
    global paused
    if val == 0:
        paused = False

Bridge.provide("ack", resume)
detection_stream.on_detect_all(send_detections_to_ui)

App.run()
