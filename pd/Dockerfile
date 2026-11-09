# === Stage 1: build forked pd-else ===
FROM debian:forky-slim AS build-externals

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git ca-certificates pkg-config bzip2 \
        puredata-dev libssl-dev libogg-dev zlib1g-dev libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

# Pin ELSE_REF to a commit/tag for reproducible builds
ARG ELSE_REPO=https://github.com/al165/pd-else.git
ARG ELSE_REF=master
RUN git clone --depth 1 --branch ${ELSE_REF} --recurse-submodules --shallow-submodules \
        ${ELSE_REPO} /src/pd-else

WORKDIR /src/pd-else

RUN cmake -S . -B build \
        -DCMAKE_BUILD_TYPE=Release \
        -DPD_FLOATSIZE=32 \
        -DCMAKE_C_STANDARD_LIBRARIES=-lzstd \
        -DCMAKE_CXX_STANDARD_LIBRARIES=-lzstd \
    && cmake --build build -j"$(nproc)" \
    && rm -f build/else/*.a

# build and install rose
ARG ROSE_REF=main
RUN git clone --depth 1 --branch ${ROSE_REF} --recurse-submodules --shallow-submodules \
    https://github.com/al165/rose.git /src/rose
WORKDIR /src/rose

RUN make PDDIR=pure-data/
RUN make install objectsdir=/root/.local/lib/pd/extra

# === Stage 2: other externals from Deken ===
FROM registry.git.iem.at/pd/deken:latest AS deken
RUN deken install --ignore-gpg mp3cast~

# === Stage 3: run patch ===
FROM debian:forky-slim

WORKDIR /fjte

RUN apt-get update && apt-get install -y --no-install-recommends puredata alsa-utils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build-externals /src/pd-else/build/else /root/.local/lib/pd/extra/else
COPY --from=build-externals /root/.local/lib/pd/extra/rose /root/.local/lib/pd/extra/rose
COPY --from=deken /root/.local/lib/pd/extra/mp3cast~ /root/.local/lib/pd/extra/mp3cast~

COPY . .

EXPOSE 8000

ENV FJTE_BASE_DIR=/fjte

CMD ["pd", "-nogui", "-nomidi", "-stderr", "FromJawToEar.pd"]
