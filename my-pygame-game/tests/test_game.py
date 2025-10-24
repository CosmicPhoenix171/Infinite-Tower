import unittest
from src.game import Game

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_initialization(self):
        self.assertIsNotNone(self.game)

    def test_game_state(self):
        self.game.start()
        self.assertEqual(self.game.state, 'running')

    def test_game_update(self):
        initial_state = self.game.state
        self.game.update()
        self.assertNotEqual(initial_state, self.game.state)

    def test_game_render(self):
        result = self.game.render()
        self.assertIsNone(result)  # Assuming render returns None

if __name__ == '__main__':
    unittest.main()