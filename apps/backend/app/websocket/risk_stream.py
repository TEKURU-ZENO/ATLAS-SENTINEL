async def risk_events():
    for score in [18, 43, 63, 86]:
        yield {"risk": score}
