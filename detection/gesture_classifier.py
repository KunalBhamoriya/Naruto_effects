"""
Gesture classifier for Naruto jutsu hand poses.
Uses geometric rules on MediaPipe hand landmarks to classify gestures.
"""

from utils.math_utils import distance
from detection.hand_detector import HandDetector
import config


class GestureClassifier:
    """Classifies hand gestures into Naruto jutsu types using geometric analysis."""

    # Gesture constants
    NONE = "NONE"
    RASENGAN = "RASENGAN"
    CHIDORI = "CHIDORI"
    RASENSHURIKEN = "RASENSHURIKEN"

    def __init__(self):
        self.gesture_history = []
        self.current_stable_gesture = self.NONE
        self.stability_count = 0

    def _is_finger_extended(self, landmarks, finger_tip_idx, finger_mcp_idx, palm_size):
        """
        Check if a finger is extended by comparing the tip-to-wrist distance
        vs the MCP-to-wrist distance. Extended fingers have tips far from wrist.
        """
        wrist = landmarks[HandDetector.WRIST]
        tip = landmarks[finger_tip_idx]
        mcp = landmarks[finger_mcp_idx]

        tip_dist = distance(tip, wrist)
        mcp_dist = distance(mcp, wrist)

        # Finger is extended if tip is significantly farther from wrist than MCP
        return tip_dist > mcp_dist * config.FINGER_EXTENDED_RATIO + palm_size * 0.15

    def _is_thumb_extended(self, landmarks, palm_size):
        """Check if thumb is extended (uses different logic due to thumb orientation)."""
        thumb_tip = landmarks[HandDetector.THUMB_TIP]
        thumb_mcp = landmarks[HandDetector.THUMB_MCP]
        index_mcp = landmarks[HandDetector.INDEX_MCP]

        # Thumb is extended if its tip is far from index finger MCP
        thumb_dist = distance(thumb_tip, index_mcp)
        return thumb_dist > palm_size * 0.5

    def _count_extended_fingers(self, landmarks, palm_size):
        """
        Count how many fingers are extended.
        Returns a list of booleans [thumb, index, middle, ring, pinky].
        """
        fingers = []

        # Thumb
        fingers.append(self._is_thumb_extended(landmarks, palm_size))

        # Index finger
        fingers.append(self._is_finger_extended(
            landmarks, HandDetector.INDEX_TIP, HandDetector.INDEX_MCP, palm_size))

        # Middle finger
        fingers.append(self._is_finger_extended(
            landmarks, HandDetector.MIDDLE_TIP, HandDetector.MIDDLE_MCP, palm_size))

        # Ring finger
        fingers.append(self._is_finger_extended(
            landmarks, HandDetector.RING_TIP, HandDetector.RING_MCP, palm_size))

        # Pinky finger
        fingers.append(self._is_finger_extended(
            landmarks, HandDetector.PINKY_TIP, HandDetector.PINKY_MCP, palm_size))

        return fingers

    def _is_cupped_hand(self, landmarks, palm_size):
        """
        Check if the hand is in a cupped position (like holding an invisible ball).
        Fingertips should be partially curled — not fully extended, not fully closed.
        """
        palm_center_x = sum(
            landmarks[i][0] for i in [
                HandDetector.WRIST, HandDetector.INDEX_MCP,
                HandDetector.MIDDLE_MCP, HandDetector.RING_MCP,
                HandDetector.PINKY_MCP
            ]
        ) / 5
        palm_center_y = sum(
            landmarks[i][1] for i in [
                HandDetector.WRIST, HandDetector.INDEX_MCP,
                HandDetector.MIDDLE_MCP, HandDetector.RING_MCP,
                HandDetector.PINKY_MCP
            ]
        ) / 5
        palm_center = (palm_center_x, palm_center_y)

        fingertip_indices = [
            HandDetector.INDEX_TIP, HandDetector.MIDDLE_TIP,
            HandDetector.RING_TIP, HandDetector.PINKY_TIP,
        ]

        # Calculate average distance of fingertips to palm center
        avg_tip_dist = sum(
            distance(landmarks[idx], palm_center) for idx in fingertip_indices
        ) / len(fingertip_indices)

        # Normalized by palm size
        ratio = avg_tip_dist / (palm_size + 1e-6)

        # Cupped = fingertips are at an intermediate distance (not flat, not fist)
        return config.CUPPED_HAND_MIN_RATIO < ratio < config.CUPPED_HAND_MAX_RATIO

    def _is_chidori_gesture(self, landmarks, palm_size):
        """
        Check for Chidori gesture: index and middle fingers extended,
        ring and pinky closed.
        """
        fingers = self._count_extended_fingers(landmarks, palm_size)
        # Index and Middle extended, Ring and Pinky NOT extended
        return (fingers[1] and fingers[2] and not fingers[3] and not fingers[4])

    def _is_open_palm(self, landmarks, palm_size):
        """
        Check if the hand is an open palm.
        Fingers are extended open facing the camera.
        Checks that at least index, middle, ring, pinky are extended,
        or at least 4 out of 5 fingers are extended.
        """
        fingers = self._count_extended_fingers(landmarks, palm_size)
        four_main = fingers[1] and fingers[2] and fingers[3] and fingers[4]
        return four_main or sum(fingers) >= 4

    def _is_all_fingers_extended(self, landmarks, palm_size):
        """Check if all fingers are extended (open hand)."""
        return self._is_open_palm(landmarks, palm_size)

    def classify(self, hands_data, frame_width):
        """
        Classify the current gesture from detected hands data.

        Args:
            hands_data: List of hands, each containing 21 (x, y) landmarks.
            frame_width: Width of the frame (for distance normalization).

        Returns:
            dict with keys:
                - 'gesture': str (NONE, RASENGAN, CHIDORI, RASENSHURIKEN)
                - 'palm_centers': list of (x, y) palm centers
                - 'fingertips': list of fingertip positions per hand
                - 'landmarks': the raw landmarks
                - 'confidence': stability count / required frames
        """
        result = {
            'gesture': self.NONE,
            'palm_centers': [],
            'fingertips': [],
            'landmarks': hands_data,
            'confidence': 0.0,
        }

        if not hands_data:
            self._update_stability(self.NONE)
            result['confidence'] = self._get_confidence()
            result['gesture'] = self.current_stable_gesture
            return result

        # Calculate palm info for all hands without re-instantiating detector
        palm_centers = []
        palm_sizes = []
        all_fingertips = []

        for hand in hands_data:
            pc = HandDetector.get_palm_center(hand)
            ps = HandDetector.get_palm_size(hand)
            ft = HandDetector.get_fingertip_positions(hand)
            palm_centers.append(pc)
            palm_sizes.append(ps)
            all_fingertips.append(ft)

        result['palm_centers'] = palm_centers
        result['fingertips'] = all_fingertips

        detected_gesture = self.NONE

        # 1. Check Rasenshuriken first (requires 2 hands open)
        if len(hands_data) >= 2:
            hand1_open = self._is_open_palm(hands_data[0], palm_sizes[0])
            hand2_open = self._is_open_palm(hands_data[1], palm_sizes[1])
            hands_dist = distance(palm_centers[0], palm_centers[1])
            max_dist = frame_width * config.RASENSHURIKEN_MAX_HAND_DISTANCE_RATIO

            if hand1_open and hand2_open and hands_dist < max_dist:
                detected_gesture = self.RASENSHURIKEN

        # 2. Check single-hand gestures across visible hands
        if detected_gesture == self.NONE:
            for i, hand in enumerate(hands_data):
                palm_size = palm_sizes[i]

                # Check Chidori (two fingers extended: index + middle)
                if self._is_chidori_gesture(hand, palm_size):
                    detected_gesture = self.CHIDORI
                    # Put this hand's palm center first so effects attach to it
                    if i > 0:
                        result['palm_centers'][0], result['palm_centers'][i] = (
                            result['palm_centers'][i], result['palm_centers'][0]
                        )
                        result['fingertips'][0], result['fingertips'][i] = (
                            result['fingertips'][i], result['fingertips'][0]
                        )
                    break

                # Check Rasengan (one hand open palm)
                elif self._is_open_palm(hand, palm_size):
                    detected_gesture = self.RASENGAN
                    if i > 0:
                        result['palm_centers'][0], result['palm_centers'][i] = (
                            result['palm_centers'][i], result['palm_centers'][0]
                        )
                        result['fingertips'][0], result['fingertips'][i] = (
                            result['fingertips'][i], result['fingertips'][0]
                        )
                    break

        self._update_stability(detected_gesture)
        result['gesture'] = self.current_stable_gesture
        result['confidence'] = self._get_confidence()

        return result

    def _update_stability(self, gesture):
        """
        Update gesture stability tracking.
        A gesture must be detected for GESTURE_STABILITY_FRAMES consecutive
        frames before it becomes the active gesture.
        """
        self.gesture_history.append(gesture)
        if len(self.gesture_history) > config.GESTURE_STABILITY_FRAMES * 2:
            self.gesture_history = self.gesture_history[-config.GESTURE_STABILITY_FRAMES * 2:]

        # Check if the last N frames all agree
        recent = self.gesture_history[-config.GESTURE_STABILITY_FRAMES:]
        if len(recent) >= config.GESTURE_STABILITY_FRAMES and all(g == gesture for g in recent):
            self.current_stable_gesture = gesture
            self.stability_count = config.GESTURE_STABILITY_FRAMES
        else:
            # Count how many of the recent frames match the most common gesture
            if recent:
                self.stability_count = sum(1 for g in recent if g == gesture)

    def _get_confidence(self):
        """Get confidence as a ratio of stability count to required frames."""
        return min(1.0, self.stability_count / config.GESTURE_STABILITY_FRAMES)
