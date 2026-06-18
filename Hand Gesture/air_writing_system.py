"""
╔══════════════════════════════════════════════════════════════════╗
║        AI-POWERED HAND GESTURE AIR WRITING SYSTEM               ║
║        Final Year Project - Computer Vision + AI                 ║
║        Compatible: mediapipe 0.10.30+                            ║
╚══════════════════════════════════════════════════════════════════╝

GESTURES:
  Index finger only     → DRAW
  Index + Middle        → PAUSE (move without drawing)
  All 4 fingers up      → CLEAR canvas
  Fist (all closed)     → AI RECOGNIZE
  Thumb only            → ERASE
  Thumb + Index pinch   → NEXT COLOR

SETUP:
  python -m pip install opencv-python mediapipe google-generativeai numpy pillow

  Free Gemini API key: https://makersuite.google.com/app/apikey
"""

import cv2
import numpy as np
import time
from collections import deque

# ─────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────

GEMINI_API_KEY  = "YOUR_GEMINI_API_KEY_HERE"
USE_AI          = GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE"

CAMERA_INDEX    = 0
CANVAS_ALPHA    = 0.75
BRUSH_SIZE      = 8
ERASER_SIZE     = 45
SMOOTHING       = 6
SHOW_LANDMARKS  = True

COLORS = {
    "White" : (255, 255, 255),
    "Cyan"  : (255, 220,   0),
    "Green" : (  0, 230,  80),
    "Yellow": (  0, 255, 255),
    "Orange": (  0, 150, 255),
    "Pink"  : (180,  60, 255),
}
COLOR_NAMES  = list(COLORS.keys())
COLOR_VALUES = list(COLORS.values())


# ─────────────────────────────────────────────────────────────────
#  AI RECOGNITION
# ─────────────────────────────────────────────────────────────────

def recognize_with_ai(canvas_img):
    if not USE_AI:
        return "AI OFF — Add Gemini API key in GEMINI_API_KEY variable"
    try:
        import google.generativeai as genai
        from PIL import Image
        genai.configure(api_key=GEMINI_API_KEY)
        model    = genai.GenerativeModel("gemini-1.5-flash")
        img_rgb  = cv2.cvtColor(canvas_img, cv2.COLOR_BGR2RGB)
        pil_img  = Image.fromarray(img_rgb)
        response = model.generate_content([
            "This image shows handwriting drawn in the air with a finger. "
            "Recognize and transcribe exactly what is written or drawn. "
            "Reply with ONLY the recognized text or description.",
            pil_img
        ])
        return response.text.strip()
    except ImportError:
        return "Install google-generativeai: python -m pip install google-generativeai"
    except Exception as e:
        return f"AI Error: {str(e)[:70]}"


# ─────────────────────────────────────────────────────────────────
#  HAND DETECTOR — NEW MEDIAPIPE 0.10.30+ API
# ─────────────────────────────────────────────────────────────────

class HandDetector:
    def __init__(self):
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        import os, urllib.request
        model_path = "hand_landmarker.task"
        if not os.path.exists(model_path):
            print("  Downloading hand landmark model (~8MB)...")
            url = ("https://storage.googleapis.com/mediapipe-models/"
                   "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")
            urllib.request.urlretrieve(url, model_path)
            print("  Model downloaded!")

        base_opts = mp_python.BaseOptions(model_asset_path=model_path)
        opts = mp_vision.HandLandmarkerOptions(
            base_options=base_opts,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        self.landmarker = mp_vision.HandLandmarker.create_from_options(opts)
        self.mp = mp
        self.ts_ms = 0

    def detect(self, frame_bgr):
        import mediapipe as mp
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.ts_ms += 33
        result = self.landmarker.detect_for_video(mp_image, self.ts_ms)
        return result

    def get_finger_states(self, landmarks):
        TIP   = [4,  8, 12, 16, 20]
        PIP   = [3,  6, 10, 14, 18]
        states = []
        states.append(landmarks[TIP[0]].x < landmarks[PIP[0]].x)
        for i in range(1, 5):
            states.append(landmarks[TIP[i]].y < landmarks[PIP[i]].y)
        return states

    def get_gesture(self, fingers):
        t, i, m, r, p = fingers
        if     i and not m and not r and not p:              return "DRAW"
        if     i and     m and not r and not p:              return "PAUSE"
        if     i and     m and     r and     p:              return "CLEAR"
        if not t and not i and not m and not r and not p:    return "RECOGNIZE"
        if     t and not i and not m and not r and not p:    return "ERASE"
        if     t and     i and not m and not r and not p:    return "COLOR"
        return "NONE"

    def get_index_tip(self, landmarks, frame_shape):
        h, w = frame_shape[:2]
        lm = landmarks[8]
        return int(lm.x * w), int(lm.y * h)

    def draw_hand(self, frame, landmarks_list):
        if not landmarks_list:
            return
        h, w = frame.shape[:2]
        connections = [
            (0,1),(1,2),(2,3),(3,4),
            (0,5),(5,6),(6,7),(7,8),
            (5,9),(9,10),(10,11),(11,12),
            (9,13),(13,14),(14,15),(15,16),
            (13,17),(17,18),(18,19),(19,20),(0,17)
        ]
        lms = landmarks_list[0]
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in lms]
        for a, b in connections:
            cv2.line(frame, pts[a], pts[b], (80, 180, 80), 1, cv2.LINE_AA)
        for pt in pts:
            cv2.circle(frame, pt, 3, (0, 255, 100), -1, cv2.LINE_AA)


# ─────────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────────

class AirWritingApp:
    def __init__(self):
        self.detector = HandDetector()

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Camera not found! Check CAMERA_INDEX.")

        h, w = frame.shape[:2]
        self.canvas       = np.zeros((h, w, 3), dtype=np.uint8)
        self.smooth_q     = deque(maxlen=SMOOTHING)
        self.prev_pt      = None
        self.color_idx    = 0
        self.gesture      = "NONE"
        self.ai_result    = ""
        self.ai_thinking  = False
        self.fps_q        = deque(maxlen=30)
        self.prev_time    = time.time()
        self._cd          = {"RECOGNIZE": 0, "COLOR": 0, "CLEAR": 0}

        print("\n" + "="*58)
        print("  AI AIR WRITING SYSTEM — READY")
        print("="*58)
        print(f"  Resolution : {w} x {h}")
        print(f"  AI Mode    : {'ENABLED (Gemini)' if USE_AI else 'DISABLED'}")
        print()
        print("  GESTURES:")
        print("   Index finger   = Draw")
        print("   Index + Middle = Pause")
        print("   All 4 fingers  = Clear canvas")
        print("   Fist           = AI Recognize")
        print("   Thumb only     = Erase")
        print("   Thumb + Index  = Next color")
        print()
        print("  KEYS: Q = quit | S = save | C = clear")
        print("="*58 + "\n")

    @property
    def color(self):
        return COLOR_VALUES[self.color_idx % len(COLOR_VALUES)]

    @property
    def color_name(self):
        return COLOR_NAMES[self.color_idx % len(COLOR_NAMES)]

    def smooth(self, pt):
        self.smooth_q.append(pt)
        return (
            int(sum(p[0] for p in self.smooth_q) / len(self.smooth_q)),
            int(sum(p[1] for p in self.smooth_q) / len(self.smooth_q)),
        )

    def cooldown_ok(self, key, secs):
        now = time.time()
        if now - self._cd[key] > secs:
            self._cd[key] = now
            return True
        return False

    def draw_hud(self, frame):
        h, w = frame.shape[:2]

        bar = frame.copy()
        cv2.rectangle(bar, (0, 0), (w, 76), (15, 15, 20), -1)
        cv2.addWeighted(bar, 0.75, frame, 0.25, 0, frame)

        now = time.time()
        self.fps_q.append(1.0 / max(now - self.prev_time, 0.001))
        self.prev_time = now
        fps = sum(self.fps_q) / len(self.fps_q)
        cv2.putText(frame, f"FPS {fps:.0f}", (18, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 100), 2)

        G_COL = {
            "DRAW": (0, 255, 100), "PAUSE": (0, 240, 255),
            "ERASE": (50, 120, 255), "CLEAR": (50, 60, 255),
            "RECOGNIZE": (255, 160, 30), "COLOR": (255, 60, 220),
            "NONE": (100, 100, 100),
        }
        cv2.putText(frame, self.gesture, (18, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    G_COL.get(self.gesture, (160, 160, 160)), 2)

        cx = w // 2
        cv2.circle(frame, (cx, 38), 20, self.color, -1)
        cv2.circle(frame, (cx, 38), 20, (200, 200, 200), 1)
        cv2.putText(frame, self.color_name, (cx + 28, 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (210, 210, 210), 1)

        cv2.putText(frame, "AIR WRITING SYSTEM", (w - 295, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (170, 170, 255), 2)
        cv2.putText(frame, "Final Year Project",  (w - 245, 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 200), 1)

        if self.ai_result or self.ai_thinking:
            panel_y = h - 58
            panel = frame.copy()
            cv2.rectangle(panel, (0, panel_y), (w, h), (18, 18, 38), -1)
            cv2.addWeighted(panel, 0.82, frame, 0.18, 0, frame)
            cv2.line(frame, (0, panel_y), (w, panel_y), (90, 90, 200), 1)

            if self.ai_thinking:
                dots = "." * (int(time.time() * 2.5) % 4)
                cv2.putText(frame, f"AI Recognizing{dots}", (18, panel_y + 36),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.78, (80, 200, 255), 2)
            else:
                cv2.putText(frame, "AI:", (18, panel_y + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 180, 255), 1)
                disp = self.ai_result[:100] + ("..." if len(self.ai_result) > 100 else "")
                cv2.putText(frame, disp, (18, panel_y + 46),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)

        guide = [("INDEX", "Draw"), ("2 FINGERS", "Pause"),
                 ("ALL UP", "Clear"), ("FIST", "AI Read"), ("THUMB", "Erase")]
        for idx, (g, lbl) in enumerate(guide):
            cv2.putText(frame, f"{g}: {lbl}", (w - 170, 100 + idx * 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 170), 1)

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame  = cv2.flip(frame, 1)
            result = self.detector.detect(frame)

            if result.hand_landmarks:
                lms     = result.hand_landmarks[0]
                fingers = self.detector.get_finger_states(lms)
                self.gesture = self.detector.get_gesture(fingers)
                tip_x, tip_y = self.detector.get_index_tip(lms, frame.shape)

                if self.gesture == "DRAW":
                    sp = self.smooth((tip_x, tip_y))
                    if self.prev_pt:
                        cv2.line(self.canvas, self.prev_pt, sp,
                                 self.color, BRUSH_SIZE, cv2.LINE_AA)
                    self.prev_pt = sp
                    cv2.circle(frame, (tip_x, tip_y),
                               BRUSH_SIZE // 2 + 2, self.color, -1)

                elif self.gesture == "PAUSE":
                    self.prev_pt = None
                    self.smooth_q.clear()
                    cv2.circle(frame, (tip_x, tip_y), 14, (0, 240, 255), 2)

                elif self.gesture == "ERASE":
                    sp = self.smooth((tip_x, tip_y))
                    if self.prev_pt:
                        cv2.line(self.canvas, self.prev_pt, sp,
                                 (0, 0, 0), ERASER_SIZE)
                    self.prev_pt = sp
                    cv2.circle(frame, (tip_x, tip_y), ERASER_SIZE // 2,
                               (100, 100, 120), 2)

                elif self.gesture == "CLEAR":
                    if self.cooldown_ok("CLEAR", 1.5):
                        self.canvas[:] = 0
                        self.ai_result = ""
                        self.prev_pt   = None
                        print("  Canvas cleared")

                elif self.gesture == "RECOGNIZE":
                    if self.cooldown_ok("RECOGNIZE", 3.0):
                        self.ai_thinking = True
                        self.prev_pt = None
                        print("  Sending to AI...")
                        canvas_copy      = self.canvas.copy()
                        self.ai_result   = recognize_with_ai(canvas_copy)
                        self.ai_thinking = False
                        print(f"  AI: {self.ai_result}")

                elif self.gesture == "COLOR":
                    if self.cooldown_ok("COLOR", 1.0):
                        self.color_idx = (self.color_idx + 1) % len(COLORS)
                        self.prev_pt   = None
                        print(f"  Color: {self.color_name}")

                else:
                    self.prev_pt = None

                if SHOW_LANDMARKS:
                    self.detector.draw_hand(frame, result.hand_landmarks)

            else:
                self.gesture = "NONE"
                self.prev_pt = None
                self.smooth_q.clear()

            mask    = self.canvas.astype(bool)
            blended = frame.copy()
            blended[mask] = (
                self.canvas[mask] * CANVAS_ALPHA +
                frame[mask]       * (1 - CANVAS_ALPHA)
            ).astype(np.uint8)
            frame = blended

            self.draw_hud(frame)
            cv2.imshow("AI Air Writing System — Final Year Project", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break
            elif key == ord('s'):
                fname = f"canvas_{int(time.time())}.png"
                cv2.imwrite(fname, self.canvas)
                print(f"  Saved: {fname}")
            elif key == ord('c'):
                self.canvas[:] = 0
                self.ai_result = ""
                print("  Canvas cleared")

        self.cap.release()
        cv2.destroyAllWindows()
        print("  Closed.")


# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║   AI-POWERED HAND GESTURE AIR WRITING — STARTING...     ║
╚══════════════════════════════════════════════════════════╝
""")
    try:
        app = AirWritingApp()
        app.run()
    except RuntimeError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Stopped.")
