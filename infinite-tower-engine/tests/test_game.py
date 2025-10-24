import unittest
from infinite_tower.game import Game

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_game_initialization(self):
        self.assertIsNotNone(self.game)
        self.assertFalse(self.game.is_running)

    def test_start_game(self):
        self.game.start()
        self.assertTrue(self.game.is_running)

    def test_pause_game(self):
        self.game.start()
        self.game.pause()
        self.assertFalse(self.game.is_running)

    def test_end_game(self):
        self.game.start()
        self.game.end()
        self.assertFalse(self.game.is_running)

if __name__ == '__main__':
    unittest.main()