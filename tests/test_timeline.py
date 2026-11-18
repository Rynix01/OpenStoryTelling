import unittest
from pathlib import Path

import numpy as np

from openstory.render import mouth_intervals, stamp
from openstory.sound import score
from openstory.story import compose, read_story


class TimelineTests(unittest.TestCase):
    def test_voice_opens_mouth_only_in_active_frames(self):
        samples = np.zeros(300, dtype=np.float32)
        samples[30:60] = 0.3
        self.assertEqual(mouth_intervals(samples, 300, 0, 30), "between(n,3,5)")
        self.assertEqual(mouth_intervals(samples, 300, 6, 8), "0")

    def test_same_theme_repeats_without_speech_or_network(self):
        first = score(40000, 8000, "İskele")
        np.testing.assert_array_equal(first, score(40000, 8000, "İskele"))
        self.assertGreater(np.max(np.abs(first)), 0.01)
        self.assertEqual(first[-1], 0)

    def test_timestamps_carry_across_minute(self):
        self.assertEqual(stamp(59.9998, srt=True), "00:01:00,000")
        self.assertEqual(stamp(3599.998), "1:00:00.00")

    def test_blink_layer_does_not_cover_the_whole_frame(self):
        source = Path(__file__).resolve().parents[1] / "examples/islak-bilet/bolum.json"
        story = read_story(source)
        base = compose(story, "cep", source.parent)
        blink = compose(story, "cep", source.parent, state="blink")
        self.assertEqual(blink.getpixel((0, 0))[3], 0)
        self.assertIsNotNone(blink.getbbox())
        self.assertLess(blink.getbbox()[2] - blink.getbbox()[0], base.width // 2)


if __name__ == "__main__":
    unittest.main()
