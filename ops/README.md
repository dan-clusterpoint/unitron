# Ops

Operational scripts and infrastructure configuration.

## Monitoring

Grafana loads alert rules from `ops/grafana`. The file
`gateway_5xx_alert.yaml` defines an alert that triggers when more than 5% of
`unitron-gateway` responses are HTTP 5xx over a 10‑minute window. The rule
notifies the team's Slack channel `#unitron-alerts`.
