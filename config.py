"""
Configuration settings for the Naruto Power Effects app.
Adjust thresholds, colors, and visual parameters here.
"""

# ─── Camera Settings ──────────────────────────────────────────────
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# ─── MediaPipe Hand Detection ────────────────────────────────────
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.6

# ─── Gesture Detection Thresholds ────────────────────────────────
# Finger is considered "extended" if tip-to-mcp distance exceeds this
# ratio relative to the palm size (wrist-to-middle-finger-mcp distance)
FINGER_EXTENDED_RATIO = 0.55

# Cupped hand: fingertip-to-palm distance ratio (lower = more curled)
CUPPED_HAND_MAX_RATIO = 0.75
CUPPED_HAND_MIN_RATIO = 0.3

# Minimum frames a gesture must be stable before activating the effect
GESTURE_STABILITY_FRAMES = 4

# Max distance between two palm centers for Rasenshuriken (as ratio of frame width)
RASENSHURIKEN_MAX_HAND_DISTANCE_RATIO = 0.5

# ─── Colors (BGR format for OpenCV) ──────────────────────────────
# Rasengan colors (Blue middle, White outer border)
RASENGAN_CORE_COLOR = (255, 130, 15)        # Vibrant electric chakra blue in the middle
RASENGAN_MID_COLOR = (245, 90, 0)           # Rich chakra blue
RASENGAN_BORDER_COLOR = (255, 255, 255)     # Crisp white outer border
RASENGAN_OUTER_COLOR = (255, 245, 230)      # White-blue aura glow
RASENGAN_PARTICLE_COLOR = (255, 170, 50)    # Blue chakra particles

# Chidori colors (Electric Blue)
CHIDORI_CORE_COLOR = (255, 255, 255)        # Pure white lightning core
CHIDORI_ARC_COLOR = (255, 225, 70)          # Electric cyan-blue arcs (BGR)
CHIDORI_SPARK_COLOR = (255, 240, 150)       # Electric blue sparks
CHIDORI_GLOW_COLOR = (255, 175, 25)         # Intense electric blue glow

# Rasenshuriken colors (Blue middle, White outer border & blades)
RASENSHURIKEN_CORE_COLOR = (255, 130, 15)   # Vivid chakra blue in the middle
RASENSHURIKEN_BLADE_COLOR = (250, 250, 250) # Pure white wind blades
RASENSHURIKEN_BORDER_COLOR = (255, 255, 255)# Crisp pure white borders
RASENSHURIKEN_WIND_COLOR = (255, 220, 180)  # White-cyan wind particles
RASENSHURIKEN_GLOW_COLOR = (255, 245, 230)  # Brilliant white-blue glow

# ─── Effect Parameters ───────────────────────────────────────────
# Rasengan (Enlarged size)
RASENGAN_BASE_RADIUS = 95
RASENGAN_PULSE_AMPLITUDE = 14
RASENGAN_PULSE_SPEED = 0.15
RASENGAN_NUM_PARTICLES = 55
RASENGAN_ORBIT_SPEED = 0.08
RASENGAN_GLOW_RADIUS = 165

# Chidori (Enlarged Electric Blue)
CHIDORI_NUM_ARCS = 14
CHIDORI_ARC_SEGMENTS = 8
CHIDORI_ARC_MAX_LENGTH = 200
CHIDORI_SPARK_COUNT = 30
CHIDORI_FLICKER_RATE = 2  # Rapid lightning flicker
CHIDORI_GLOW_RADIUS = 135

# Rasenshuriken (Enlarged size)
RASENSHURIKEN_CORE_RADIUS = 65
RASENSHURIKEN_BLADE_LENGTH = 230
RASENSHURIKEN_BLADE_WIDTH = 50
RASENSHURIKEN_NUM_BLADES = 4
RASENSHURIKEN_SPIN_SPEED = 0.12
RASENSHURIKEN_WIND_PARTICLES = 75
RASENSHURIKEN_GLOW_RADIUS = 260

# ─── Particle System ─────────────────────────────────────────────
PARTICLE_MAX_LIFETIME = 40       # Frames before particle dies
PARTICLE_FADE_START = 0.6        # Start fading at this % of lifetime
PARTICLE_MIN_SIZE = 1
PARTICLE_MAX_SIZE = 4

# ─── Smoothing ────────────────────────────────────────────────────
POSITION_SMOOTHING = 0.3  # Lower = smoother but more lag (0.0 - 1.0)
EFFECT_FADE_IN_SPEED = 0.08
EFFECT_FADE_OUT_SPEED = 0.12

# ─── Display ──────────────────────────────────────────────────────
SHOW_LANDMARKS = False           # Show MediaPipe hand skeleton
SHOW_FPS = True                 # Show FPS counter
SHOW_GESTURE_LABEL = True       # Show detected gesture name
FLIP_CAMERA = True              # Mirror the camera feed
WINDOW_NAME = "Naruto Power Effects"
