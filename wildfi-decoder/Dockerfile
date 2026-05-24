# syntax=docker/dockerfile:1.7

FROM eclipse-temurin:21-jre-jammy AS source

ARG WILDFI_DECODER_GIT_REF=b4002eb9a6111de140b95e5a35c3f3bd552d51be

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git init WildFiDecoder \
    && cd WildFiDecoder \
    && git remote add origin https://github.com/wildlab/WildFiDecoder.git \
    && git fetch --depth=1 origin "${WILDFI_DECODER_GIT_REF}" \
    && git checkout --detach FETCH_HEAD

FROM eclipse-temurin:21-jre-jammy

ENV WILDFI_DECODER_HOME=/opt/wildfi-decoder \
    WILDFI_DECODER_WORKDIR=/work \
    WILDFI_DECODER_MODE=2 \
    WILDFI_DECODER_BURST_FORM=0 \
    WILDFI_DECODER_FILE_INDEX=0 \
    WILDFI_DECODER_TAG_SELECTION=0 \
    WILDFI_IMU_FREQUENCY=25

RUN groupadd --system wildfi \
    && useradd --system --gid wildfi --home-dir /nonexistent --shell /usr/sbin/nologin wildfi \
    && mkdir -p "${WILDFI_DECODER_HOME}" "${WILDFI_DECODER_WORKDIR}" \
    && chown -R wildfi:wildfi "${WILDFI_DECODER_HOME}" "${WILDFI_DECODER_WORKDIR}"

WORKDIR ${WILDFI_DECODER_HOME}

COPY --from=source --chown=wildfi:wildfi \
    /src/WildFiDecoder/WildFiDecoderMultiThreaded/WildFiDecoderStandalone.jar \
    /src/WildFiDecoder/WildFiDecoderMultiThreaded/WildFiDecoderConfig.txt \
    /opt/wildfi-decoder/
COPY --chown=wildfi:wildfi --chmod=0555 wildfi-decoder/run-wildfi-decoder.sh /usr/local/bin/run-wildfi-decoder

USER wildfi
WORKDIR /work

ENTRYPOINT ["run-wildfi-decoder"]
