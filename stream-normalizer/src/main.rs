use dealiot_stream_normalizer::{
    normalize_record, normalized_event_json, LatestState, NormalizerConfig,
};
use log::{error, info};
use rdkafka::config::ClientConfig;
use rdkafka::consumer::{Consumer, StreamConsumer};
use rdkafka::message::Message;
use rdkafka::producer::{FutureProducer, FutureRecord};
use rdkafka::util::Timeout;
use rdkafka::Offset;
use std::time::Duration;
use thiserror::Error;

#[derive(Debug, Error)]
enum NormalizerError {
    #[error("{0}")]
    Config(String),
    #[error(transparent)]
    Kafka(#[from] rdkafka::error::KafkaError),
    #[error(transparent)]
    Json(#[from] serde_json::Error),
}

#[tokio::main]
async fn main() -> Result<(), NormalizerError> {
    env_logger::init();
    let config = NormalizerConfig::from_env();
    run(config).await
}

async fn run(config: NormalizerConfig) -> Result<(), NormalizerError> {
    let consumer = kafka_consumer(&config)?;
    let producer = kafka_producer(&config)?;
    let topics: Vec<_> = config.source_topics.iter().map(String::as_str).collect();
    consumer.subscribe(&topics)?;
    info!(
        "Subscribed to source topics: {}",
        config.source_topics.join(",")
    );

    let mut latest = LatestState::default();

    loop {
        tokio::select! {
            message = consumer.recv() => {
                let message = message?;
                let source_topic = message.topic().to_string();
                let payload = match message.payload_view::<str>() {
                    Some(Ok(payload)) => payload,
                    Some(Err(error)) => {
                        error!("Skipping non-UTF8 Kafka payload from {source_topic}: {error}");
                        continue;
                    }
                    None => continue,
                };

                let Some(event) = normalize_record(&source_topic, payload) else {
                    continue;
                };
                let event_json = normalized_event_json(&event)?;
                producer
                    .send(
                        FutureRecord::to(&config.features_topic)
                            .key(&event.entity_id)
                            .payload(&event_json),
                        Timeout::After(Duration::from_secs(30)),
                    )
                    .await
                    .map_err(|(error, _)| NormalizerError::Config(format!("features send failed: {error}")))?;

                if latest.accepts(&event) {
                    producer
                        .send(
                            FutureRecord::to(&config.state_topic)
                                .key(&event.entity_id)
                                .payload(&event_json),
                            Timeout::After(Duration::from_secs(30)),
                        )
                        .await
                        .map_err(|(error, _)| NormalizerError::Config(format!("state send failed: {error}")))?;
                }

                consumer.store_offset(message.topic(), message.partition(), Offset::Offset(message.offset() + 1))?;
            }
            signal = tokio::signal::ctrl_c() => {
                signal.map_err(|error| NormalizerError::Config(format!("signal handler failed: {error}")))?;
                info!("Shutdown signal received");
                break;
            }
        }
    }

    Ok(())
}

fn kafka_consumer(config: &NormalizerConfig) -> Result<StreamConsumer, NormalizerError> {
    let mut client_config = kafka_client_config(config);
    client_config
        .set("group.id", config.consumer_group.as_str())
        .set("enable.auto.commit", "false")
        .set("enable.auto.offset.store", "false")
        .set(
            "auto.offset.reset",
            std::env::var("KAFKA_AUTO_OFFSET_RESET").unwrap_or_else(|_| "earliest".to_string()),
        );
    client_config.create().map_err(Into::into)
}

fn kafka_producer(config: &NormalizerConfig) -> Result<FutureProducer, NormalizerError> {
    kafka_client_config(config)
        .set("acks", "all")
        .set("retries", "10")
        .set("linger.ms", "50")
        .create()
        .map_err(Into::into)
}

fn kafka_client_config(config: &NormalizerConfig) -> ClientConfig {
    let mut client_config = ClientConfig::new();
    client_config.set("bootstrap.servers", config.bootstrap_servers.as_str());
    apply_security_config(&mut client_config);
    client_config
}

fn apply_security_config(client_config: &mut ClientConfig) {
    let security_protocol =
        std::env::var("KAFKA_SECURITY_PROTOCOL").unwrap_or_else(|_| "PLAINTEXT".to_string());
    client_config.set("security.protocol", security_protocol.trim());

    if security_protocol.starts_with("SASL_") {
        if let Ok(mechanism) = std::env::var("KAFKA_SASL_MECHANISM") {
            client_config.set("sasl.mechanisms", mechanism);
        }
        if let Ok(username) = std::env::var("KAFKA_SASL_USERNAME") {
            client_config.set("sasl.username", username);
        }
        if let Ok(password) = std::env::var("KAFKA_SASL_PASSWORD") {
            client_config.set("sasl.password", password);
        }
    }

    if security_protocol.contains("SSL")
        && std::env::var("KAFKA_SSL_CHECK_HOSTNAME").is_ok_and(|value| {
            matches!(
                value.trim().to_ascii_lowercase().as_str(),
                "0" | "false" | "no" | "off"
            )
        })
    {
        client_config.set("enable.ssl.certificate.verification", "false");
    }
}
