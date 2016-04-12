# ap-config-scanner
A tool to automatically scan AP serial numbers and firmware into a database for a web frontend.

Uses SNMPv2 to scan all online Access Points for serial number and firmware. This remains the only tool to collect this information.
Gets list of APs from a source of truth database, then attempts to hit each one over (read-only) SNMPv2.
Resulting data is stored in a local SQLite3 DB which feeds a web front end.
