# syntax=docker/dockerfile:1.7

FROM rust:1.85-bookworm AS builder

WORKDIR /src

RUN apt-get update \
 && apt-get install -y --no-install-recommends cmake pkg-config libssl-dev ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY --chmod=0444 Cargo.toml /src/Cargo.toml
COPY --chmod=0444 mqtt-kafka-bridge/Cargo.toml /src/mqtt-kafka-bridge/Cargo.toml
COPY --chmod=0444 mqtt-kafka-bridge/src /src/mqtt-kafka-bridge/src

RUN cargo build --release --locked || cargo build --release

FROM debian:bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --system --create-home --shell /usr/sbin/nologin appuser

COPY --from=builder --chown=root:root --chmod=0555 \
  /src/target/release/dealiot-mqtt-kafka-bridge \
  /usr/local/bin/dealiot-mqtt-kafka-bridge

USER appuser
ENV RUST_LOG="info"
CMD ["dealiot-mqtt-kafka-bridge"]
