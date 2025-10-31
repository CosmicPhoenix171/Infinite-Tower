import unittest
from infinite_tower.floors.generator import FloorGenerator, Room

class TestFloorGenerator(unittest.TestCase):

    def setUp(self):
        # FloorGenerator constructor takes a seed parameter
        self.generator = FloorGenerator(seed="test_seed")

    def test_generate_floor(self):
        # generate_floor takes num_rooms parameter and returns list of rooms
        rooms = self.generator.generate_floor(num_rooms=5)
        self.assertIsNotNone(rooms)
        self.assertTrue(isinstance(rooms, list))
        self.assertEqual(len(rooms), 5)

    def test_room_structure(self):
        # Test that each room has the expected Room object structure
        rooms = self.generator.generate_floor(num_rooms=3)
        for room in rooms:
            self.assertTrue(isinstance(room, Room))
            self.assertTrue(hasattr(room, "width"))
            self.assertTrue(hasattr(room, "height"))
            self.assertTrue(hasattr(room, "enemies"))
            self.assertTrue(hasattr(room, "loot"))
            self.assertTrue(hasattr(room, "tiles"))
            self.assertTrue(hasattr(room, "room_type"))

    def test_room_generation(self):
        # Test that rooms are Room objects
        rooms = self.generator.generate_floor(num_rooms=3)
        self.assertTrue(all(isinstance(room, Room) for room in rooms))
        self.assertGreater(len(rooms), 0)
        
    def test_seed_consistency(self):
        # Test that same seed produces similar results
        # Note: Room objects won't be equal, but their attributes should match
        gen1 = FloorGenerator(seed="consistent_seed")
        gen2 = FloorGenerator(seed="consistent_seed")
        rooms1 = gen1.generate_floor(num_rooms=3)
        rooms2 = gen2.generate_floor(num_rooms=3)
        
        self.assertEqual(len(rooms1), len(rooms2))
        
        # Compare room attributes
        for r1, r2 in zip(rooms1, rooms2):
            self.assertEqual(r1.width, r2.width)
            self.assertEqual(r1.height, r2.height)
            self.assertEqual(r1.room_type, r2.room_type)
            self.assertEqual(len(r1.enemies), len(r2.enemies))
            self.assertEqual(len(r1.loot), len(r2.loot))
    
    def test_room_doors(self):
        # Test that adjacent rooms are connected with doors
        rooms = self.generator.generate_floor(num_rooms=4)
        # At least some rooms should have doors
        total_doors = sum(len(room.doors) for room in rooms)
        self.assertGreater(total_doors, 0)
    
    def test_room_population(self):
        # Test that rooms are populated with enemies and loot
        rooms = self.generator.generate_floor(num_rooms=5, floor_level=1)
        
        # Check that at least some rooms have enemies or loot
        total_enemies = sum(len(room.enemies) for room in rooms)
        total_loot = sum(len(room.loot) for room in rooms)
        
        # Not all rooms will have enemies/loot (safe rooms exist)
        # but the total should be > 0
        self.assertGreater(total_enemies + total_loot, 0)

if __name__ == '__main__':
    unittest.main()