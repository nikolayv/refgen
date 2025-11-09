# ComfyUI Models Directory

This directory contains scripts and documentation for managing ComfyUI models.

## Important Note

**Model files are NOT stored in this git repository.** They are downloaded to the ComfyUI installation directory on the EC2 instance:

```
/home/ubuntu/ComfyUI/models/
├── checkpoints/       # Base diffusion models
├── controlnet/        # ControlNet models
├── ipadapter/         # IP-Adapter models
├── loras/            # LoRA models
└── ...
```

## Files in this Directory

- **download_models.sh** - Automated script to download all required models
- **models_manifest.txt** - Complete documentation of all models and their sources
- **README.md** - This file

## Quick Start

To download all required models for the workflows in this repository:

```bash
cd /home/ubuntu/refgen/models
./download_models.sh
```

The script will:
1. Check if models already exist (won't re-download)
2. Download missing models from HuggingFace
3. Place them in the correct ComfyUI directories
4. Report success/failure for each model

## Adding New Models

When you add a new workflow that requires additional models:

1. Update `models_manifest.txt` with the new model details
2. Update `download_models.sh` to include download commands
3. Document which workflow uses the model
4. Commit the updated scripts to git

## Storage Considerations

Models are large files (500MB - 6GB each):
- They persist on the EC2 instance across restarts
- They are lost if the instance is terminated
- Total storage for current models: ~8.5 GB
- EC2 instance has 100GB storage available

## Model Sources

All models are sourced from HuggingFace:
- Stable Diffusion XL: https://huggingface.co/stabilityai
- ControlNet: https://huggingface.co/lllyasviel
- IP-Adapter: https://huggingface.co/h94

## Troubleshooting

If downloads fail:
1. Check internet connectivity on EC2: `ping huggingface.co`
2. Verify wget is installed: `which wget`
3. Check disk space: `df -h`
4. Try manual download with `wget -c` to resume interrupted downloads
