try:
    import fastapi, httpx, bs4, lxml
    print("smoke ok")
except Exception as e:
    raise SystemExit(f"smoke failed: {e}")
