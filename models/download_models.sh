#!/bin/bash
# Model Download Script for ComfyUI Workflows
# This script downloads required models to the ComfyUI models directory

set -e  # Exit on error

COMFYUI_DIR="/home/ubuntu/ComfyUI"
CHECKPOINTS_DIR="$COMFYUI_DIR/models/checkpoints"
CONTROLNET_DIR="$COMFYUI_DIR/models/controlnet"
IPADAPTER_DIR="$COMFYUI_DIR/models/ipadapter"
CLIPVISION_DIR="$COMFYUI_DIR/models/clip_vision"

# Create directories if they don't exist
mkdir -p "$CHECKPOINTS_DIR"
mkdir -p "$CONTROLNET_DIR"
mkdir -p "$IPADAPTER_DIR"
mkdir -p "$CLIPVISION_DIR"

echo "Downloading models to ComfyUI installation..."

# Download SDXL Base 1.0
if [ ! -f "$CHECKPOINTS_DIR/sd_xl_base_1.0.safetensors" ]; then
    echo "Downloading SDXL Base 1.0 (6.5GB)..."
    wget -O "$CHECKPOINTS_DIR/sd_xl_base_1.0.safetensors" \
        "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
else
    echo "✓ SDXL Base 1.0 already exists"
fi

# Download ControlNet Union SDXL
if [ ! -f "$CONTROLNET_DIR/controlnet-union-sdxl-1.0.safetensors" ]; then
    echo "Downloading ControlNet Union SDXL (2.5GB)..."
    wget -O "$CONTROLNET_DIR/controlnet-union-sdxl-1.0.safetensors" \
        "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
else
    echo "✓ ControlNet Union SDXL already exists"
fi

# Download IP-Adapter SDXL
if [ ! -f "$IPADAPTER_DIR/ip-adapter_sdxl.safetensors" ]; then
    echo "Downloading IP-Adapter SDXL (670MB)..."
    wget -O "$IPADAPTER_DIR/ip-adapter_sdxl.safetensors" \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.safetensors"
else
    echo "✓ IP-Adapter SDXL already exists"
fi

# Download CLIP Vision Model (bigG for VIT-G preset)
if [ ! -f "$CLIPVISION_DIR/CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors" ]; then
    echo "Downloading CLIP Vision bigG (3.5GB)..."
    wget -O "$CLIPVISION_DIR/CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors" \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors"
else
    echo "✓ CLIP Vision bigG already exists"
fi

# Download IP-Adapter PLUS SDXL (for high strength style transfer)
if [ ! -f "$IPADAPTER_DIR/ip-adapter-plus_sdxl_vit-h.safetensors" ]; then
    echo "Downloading IP-Adapter PLUS SDXL (820MB)..."
    wget -O "$IPADAPTER_DIR/ip-adapter-plus_sdxl_vit-h.safetensors" \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors"
else
    echo "✓ IP-Adapter PLUS SDXL already exists"
fi

# Download CLIP Vision Model H-14 (for PLUS preset)
if [ ! -f "$CLIPVISION_DIR/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" ]; then
    echo "Downloading CLIP Vision H-14 (2.5GB)..."
    wget -O "$CLIPVISION_DIR/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" \
        "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors"
else
    echo "✓ CLIP Vision H-14 already exists"
fi

echo ""
echo "All models downloaded successfully!"
echo ""
echo "Model locations:"
echo "  Checkpoints:  $CHECKPOINTS_DIR"
echo "  ControlNet:   $CONTROLNET_DIR"
echo "  IP-Adapter:   $IPADAPTER_DIR"
echo "  CLIP Vision:  $CLIPVISION_DIR"
