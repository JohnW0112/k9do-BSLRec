from collections import deque
import numpy as np

class SequenceBuffer:
    def __init__(self, max_length=30):
        """
        Stores a sliding window of skeleton frames.

        :param max_length: Maximum number of frames to keep in buffer.
        """
        self.buffer = deque(maxlen=max_length)

    def append(self, skeleton_frame):
        """
        Append a new frame to the buffer.

        :param skeleton_frame: Dictionary with keys 'pose', 'left_hand', 'right_hand'.
                               Each value is a NumPy array or None.
        """
        self.buffer.append(skeleton_frame)

    def is_full(self):
        """
        Check if the buffer is full.

        :return: True if buffer is full, False otherwise.
        """
        return len(self.buffer) == self.buffer.maxlen

    def clear(self):
        """
        Clear the buffer.
        """
        self.buffer.clear()

    def get_sequence(self, flatten=True):
        """
        Get the full sequence from the buffer.

        :param flatten: If True, returns a sequence of flattened vectors.
        :return: Numpy array of shape (sequence_len, feature_dim)
        """
        sequence = []
        for frame in self.buffer:
            features = []

            # Pose (33 keypoints * 4 = 132)
            if frame['pose'] is not None:
                features.extend(frame['pose'].flatten())
            else:
                features.extend([0] * (33 * 4))

            # Right hand (21 keypoints * 3 = 63)
            if frame['right_hand'] is not None:
                features.extend(frame['right_hand'].flatten())
            else:
                features.extend([0] * (21 * 3))

            # Left hand (21 keypoints * 3 = 63)
            if frame['left_hand'] is not None:
                features.extend(frame['left_hand'].flatten())
            else:
                features.extend([0] * (21 * 3))

            sequence.append(features)

        return np.array(sequence) if flatten else sequence
