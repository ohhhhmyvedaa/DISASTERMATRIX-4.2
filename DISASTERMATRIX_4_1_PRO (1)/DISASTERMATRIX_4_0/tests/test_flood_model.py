import unittest
from core.flood_model import water_depth, tank_volume_litres, rainfall_volume_litres, water_balance, rate_of_rise

class FloodModelTests(unittest.TestCase):
    def test_depth(self): self.assertAlmostEqual(water_depth(30,24),6)
    def test_volume(self): self.assertAlmostEqual(tank_volume_litres(40,30,10),12)
    def test_rain(self): self.assertAlmostEqual(rainfall_volume_litres(10,2),20)
    def test_balance(self): self.assertAlmostEqual(water_balance(20,5,3),12)
    def test_rise(self): self.assertAlmostEqual(rate_of_rise(8,4,120),2)
if __name__=="__main__": unittest.main()
