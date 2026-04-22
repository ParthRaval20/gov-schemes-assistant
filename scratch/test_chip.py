from rag.agent import ask_agent

print("=== Testing 'Schemes for farmers' ===")
for r in ask_agent("Schemes for farmers", session_id="test_chip_1"):
    t = r.get("type", "?")
    if "schemes" in r:
        schemes = r["schemes"]
        names = []
        for s in schemes[:5]:
            if hasattr(s, "scheme_name"):
                names.append(s.scheme_name)
            elif isinstance(s, dict):
                names.append(s.get("scheme_name", "?"))
        print(f"  type={t}, count={len(schemes)}, names={names}")
    elif "reply" in r:
        print(f"  type={t}, reply={str(r['reply'])[:120]}...")
    elif "text" in r:
        pass  # streaming chunks, skip
    else:
        print(f"  type={t}")

print("\n=== Testing 'Women welfare schemes' ===")
for r in ask_agent("Women welfare schemes", session_id="test_chip_2"):
    t = r.get("type", "?")
    if "schemes" in r:
        schemes = r["schemes"]
        names = []
        for s in schemes[:5]:
            if hasattr(s, "scheme_name"):
                names.append(s.scheme_name)
            elif isinstance(s, dict):
                names.append(s.get("scheme_name", "?"))
        print(f"  type={t}, count={len(schemes)}, names={names}")
    elif "reply" in r:
        print(f"  type={t}, reply={str(r['reply'])[:120]}...")
    elif "text" in r:
        pass
    else:
        print(f"  type={t}")
