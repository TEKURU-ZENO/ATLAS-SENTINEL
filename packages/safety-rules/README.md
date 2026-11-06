# Safety Rules

`permit_rules.py` contains the currently implemented demo interlocks: hot-work gas hold, missing sensor hold, confined-space gas-test hold, and permit-expiry suspension. The 2.5% LEL hot-work threshold is a configurable prototype assumption inherited from the demo, not a value claimed to come from OISD-STD-105 or the OSH Code. Review and approve all thresholds against the installation's procedures, detector units, and competent safety authority before operational use.

Unimplemented and source-dependent rules are intentionally not shipped as if they were authoritative.
