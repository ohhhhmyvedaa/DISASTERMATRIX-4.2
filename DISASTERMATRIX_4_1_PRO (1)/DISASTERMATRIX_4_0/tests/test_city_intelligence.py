import unittest
from core.city_intelligence import load_hazard_sources, load_chennai_locations, city_summary, CITY_COORDINATES

class CityIntelligenceTests(unittest.TestCase):
    def test_three_cities_present(self):
        self.assertEqual(set(CITY_COORDINATES), {"Chennai", "Puducherry", "Tiruchirappalli"})
    def test_hazard_sources_present(self):
        df=load_hazard_sources()
        self.assertTrue({"Chennai", "Puducherry", "Tiruchirappalli"}.issubset(set(df.city)))
    def test_chennai_subset_has_source(self):
        df=load_chennai_locations()
        self.assertGreater(len(df), 10)
        self.assertTrue(df.source_url.str.startswith("https://").all())
    def test_city_summary_has_caveat(self):
        for city in CITY_COORDINATES:
            self.assertTrue(city_summary(city)["caveat"])

if __name__ == "__main__": unittest.main()
