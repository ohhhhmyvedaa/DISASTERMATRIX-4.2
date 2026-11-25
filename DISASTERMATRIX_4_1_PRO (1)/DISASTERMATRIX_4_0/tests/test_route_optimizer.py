import unittest
from core.route_optimizer import shortest_route
class RouteTests(unittest.TestCase):
    def test_route(self):
        result=shortest_route("A","P")
        self.assertTrue(result["path"])
        self.assertEqual(result["path"][0],"A")
        self.assertEqual(result["path"][-1],"P")
if __name__=="__main__": unittest.main()
