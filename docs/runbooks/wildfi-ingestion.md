# WildFi Ingestion

DEALIoT accepts WildFi gateway/tag data through the MQTT bridge. The upstream WildFi project is
`https://github.com/trichl/WildFiOpenSource`.

## Supported Ingestion Contract

Publish decoded WildFi JSON to MQTT topics under:

```text
wildfi/tags/{tag_id}/gps
wildfi/tags/{tag_id}/imu
wildfi/tags/{tag_id}/environment
wildfi/tags/{tag_id}/proximity
wildfi/gateways/{gateway_id}/tags/{tag_id}/metadata
```

The bridge subscribes to `$share/ingestors/wildfi/#` in addition to the generic device topic. GPS,
GNSS, and raw GPS topics are routed to Kafka topic `raw.gps`. IMU, environment, proximity,
metadata, movement, and decoded WildFi topics are routed to `raw.sensor`.

## GPS Payload

Use one of these timestamp fields:

- `timestamp`: ISO-8601 string,
- `utcTimestamp`: Unix timestamp in seconds or milliseconds,
- `utc_timestamp`: Unix timestamp in seconds or milliseconds.

Use `lat`/`lon` or `latitude`/`longitude` for coordinates. Example:

```json
{
  "utcTimestamp": 1704067200,
  "lat": 47.695,
  "lon": 9.132,
  "hdop": 1.4,
  "temperatureInDegCel": 18.7
}
```

## Native WildFi Binary Files

WildFi movement/proximity log files are native binary payloads. Production should not publish those
files directly as telemetry. Store the binary artifact in object storage and publish metadata, or run
the WildFi decoder first and publish decoded JSON. The production Kubernetes overlay includes
`wildfi-decoder-config.yaml` with the decoder conversion factors and the expected MQTT mapping.

## Configuration

Set these variables for the bridge:

```text
MQTT_TOPICS=$share/ingestors/devices/#,$share/ingestors/wildfi/#
WILDFI_TOPIC_PREFIXES=wildfi,wild-fi
```

For Kubernetes production, update
`deploy/kubernetes/overlays/production/runtime-config.production.example.env` through a
site-specific overlay or GitOps tooling.
