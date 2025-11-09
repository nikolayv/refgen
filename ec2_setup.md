# EC2 Setup for ComfyUI with Claude Code

This document describes the detailed setup process for creating an EC2 GPU instance with ComfyUI.

## Overview

We set up an AWS EC2 G5 instance with GPU support to run ComfyUI, enabling Claude Code to edit workflows, custom nodes, and Python code while seeing real-time feedback from the ComfyUI console.

This guide includes cloning the [refgen repository](https://github.com/nikolayv/refgen) which contains:
- Setup documentation (this file)
- Usage instructions
- Helper scripts (`start-comfyui.sh`)
- Workflow files

## Setup Architecture

- **Instance Type**: g5.xlarge (NVIDIA A10G GPU with 24GB VRAM)
- **AMI**: Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)
- **Region**: us-east-1 (N. Virginia)
- **Security**: Uses same security group as existing DB proxy instance
- **Access Method**: SSH with dedicated key pair, configured for VS Code Remote SSH
- **Storage**: 100GB gp3
- **Cost**: ~$1.00/hour when running

## Detailed Setup Steps

### 1. AWS CLI Verification
First, we verified AWS CLI was installed and credentials were configured:
```bash
aws --version
aws sts get-caller-identity
```

### 2. SSH Key Pair Creation
Created a dedicated SSH key pair for ComfyUI access:
```bash
aws ec2 create-key-pair \
  --region us-east-1 \
  --key-name comfyui-claude-code \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/comfyui-claude-code.pem
chmod 400 ~/.ssh/comfyui-claude-code.pem
```

### 3. AMI Selection
Found the latest Deep Learning AMI with NVIDIA drivers and CUDA pre-installed:
```bash
aws ec2 describe-images \
  --region us-east-1 \
  --owners amazon \
  --filters "Name=name,Values=Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)*" \
            "Name=state,Values=available" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].[ImageId, Name]'
```
Result: `ami-0601999f27e2188a7`

### 4. Security Group Configuration
Instead of creating a new security group, we reused the existing security group from the memgenie-db-access instance (`sg-04ea9408571e46ef0`) which allows SSH access from a specific IP.

To find your existing security groups:
```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --filters "Name=tag:Name,Values=*db*,*DB*,*proxy*,*Proxy*" \
            "Name=instance-state-name,Values=running,stopped" \
  --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0]]'
```

### 5. EC2 Instance Launch
Launched the g5.xlarge instance with 100GB storage:
```bash
aws ec2 run-instances \
  --region us-east-1 \
  --image-id ami-0601999f27e2188a7 \
  --instance-type g5.xlarge \
  --key-name comfyui-claude-code \
  --security-group-ids sg-04ea9408571e46ef0 \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ComfyUI-Claude-Code}]'
```

Instance Details:
- Instance ID: `i-05e0226ee5b99ace1`
- Public IP: `34.235.112.212`
- Private IP: `172.31.36.172`

### 6. SSH Configuration
Added SSH config entry for easy access:
```bash
cat >> ~/.ssh/config << 'EOF'

# ComfyUI EC2 Instance for Claude Code
Host comfyui-ec2
    HostName 34.235.112.212
    User ubuntu
    IdentityFile ~/.ssh/comfyui-claude-code.pem
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking no
EOF
```

**Note**: If you stop and restart the instance, the public IP will change and you'll need to update the `HostName` in this config.

### 7. Clone Setup Repository
First, clone this repository which contains documentation and helper scripts:

```bash
# SSH into the instance
ssh comfyui-ec2

# Update system packages
sudo apt-get update
sudo apt-get install -y git python3-pip python3-venv

# Clone the refgen repository (contains documentation and scripts)
cd ~
git clone https://github.com/nikolayv/refgen.git
```

### 8. ComfyUI Installation
Install ComfyUI and its dependencies:

```bash
# Clone ComfyUI repository
cd ~
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA support
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install ComfyUI requirements
pip install -r requirements.txt
```

### 9. Link ComfyUI to refgen Repository
Create symlinks so ComfyUI uses the version-controlled workflows and inputs from the refgen repository:

```bash
# Remove default directories
rm -rf ~/ComfyUI/workflows
rm -rf ~/ComfyUI/input

# Create symlinks to refgen
ln -s ~/refgen/workflows ~/ComfyUI/workflows
ln -s ~/refgen/input ~/ComfyUI/input

# Verify symlinks
ls -la ~/ComfyUI/ | grep -E "workflows|input"
# Should show:
#   workflows -> /home/ubuntu/refgen/workflows
#   input -> /home/ubuntu/refgen/input
```

This setup ensures:
- Workflows are version controlled in the refgen repository
- Input images are tracked alongside workflows
- Changes in refgen are immediately visible in ComfyUI
- You only need to commit/push from the refgen directory

### 10. Helper Script Setup
Create a symlink to the start script from the refgen repository:

```bash
# Create symlink to start script (already in refgen repo)
ln -s ~/refgen/start-comfyui.sh ~/start-comfyui.sh

# Verify the symlink
ls -lh ~/start-comfyui.sh
# Should show: ~/start-comfyui.sh -> /home/ubuntu/refgen/start-comfyui.sh
```

The script contains:
```bash
#!/bin/bash
cd ~/ComfyUI
source venv/bin/activate
python main.py --listen 0.0.0.0 --port 8188
```

### 11. Download Models
Download required models for the workflows:

```bash
# Run the automated download script from refgen
cd ~/refgen/models
./download_models.sh
```

This will download (~13.1GB total):
- SDXL Base 1.0 (6.5GB)
- ControlNet Union SDXL (2.5GB) - supports 12+ control types
- IP-Adapter SDXL (670MB)
- CLIP Vision bigG (3.5GB) - required by IP-Adapter

Models are downloaded to the ComfyUI models directory and persist across instance restarts (but not termination).

### 12. GPU Verification
Verified GPU access and PyTorch CUDA support:
```bash
# Check NVIDIA GPU
nvidia-smi  # Shows NVIDIA A10G with 23GB VRAM

# Verify PyTorch can access GPU
cd ~/ComfyUI
source venv/bin/activate
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
```

Expected output:
```
CUDA available: True
GPU: NVIDIA A10G
```

### 13. Claude Code CLI Installation (Optional)
Installed Claude Code CLI directly on the EC2 instance for terminal-based usage:

```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify Node.js and npm
node --version  # v20.19.5
npm --version   # 10.8.2

# Install Claude Code CLI globally
sudo npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version  # 2.0.36
```

Now you can use Claude Code directly on the EC2 instance:
```bash
ssh comfyui-ec2
cd ~/ComfyUI
claude
```

## Installed Software Versions

- **OS**: Ubuntu 22.04.5 LTS
- **Kernel**: 6.8.0-1040-aws
- **NVIDIA Driver**: 580.95.05
- **CUDA**: 12.9 (default), with 12.6, 12.8, 13.0 also available
- **Python**: 3.10.12
- **PyTorch**: 2.5.1+cu121
- **ComfyUI**: Latest from main branch
- **Node.js**: 20.19.5
- **npm**: 10.8.2
- **Claude Code CLI**: 2.0.36

## Package Details

The ComfyUI installation includes:
- Core ComfyUI packages (frontend, workflow templates, embedded docs)
- PyTorch ecosystem (torch, torchvision, torchaudio)
- ML libraries (transformers, tokenizers, safetensors)
- Image processing (Pillow, kornia, einops)
- Utilities (aiohttp, pyyaml, tqdm, psutil)
- Video processing (av)
- Model handling (spandrel, sentencepiece)

## Instance Management Commands

### Check instance status:
```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-05e0226ee5b99ace1 \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]'
```

### Stop instance (to save costs):
```bash
aws ec2 stop-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1
```

### Start instance:
```bash
aws ec2 start-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1
```

### Get new public IP after restart:
```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-05e0226ee5b99ace1 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

### Terminate instance (permanent):
```bash
aws ec2 terminate-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1
```

## Troubleshooting

### Cannot connect via SSH
1. Check instance is running: `aws ec2 describe-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1`
2. Verify security group allows your IP
3. Check SSH key permissions: `chmod 400 ~/.ssh/comfyui-claude-code.pem`
4. If IP changed after restart, update `~/.ssh/config`

### GPU not detected
1. Check NVIDIA driver: `nvidia-smi`
2. Verify CUDA environment: `nvcc --version`
3. Check PyTorch installation: `python -c "import torch; print(torch.cuda.is_available())"`

### ComfyUI fails to start
1. Ensure virtual environment is activated: `source ~/ComfyUI/venv/bin/activate`
2. Check Python version: `python --version` (should be 3.10+)
3. Reinstall requirements: `pip install -r ~/ComfyUI/requirements.txt`
4. Check disk space: `df -h`
