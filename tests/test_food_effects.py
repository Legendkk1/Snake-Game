import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.join(os.path.dirname(__file__), "..", "Snake Game")
sys.path.insert(0, ROOT)

import Snake_game


class FoodEffectsTests(unittest.TestCase):
    def test_normal_food_only_grows(self):
        effect, x_change, y_change = Snake_game.resolve_food_effect("normal", 20, 0)
        self.assertEqual(effect, "grow")
        self.assertEqual((x_change, y_change), (20, 0))

    def test_kill_food_ends_the_game(self):
        effect, x_change, y_change = Snake_game.resolve_food_effect("kill", 20, 0)
        self.assertEqual(effect, "lose")
        self.assertEqual((x_change, y_change), (20, 0))


if __name__ == "__main__":
    unittest.main()
