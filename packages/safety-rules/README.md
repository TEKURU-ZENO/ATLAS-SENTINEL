# Safety Rules

`permit_rules.py` contains the currently implemented demo interlocks: hot-work gas hold, missing/stale/unverified sensor hold, confined-space gas-test hold, and permit-expiry suspension. The API treats readings older than `ATLAS_SENSOR_MAX_AGE_MINUTES` (15 minutes by default) as unavailable, and this repository's sample remains unverified even if its timestamp is recent. The 2.5% LEL hot-work threshold is a prototype assumption inherited from the demo, not a value claimed to come from OISD-STD-105 or the OSH Code. Review and approve all thresholds and freshness requirements against the installation's procedures, detector units, and competent safety authority before operational use.

Unimplemented and source-dependent rules are intentionally not shipped as if they were authoritative.
