def answer(question, context=None):
    q=question.lower()
    if any(k in q for k in ("water depth","hc-sr04","ultrasonic")):
        return "The HC-SR04 measures distance from the sensor to the water surface. Water depth = calibrated empty-tank reference height − measured distance. Reject out-of-range readings; do not treat missing values as zero."
    if "risk" in q:
        return "The experimental risk index is a weighted score from 0–100. In this project it combines normalised depth, rate of rise, soil moisture and drainage stress. It is not a real-world flood probability."
    if "dijkstra" in q or "route" in q:
        return "Dijkstra's algorithm finds the lowest total edge-cost path in a graph when edge costs are non-negative. Here the graph is a teaching grid, not a surveyed road network."
    if "rainfall" in q or "chennai" in q or "puducherry" in q or "tiruchirappalli" in q or "trichy" in q:
        return "The city panel contains cited historical annual rainfall reference values. These are not current rainfall. Chennai, Puducherry and Trichy values use different reporting periods and geographic definitions, so compare them cautiously."
    if "pump" in q:
        return "The Arduino controls the pump through a MOSFET driver and a separate suitable low-voltage supply. The laptop AI cannot directly activate it. Use a timeout, hysteresis and manual stop, and test hardware with supervision."
    if "mae" in q or "error" in q:
        return "Mean Absolute Error (MAE) = average of |predicted − observed|. It describes average error on the trials measured; a small classroom dataset does not prove real-world forecast accuracy."
    return "I am the offline DISASTERMATRIX project assistant. I can explain the sensor pipeline, flood equations, risk index, Dijkstra routing, city reference data and hardware safety. Ask a more specific question or configure an online AI provider for broader answers."
