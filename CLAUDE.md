# ComfyUI EC2 Setup for Claude Code

This repository contains documentation for setting up and using an AWS EC2 GPU instance with ComfyUI for iterative development with Claude Code.

## Overview

We set up an AWS EC2 G5 instance (NVIDIA A10G GPU with 24GB VRAM) running ComfyUI, enabling Claude Code to edit workflows, custom nodes, and Python code while seeing real-time feedback from the ComfyUI console.

## Documentation

- **[ec2_setup.md](./ec2_setup.md)** - Complete setup instructions for creating the EC2 instance and installing ComfyUI
- **[usage.md](./usage.md)** - Daily usage guide including connecting, running ComfyUI, and managing the instance

## Quick Start

If the instance is already set up, you can connect immediately:

```bash
# Option 1: Direct SSH (for quick terminal access)
ssh comfyui-ec2

# Option 2: VS Code Remote SSH (recommended for GUI workflow)
# 1. Open VS Code
# 2. Press F1 → "Remote-SSH: Connect to Host" → Select "comfyui-ec2"
# 3. Open folder: /home/ubuntu/ComfyUI
# 4. Claude Code now works on the remote instance

# Option 3: Claude Code CLI (directly on EC2)
ssh comfyui-ec2
cd ~/ComfyUI
claude  # Claude Code CLI is installed on the instance

# Start ComfyUI on the remote instance
~/start-comfyui.sh
```

## Instance Information

- **Instance ID**: `i-05e0226ee5b99ace1`
- **Instance Type**: g5.xlarge (NVIDIA A10G, 24GB VRAM)
- **Region**: us-east-1
- **Cost**: ~$1.00/hour when running
- **ComfyUI Location**: `/home/ubuntu/ComfyUI`

## Key Features

✅ **Full GPU Access** - NVIDIA A10G with 24GB VRAM
✅ **Pre-configured Environment** - CUDA, PyTorch, and ComfyUI ready to go
✅ **VS Code Remote SSH** - Direct integration with Claude Code
✅ **Easy Management** - Simple commands to start/stop to save costs
✅ **Deep Learning AMI** - Ubuntu 22.04 with NVIDIA drivers pre-installed

## Architecture

```
Local Machine (Claude Code)
    ↓ (SSH/VS Code Remote)
EC2 Instance (g5.xlarge)
    ├── Ubuntu 22.04 LTS
    ├── NVIDIA Driver 580.95.05
    ├── CUDA 12.9
    ├── Python 3.10 + venv
    └── ComfyUI
        ├── PyTorch 2.5.1+cu121
        ├── Custom nodes
        ├── Models
        └── Workflows
```

## Workflow

1. Connect to instance via VS Code Remote SSH
2. Claude Code can now see/edit all files on the remote instance
3. Run ComfyUI and see console output in real-time
4. Claude iterates on code, sees errors, and fixes them
5. Test changes immediately in the running ComfyUI instance

## Cost Management

**Important**: The instance costs ~$1/hour when running. Always stop it when not in use:

```bash
# Stop instance
aws ec2 stop-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1

# Start instance
aws ec2 start-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1
```

## Next Steps

1. Read [ec2_setup.md](./ec2_setup.md) if you need to create a new instance or troubleshoot
2. Read [usage.md](./usage.md) for daily operations and development workflows
3. Connect via VS Code Remote SSH and start developing with Claude Code!

## SSH Key Location

Your private key is stored at: `~/.ssh/comfyui-claude-code.pem`

## Support

For setup issues, see the Troubleshooting sections in:
- [ec2_setup.md - Troubleshooting](./ec2_setup.md#troubleshooting)
- [usage.md - Troubleshooting](./usage.md#troubleshooting)
