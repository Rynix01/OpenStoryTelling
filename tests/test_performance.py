import unittest
from copy import deepcopy
from pathlib import Path

import numpy as np
from PIL import Image

from openstory.stage import draw_actors
from openstory.story import read_story, validate


class PerformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1] / "examples" / "kiyi-radyo"
        cls.story = read_story(cls.root / "bolum.json")
        cls.board = cls.story["boards"]["kayit"]
        cls.background = Image.new("RGB", (180, 320))

    def frame(self, line, level, t=.65, progress=.45):
        return np.asarray(draw_actors(self.story, self.board, self.background, None,
                                      line, t, progress, level))

    def test_only_the_speakers_side_moves_its_mouth(self):
        line = {"speaker":"KucukSelim","emotion":"merak"}
        difference = self.frame(line, 0) != self.frame(line, .9)
        self.assertTrue(difference[:, :90].any())
        self.assertFalse(difference[:, 90:].any())

    def test_inner_voice_leaves_both_mouths_still(self):
        for mode in ("thought", "recording"):
            line = {"speaker":"Nermin","emotion":"uzgun","mode":mode}
            np.testing.assert_array_equal(self.frame(line, 0), self.frame(line, .9))

    def test_body_moves_in_a_locked_shot_without_audio(self):
        line = {"speaker":"Nermin", "emotion":"merak", "gesture":"reach"}
        self.assertGreater(np.count_nonzero(self.frame(line,0,.1,.04) != self.frame(line,0,.9,.65)), 200)

    def test_child_and_adult_roles_reject_mismatched_voices(self):
        for character, voice in [("KucukSelim", "serdar"), ("Ece", "can"), ("Selim","ayse")]:
            story = deepcopy(self.story)
            story["voices"][character] = voice
            with self.assertRaises(ValueError):
                validate(story, self.root)

    def test_no_unassigned_cues_or_missing_hand_props(self):
        story = deepcopy(self.story)
        story["shots"][0]["lines"][0]["speaker"] = "unknown"
        with self.assertRaises(ValueError):
            validate(story,self.root)
        story = deepcopy(self.story)
        story["boards"]["kayit"]["actors"][0]["propArt"] = "missing"
        with self.assertRaises(ValueError):
            validate(story,self.root)
