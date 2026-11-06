from app.services.twin_service import get_twin_state
from app.services.risk_model import compound_risk


def get_current_risk() -> dict:
    twin = get_twin_state()
    model = compound_risk(twin)
    risk = model["score"]
    previous = twin["sensor_history"][-2]["value"] if len(twin["sensor_history"]) > 1 else twin["methane_percent_lel"]
    rising = twin["methane_percent_lel"] > previous
    forecast30 = min(99, risk + (10 if rising else 3))
    forecast60 = min(99, forecast30 + (10 if rising else 4))
    leading_interactions = ", ".join(item["label"].lower() for item in model["interactions"][:2]) or "the available sensor and permit signals"
    return {
        "current": min(risk, 99),
        "forecast30": forecast30,
        "forecast60": forecast60,
        "reason": f"Risk is elevated by {leading_interactions}" + ("; sensor readings are rising." if rising else "."),
        "level": model["level"],
        "drivers": model["drivers"],
        "interactions": model["interactions"],
        "method": model["method"],
        "sensor_timestamp": twin["sensor_timestamp"],
        "data_source": twin["data_source"],
        "data_notice": twin["data_notice"],
    }
