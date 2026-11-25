import unittest
from core.risk_engine import weighted_risk, risk_label
class RiskTests(unittest.TestCase):
    def test_weighted(self): self.assertAlmostEqual(weighted_risk(100,0,0,0),40)
    def test_label(self): self.assertEqual(risk_label(80),"CRITICAL")
if __name__=="__main__": unittest.main()
