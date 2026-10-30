"""
🍥 Naruto Power Effects — Main Application
==========================================
Real-time hand gesture recognition with Naruto-style visual effects.

Controls:
    Q / ESC  — Quit
    L        — Toggle landmark visibility
    F        — Toggle FPS display
    G        — Toggle gesture label
    M        — Toggle camera mirror
    R        — Reset effects

Gestures:
    🔵 Rasengan      — Cupped palm (like holding a ball)
    ⚡ Chidori        — Index + Middle fingers extended, others closed
    💨 Rasenshuriken  — Both hands open with all fingers spread
"""

import cv2
import time
import sys
import os

# Fix Unicode output on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

import config
from detection.hand_detector import HandDetector
from detection.gesture_classifier import GestureClassifier
from effects.rasengan import RasenganEffect
from effects.chidori import ChidoriEffect
from effects.rasenshuriken import RasenshurikenEffect
from utils.drawing import put_text_with_shadow


def main():
    """Main application loop."""
    print("=" * 60)
    print("  NARUTO POWER EFFECTS")
    print("  Hand Gesture Recognition with Jutsu Visual Effects")
    print("=" * 60)
    print()
    print("  Controls:")
    print("    Q / ESC  - Quit")
    print("    L        - Toggle landmarks")
    print("    F        - Toggle FPS")
    print("    G        - Toggle gesture label")
    print("    M        - Toggle mirror")
    print("    R        - Reset effects")
    print()
    print("  Gestures:")
    print("    Open palm (one hand) -> [BLUE] Rasengan")
    print("    Two fingers extended -> [ELECTRIC BLUE] Chidori")
    print("    Both hands open      -> [WHITE/BLUE] Rasenshuriken")
    print()

    # ─── Initialize Camera ──────────────────────────────────────
    print("[INFO] Opening camera...")
    cap = cv2.VideoCapture(config.CAMERA_INDEX)

    if not cap.isOpened():
        print("[ERROR] Could not open camera! Check if webcam is connected.")
        print("        Try changing CAMERA_INDEX in config.py (0, 1, 2...)")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Camera resolution: {actual_w}x{actual_h}")

    # ─── Initialize Detection ───────────────────────────────────
    print("[INFO] Initializing hand detector (MediaPipe)...")
    detector = HandDetector()
    classifier = GestureClassifier()

    # ─── Initialize Effects ─────────────────────────────────────
    effects = {
        GestureClassifier.RASENGAN: RasenganEffect(),
        GestureClassifier.CHIDORI: ChidoriEffect(),
        GestureClassifier.RASENSHURIKEN: RasenshurikenEffect(),
    }

    # ─── Display Settings (toggleable) ──────────────────────────
    show_landmarks = config.SHOW_LANDMARKS
    show_fps = config.SHOW_FPS
    show_gesture = config.SHOW_GESTURE_LABEL
    flip_camera = config.FLIP_CAMERA

    # ─── FPS Tracking ───────────────────────────────────────────
    fps = 0
    frame_times = []
    prev_time = time.time()

    # ─── Gesture Info for Display ───────────────────────────────
    gesture_display_info = {
        GestureClassifier.NONE: {"name": "No Gesture", "color": (150, 150, 150)},
        GestureClassifier.RASENGAN: {"name": "RASENGAN", "color": (255, 180, 50)},
        GestureClassifier.CHIDORI: {"name": "CHIDORI", "color": (255, 225, 70)},
        GestureClassifier.RASENSHURIKEN: {"name": "RASENSHURIKEN", "color": (255, 230, 160)},
    }

    print("[INFO] Ready! Show your hand to the camera.")
    print()

    # ─── Create Window Explicitly (fixes invisible window on Windows) ──
    cv2.namedWindow(config.WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(config.WINDOW_NAME, actual_w, actual_h)
    cv2.moveWindow(config.WINDOW_NAME, 100, 50)
    # Bring window to foreground
    cv2.setWindowProperty(config.WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(1)
    cv2.setWindowProperty(config.WINDOW_NAME, cv2.WND_PROP_TOPMOST, 0)

    # ─── Main Loop ──────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame from camera.")
            break

        # Mirror the frame
        if flip_camera:
            frame = cv2.flip(frame, 1)

        frame_h, frame_w = frame.shape[:2]

        # ─── Hand Detection ─────────────────────────────────────
        hands_data = detector.detect(frame)

        # ─── Gesture Classification ─────────────────────────────
        result = classifier.classify(hands_data, frame_w)
        current_gesture = result['gesture']
        palm_centers = result['palm_centers']
        fingertips = result['fingertips']
        confidence = result['confidence']

        # ─── Activate/Deactivate Effects ─────────────────────────
        for gesture_name, effect in effects.items():
            if current_gesture == gesture_name:
                effect.activate()
            else:
                effect.deactivate()

        # ─── Update & Render Effects ─────────────────────────────
        for effect in effects.values():
            effect.update(palm_centers, fingertips, frame.shape)
            effect.render(frame)

        # ─── Draw Landmarks (optional) ───────────────────────────
        if show_landmarks:
            detector.draw_landmarks(frame)

        # ─── Draw UI Overlay ─────────────────────────────────────
        if show_gesture and current_gesture != GestureClassifier.NONE:
            info = gesture_display_info[current_gesture]

            # Gesture name
            put_text_with_shadow(
                frame, info["name"],
                (frame_w // 2 - len(info["name"]) * 12, 50),
                font_scale=1.2,
                color=info["color"],
                thickness=3
            )

            # Confidence bar
            bar_width = 200
            bar_x = frame_w // 2 - bar_width // 2
            bar_y = 65
            bar_height = 8
            # Background
            cv2.rectangle(frame, (bar_x, bar_y),
                          (bar_x + bar_width, bar_y + bar_height),
                          (50, 50, 50), -1)
            # Fill
            fill_width = int(bar_width * confidence)
            cv2.rectangle(frame, (bar_x, bar_y),
                          (bar_x + fill_width, bar_y + bar_height),
                          info["color"], -1)
            # Border
            cv2.rectangle(frame, (bar_x, bar_y),
                          (bar_x + bar_width, bar_y + bar_height),
                          (100, 100, 100), 1)

        # ─── FPS Counter ──────────────────────────────────────────
        current_time = time.time()
        frame_times.append(current_time - prev_time)
        prev_time = current_time

        # Average over last 30 frames
        if len(frame_times) > 30:
            frame_times = frame_times[-30:]
        avg_frame_time = sum(frame_times) / len(frame_times)
        fps = 1.0 / (avg_frame_time + 1e-6)

        if show_fps:
            fps_color = (0, 255, 0) if fps >= 25 else (0, 165, 255) if fps >= 15 else (0, 0, 255)
            put_text_with_shadow(
                frame, f"FPS: {int(fps)}",
                (15, 35),
                font_scale=0.7,
                color=fps_color,
                thickness=2
            )

        # ─── Hand count indicator ─────────────────────────────────
        hand_count = len(hands_data)
        if hand_count > 0:
            put_text_with_shadow(
                frame, f"Hands: {hand_count}",
                (15, frame_h - 20),
                font_scale=0.6,
                color=(200, 200, 200),
                thickness=1
            )

        # ─── Controls hint ───────────────────────────────────────
        put_text_with_shadow(
            frame, "Q: Quit | L: Landmarks | R: Reset",
            (frame_w - 380, frame_h - 20),
            font_scale=0.5,
            color=(120, 120, 120),
            thickness=1
        )

        # ─── Display ─────────────────────────────────────────────
        cv2.imshow(config.WINDOW_NAME, frame)

        # ─── Key Handling ────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key in (ord('q'), 27):  # Q or ESC
            print("[INFO] Quitting...")
            break
        elif key == ord('l'):
            show_landmarks = not show_landmarks
            print(f"[INFO] Landmarks: {'ON' if show_landmarks else 'OFF'}")
        elif key == ord('f'):
            show_fps = not show_fps
            print(f"[INFO] FPS display: {'ON' if show_fps else 'OFF'}")
        elif key == ord('g'):
            show_gesture = not show_gesture
            print(f"[INFO] Gesture label: {'ON' if show_gesture else 'OFF'}")
        elif key == ord('m'):
            flip_camera = not flip_camera
            print(f"[INFO] Mirror: {'ON' if flip_camera else 'OFF'}")
        elif key == ord('r'):
            for effect in effects.values():
                effect.deactivate()
            print("[INFO] Effects reset.")

    # ─── Cleanup ─────────────────────────────────────────────────
    print("[INFO] Cleaning up...")
    detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Done. Dattebayo! 🍥")


if __name__ == "__main__":
    main()
