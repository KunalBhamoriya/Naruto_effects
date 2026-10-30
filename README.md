# 🍥 Naruto Power Effects

A real-time Computer Vision application that tracks hand gestures via your webcam and overlays high-performance Naruto jutsu visual effects (**Rasengan**, **Chidori**, and **Rasenshuriken**) directly on your hands.

Powered by **Python**, **OpenCV**, and **Google MediaPipe**.

---

## ⚡ Features & Hand Signs

| Jutsu | Hand Sign | Visual Effect |
|---|---|---|
| 🔵 **Rasengan** | **One open palm** facing camera | Large spinning electric blue chakra orb with a crisp white border ring and orbiting chakra particles. |
| ⚡ **Chidori** | **Two fingers extended** (Index + Middle / peace sign pointing forward) | Massive crackling electric cyan-blue lightning arcs branching from fingertips with a flickering white core and spark particles. |
| 💨 **Rasenshuriken** | **Both hands open**, fingers spread wide | Giant four-bladed spinning wind shuriken spanning between both hands with pure white wind blades and a blue core. |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **MediaPipe (Tasks API)** — Real-time 21 hand landmark detection running on CPU.
- **OpenCV (`cv2`)** — Video capture, rendering, localized alpha blending, and particle visualization.
- **NumPy** — Vector math, distance calculations, and particle physics.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed on your system.
- A working webcam.

---

### 2. Setup Virtual Environment

#### On Windows (PowerShell):
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

*(If PowerShell gives an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

#### On macOS / Linux:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. MediaPipe Model File

The project requires the `hand_landmarker.task` model file in the root folder. If it is not already present, download it using Python:

```bash
python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task', 'hand_landmarker.task'); print('Model downloaded successfully!')"
```

---

### 5. Run the Application

```bash
python main.py
```

---

## 🎮 Keyboard Controls

While the camera window is focused:

| Key | Action |
|---|---|
| **`Q`** or **`ESC`** | Quit application |
| **`L`** | Toggle hand skeleton landmarks (On/Off) |
| **`F`** | Toggle FPS counter display |
| **`G`** | Toggle jutsu banner text |
| **`M`** | Toggle camera mirroring (flip horizontally) |
| **`R`** | Reset / deactivate current active effects |

---

## ⚙️ Customization (`config.py`)

All visual parameters, thresholds, and colors can be adjusted in [`config.py`](config.py):

- **Camera Resolution:** Modify `CAMERA_WIDTH` and `CAMERA_HEIGHT` (defaults to `1280x720`).
- **Effect Sizes:**
  - `RASENGAN_BASE_RADIUS`: Size of the Rasengan orb.
  - `RASENSHURIKEN_BLADE_LENGTH` & `RASENSHURIKEN_CORE_RADIUS`: Dimensions of the Rasenshuriken.
  - `CHIDORI_ARC_MAX_LENGTH` & `CHIDORI_NUM_ARCS`: Scale and density of Chidori lightning arcs.
- **Colors (BGR Format):** Customize colors for cores, borders, glow auras, and sparks.
- **Detection Stability:** `GESTURE_STABILITY_FRAMES` sets the number of consecutive frames required before activating an effect (prevents flickering).

---

## 📂 Project Structure

```
Naruto/
├── main.py                     # Application entry point & camera loop
├── config.py                   # Central settings, sizes, and color palettes
├── requirements.txt            # Python dependencies
├── hand_landmarker.task        # MediaPipe vision model file
│
├── detection/
│   ├── hand_detector.py        # MediaPipe Tasks HandLandmarker wrapper
│   └── gesture_classifier.py   # Geometric rules for recognizing hand signs
│
├── effects/
│   ├── base_effect.py          # Abstract effect base class with opacity fading
│   ├── particle.py             # Particle physics engine (orbits, bursts, fades)
│   ├── rasengan.py             # Rasengan visual effect renderer
│   ├── chidori.py              # Chidori lightning & spark renderer
│   └── rasenshuriken.py        # Rasenshuriken multi-blade renderer
│
└── utils/
    ├── drawing.py              # Localized ROI glow, blades, lightning arcs, text
    └── math_utils.py           # Vectors, interpolation, angles, distances
```

---

## 💡 Troubleshooting

- **Low FPS / Stutter:** Ensure you are in a well-lit room. The app uses downsampled inference and localized ROI blending to maintain 30–60 FPS on standard CPUs.
- **Camera Not Opening:** If you have multiple webcams, change `CAMERA_INDEX = 0` to `1` or `2` in `config.py`.
- **Window Not Appearing on Windows:** Click the taskbar icon if the OpenCV window opens behind other active windows.
