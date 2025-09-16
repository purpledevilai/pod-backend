#!/bin/bash

set -e  # Exit on error

# -------------------------
# Configurable Variables
# -------------------------

LAYER_NAME="requirements"
LAYER_DIR="layers/$LAYER_NAME"
ZIP_NAME="$LAYER_NAME-layer.zip"

PYTHON_VERSION="3.11"
ARCHITECTURE="x86_64"  # Change to arm64 if needed
REQUIREMENTS="pydantic requests PyJWT"

CONTAINER_IMAGE="public.ecr.aws/sam/build-python${PYTHON_VERSION}:1-${ARCHITECTURE}"
CONTAINER_NAME="layer-build-temp"

# -------------------------
# Build Process
# -------------------------

echo "🐳 Pulling container image: $CONTAINER_IMAGE"
docker pull $CONTAINER_IMAGE

# Clean up old artifacts if any
rm -f $LAYER_DIR/$ZIP_NAME
rm -rf $LAYER_DIR/python

echo "🚀 Running container to install packages and create layer zip..."

docker run --rm -v "$(pwd)/$LAYER_DIR:/var/task" --platform "linux/${ARCHITECTURE}" $CONTAINER_IMAGE /bin/sh -c "
  pip3 install \
    --platform manylinux2014_${ARCHITECTURE} \
    --target=./python \
    --no-cache-dir \
    --implementation cp \
    --python-version ${PYTHON_VERSION} \
    --only-binary=:all: --upgrade \
    ${REQUIREMENTS} && \
  zip -r ${ZIP_NAME} ./python
"

if [ -f "$LAYER_DIR/$ZIP_NAME" ]; then
    echo "✅ Layer zip created successfully at: $LAYER_DIR/$ZIP_NAME"
else
    echo "❌ Failed to generate layer zip"
    exit 1
fi
