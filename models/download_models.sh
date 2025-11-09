#!/bin/bash
# Model Download Script for ComfyUI Workflows
# This script downloads required models to the ComfyUI models directory

set -e  # Exit on error

COMFYUI_DIR="/home/ubuntu/ComfyUI"
CHECKPOINTS_DIR="$COMFYUI_DIR/models/checkpoints"
CONTROLNET_DIR="$COMFYUI_DIR/models/controlnet"
IPADAPTER_DIR="$COMFYUI_DIR/models/ipadapter"

# Create directories if they don't exist
mkdir -p "$CHECKPOINTS_DIR"
mkdir -p "$CONTROLNET_DIR"
mkdir -p "$IPADAPTER_DIR"

echo "Downloading models to ComfyUI installation..."

# Download SDXL Base 1.0
if [ ! -f "$CHECKPOINTS_DIR/sd_xl_base_1.0.safetensors" ]; then
    echo "Downloading SDXL Base 1.0 (6.5GB)..."
    wget -O "$CHECKPOINTS_DIR/sd_xl_base_1.0.safetensors" \
        "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
else
    echo "✓ SDXL Base 1.0 already exists"
fi

# Download ControlNet MLSD
if [ ! -f "$CONTROLNET_DIR/control_v11p_sd15_mlsd.pth" ]; then
    echo "Downloading ControlNet MLSD (1.4GB)..."
    wget -O "$CONTROLNET_DIR/control_v11p_sd15_mlsd.pth" \
        "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_mlsd.pth"
else
    echo "✓ ControlNet MLSD already exists"
fi

# Download IP-Adapter SDXL
if [ ! -f "$IPADAPTER_DIR/ip-adapter_sdxl.safetensors" ]; then
    echo "Downloading IP-Adapter SDXL (670MB)..."
    wget -O "$IPADAPTER_DIR/ip-adapter_sdxl.safetensors" \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.safetensors"
else
    echo "✓ IP-Adapter SDXL already exists"
fi

echo ""
echo "All models downloaded successfully!"
echo ""
echo "Model locations:"
echo "  Checkpoints: $CHECKPOINTS_DIR"
echo "  ControlNet:  $CONTROLNET_DIR"
echo "  IP-Adapter:  $IPADAPTER_DIR"
