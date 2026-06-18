<div align="center">

# ✋ AI Hand Gesture Air Writing System

**Write in the air with your finger — a webcam reads your hand, MediaPipe tracks it, and Google Gemini reads what you wrote.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange.svg)
![Gemini](https://img.shields.io/badge/Google%20Gemini-AI%20Recognition-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

</div>

---

## Overview

This project turns a regular webcam into a virtual whiteboard. Raise your index finger and start writing in mid-air — the system tracks your hand in real time with **MediaPipe**, renders your strokes onto a live canvas with **OpenCV**, and, with a single gesture (a closed fist), sends what you wrote to **Google Gemini** for handwriting recognition.

No stylus, no touchscreen, no mouse — just your hand and a camera.

---

## Features

- **Real-time hand tracking** at 30+ FPS using MediaPipe's hand landmark model (21 points per hand)
- **Gesture-based controls** — no buttons or menus, everything is driven by finger positions
- **AI handwriting recognition** powered by Gemini 1.5 Flash
- **Smooth, jitter-free strokes** via a moving-average smoothing filter
- **Multi-color drawing** with a quick pinch gesture to cycle colors
- **Eraser mode** for fixing mistakes without clearing the whole canvas
- **Live HUD** showing FPS, current gesture, active color, and AI output
- **Save your canvas** as a PNG at any time

---

## Demo Gestures

| Gesture | Fingers Raised | Action |
|---|---|---|
| ✍️ **Draw** | Index only | Draws on the canvas |
| ✋ **Pause** | Index + Middle | Lifts the pen — move freely without drawing |
| 🗑️ **Clear** | All four fingers | Wipes the canvas |
| 🤖 **AI Recognize** | Fist (none raised) | Sends the canvas to Gemini for reading |
| 🧹 **Erase** | Thumb only | Erases a small area around your fingertip |
| 🎨 **Next Color** | Thumb + Index pinch | Cycles to the next brush color |

**Keyboard shortcuts:** `Q` / `Esc` to quit · `S` to save the canvas as PNG · `C` to clear

---

## How It Works

1. **Capture** — OpenCV grabs frames from your webcam.
2. **Track** — MediaPipe's `HandLandmarker` detects 21 landmarks on your hand per frame.
3. **Classify** — The app checks which fingers are extended and maps that combination to a gesture.
4. **Draw** — While in "Draw" mode, the index fingertip position is smoothed and connected into strokes on a persistent canvas layer.
5. **Blend** — The canvas is alpha-blended over the live camera feed so you can see your writing and your hand at once.
6. **Recognize** — On a fist gesture, the current canvas image is sent to the Gemini API, which transcribes the handwriting and returns the text.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.8+ |
| Hand Tracking | [MediaPipe](https://developers.google.com/mediapipe) (Hand Landmarker, Tasks API) |
| Computer Vision | OpenCV |
| AI Recognition | Google Gemini 1.5 Flash |
| Numerics | NumPy |

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A webcam (built-in or USB)
- Internet connection (only required for AI recognition)
- A free Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Install dependencies

```bash
pip install opencv-python mediapipe google-generativeai numpy pillow
```

### 3. Get a free Gemini API key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key** and copy it

### 4. Add your API key

Open `air_writing_system.py` and replace the placeholder:

```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```

with your actual key:

```python
GEMINI_API_KEY = "AIzaSy...your_key..."
```

> The app also runs without a key — drawing, erasing, color switching, and clearing all work offline. Only AI recognition needs the key.

### 5. Run it

```bash
python air_writing_system.py
```

The hand landmark model (`hand_landmarker.task`, ~8 MB) is downloaded automatically on first run if it isn't already present in the project folder.

---

## Project Structure

```
air-writing-system/
├── air_writing_system.py   # Main application — run this
├── hand_landmarker.task    # MediaPipe hand landmark model
└── README.md               # This file
```

---

## Tips for Best Results

- Use the app in a **well-lit** room
- Keep your hand **fully visible** within the camera frame
- Write **large, clear letters** to help the AI recognize them accurately
- Use the **Pause gesture** (index + middle) whenever you need to reposition your hand without drawing
- Avoid backgrounds that closely match your skin tone, which can confuse tracking

---

## Roadmap

- [ ] Multi-hand support for two-handed gestures
- [ ] On-screen color palette picker
- [ ] Export recognized text directly to a `.txt` file
- [ ] Support for additional AI backends (OpenAI, local OCR)

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

Built with Python, OpenCV, MediaPipe, and Google Gemini AI.

</div># Hand-Gesture
