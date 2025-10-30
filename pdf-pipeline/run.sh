#!/bin/bash

# PDF-to-Image Conversion Pipeline
# This script builds and runs the robust PDF converter

echo "====================================="
echo "PDF-to-Image Conversion Pipeline"
echo "====================================="
echo ""

# Build the Docker image
echo "Step 1: Building Docker image..."
docker build -t pdf2img-robust .

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed!"
    exit 1
fi

echo ""
echo "Step 2: Running conversion..."
echo "Input: ~/Desktop/PDF/"
echo "Output: ./output/"
echo ""

# Run the container with bind mounts
docker run --rm \
  -v "$HOME/Desktop/PDF:/data/pdfs:ro" \
  -v "$PWD/output:/data/output" \
  pdf2img-robust

if [ $? -eq 0 ]; then
    echo ""
    echo "====================================="
    echo "Conversion completed!"
    echo "Check ./output/ for extracted images"
    echo "====================================="
else
    echo ""
    echo "Error: Conversion failed!"
    exit 1
fi

