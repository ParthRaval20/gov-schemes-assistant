import os, sys
sys.path.insert(0, "d:\\office\\gov-schemes-assistant")
from rag.agent import ask_agent

print("=== Testing 'Schemes for farmers' ===")
for r in ask_agent("Schemes for farmers", session_id="test_chip_3"):
    t = r.get("type", "?")
    print(f"  EVENT: {r}")
