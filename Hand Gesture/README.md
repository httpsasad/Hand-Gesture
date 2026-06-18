# ✦ AI-Powered Hand Gesture Air Writing System
### Final Year Project | Computer Vision + Artificial Intelligence

---

## 📌 Project Overview

This project allows users to **write in the air** using their index finger in front of a webcam.
The system uses **MediaPipe** for real-time hand tracking and **Google Gemini AI** to recognize
what you've written. The application mirrors your behavior — as you move your hand, it writes exactly
as you gesture.

---

## 🛠 Technologies Used

| Component        | Technology              |
|-----------------|-------------------------|
| Language         | Python 3.8+             |
| Hand Tracking    | MediaPipe (Google)      |
| Computer Vision  | OpenCV                  |
| AI Recognition   | Google Gemini 1.5 Flash |
| Numerics         | NumPy                   |

---

## ⚡ Installation

### Step 1 — Install Python Libraries
```bash
pip install opencv-python mediapipe google-generativeai numpy pillow
```

### Step 2 — Get FREE Gemini API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

### Step 3 — Add API Key to Code
Open `air_writing_system.py` and on line 42, replace:
```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
```
with your actual key:
```python
GEMINI_API_KEY = "AIzaSy...your_key..."
```

### Step 4 — Run the Project
```bash
python air_writing_system.py
```

---

## 🖐 Hand Gesture Controls

| Gesture                    | Action              |
|---------------------------|---------------------|
| ☛ **Index finger UP**     | ✍️ Draw / Write     |
| ☛ **Index + Middle UP**   | ✋ Pause (move hand) |
| ☛ **All 4 fingers UP**    | 🗑 Clear canvas     |
| ☛ **Fist (closed hand)**  | 🤖 AI Recognize     |
| ☛ **Thumb only UP**       | 🧹 Eraser mode      |
| ☛ **Thumb + Index (pinch)**| 🎨 Next color      |

---

## ⌨ Keyboard Shortcuts

| Key       | Action              |
|----------|---------------------|
| `Q`      | Quit application    |
| `S`      | Save canvas to PNG  |
| `C`      | Clear canvas        |
| `ESC`    | Quit application    |

---

## 📁 Project Structure

```
air_writing_project/
│
├── air_writing_system.py    ← Main program (run this)
└── README.md                ← This file
```

---

## 🎯 How It Works

1. **Camera captures** your hand in real-time (30+ FPS)
2. **MediaPipe** detects 21 hand landmarks per frame
3. **Gesture classifier** checks which fingers are raised
4. **Drawing engine** draws smooth strokes on a transparent canvas
5. **Canvas is blended** with the live camera feed
6. **On fist gesture**, the canvas is sent to **Google Gemini AI**
7. **Gemini reads** the handwriting and displays recognized text

---

## 📊 System Requirements

- Python 3.8 or higher
- Webcam (built-in or USB)
- Internet connection (for AI recognition)
- Good lighting on your hand

---

## 💡 Tips for Best Results

- ✅ Use in **well-lit** environment
- ✅ Keep hand **clearly visible** in frame
- ✅ Write **large letters** for better AI recognition
- ✅ Use **PAUSE gesture** (2 fingers) when repositioning hand
- ✅ After writing, make a **fist** to trigger AI reading
- ❌ Avoid backgrounds similar to skin tone

---

## 👨‍💻 Developed By

**Final Year Project — Computer Science Department**  
Technologies: Python | OpenCV | MediaPipe | Google Gemini AI
