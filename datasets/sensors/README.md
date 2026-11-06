# Sensor Sample Provenance

`sensor_history.csv` is a four-reading repository example used to exercise the demo twin and API. The repository contains no instrument export, calibration record, chain of custody, facility attribution, or source citation for these values. Treat the readings as illustrative/unknown-provenance demo data, not verified real-world telemetry.

Do not train or evaluate a safety model on this file. The separately generated `datasets/simulated/sensor_stream.csv` is explicitly synthetic and has its own documented labels. Production integrations must preserve sensor identity, engineering units, calibration/quality flags, timestamps with timezone, source-system identifiers, and missing/stale-data state.
