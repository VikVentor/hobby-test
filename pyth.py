# SPDX-FileCopyrightText: Copyright (C) 2025 ARDUINO SA <http://www.arduino.cc>
#
# SPDX-License-Identifier: MPL-2.0

from arduino.app_utils import *
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import time

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

paused = False
label_map = {
    "esp32": 1,
    "servo": 2,
    "motor": 3,
    "wheel": 4,
    "sensor": 5
}

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
