import unittest
from infinite_tower.floors.generator import FloorGenerator

class TestFloorGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = FloorGenerator()

    def test_generate_floor(self):
        floor = self.generator.generate_floor(seed="test_seed")
        self.assertIsNotNone(floor)
        self.assertIn("rooms", floor)
        self.assertIn("layout", floor)

    def test_floor_layout(self):
        floor = self.generator.generate_floor(seed="test_seed")
        layout = floor["layout"]
        self.assertTrue(isinstance(layout, list))
        self.assertGreater(len(layout), 0)

    def test_room_generation(self):
        floor = self.generator.generate_floor(seed="test_seed")
        rooms = floor["rooms"]
        self.assertTrue(all(isinstance(room, dict) for room in rooms))
        self.assertGreater(len(rooms), 0)

if __name__ == '__main__':
    unittest.main()