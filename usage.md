# ComfyUI EC2 Usage Guide

This guide covers how to use the ComfyUI EC2 instance with Claude Code for iterative development.

## Instance Details

- **Instance ID**: `i-05e0226ee5b99ace1`
- **Instance Type**: g5.xlarge (NVIDIA A10G with 24GB VRAM)
- **Region**: us-east-1
- **Public IP**: 34.235.112.212 (changes after stop/start)
- **Private IP**: 172.31.36.172
- **Storage**: 100GB gp3
- **Cost**: ~$1.00/hour when running

## Connecting to the Instance

### Option 1: Simple SSH

The SSH config is already set up, so you can connect with:
```bash
ssh comfyui-ec2
```

### Option 2: VS Code Remote SSH

This is the recommended method for Claude Code integration:

1. **Install Extension**
   - Open VS Code
   - Install the "Remote - SSH" extension (ms-vscode-remote.remote-ssh)

2. **Connect to Host**
   - Press `F1` or `Cmd+Shift+P`
   - Type "Remote-SSH: Connect to Host"
   - Select `comfyui-ec2` from the list
   - VS Code will open a new window connected to the remote instance

3. **Open ComfyUI Folder**
   - In the remote VS Code window, go to File → Open Folder
   - Navigate to `/home/ubuntu/ComfyUI`
   - Click OK

4. **Use Claude Code**
   - Now Claude Code can see and edit all ComfyUI files
   - Run terminal commands directly on the remote instance
   - See console output in real-time

### Option 3: Claude Code CLI (Directly on EC2)

Claude Code CLI is installed directly on the EC2 instance. You can use it after SSH-ing in:

```bash
ssh comfyui-ec2
cd ~/ComfyUI
claude
```

This gives you Claude Code running directly in the remote environment, with full access to the GPU, files, and ComfyUI installation.

### Using Claude Code

**Via VS Code Remote SSH (Option 2)**:
- Claude Code works automatically when you connect via VS Code Remote SSH
- All file operations and terminal commands run on the remote instance
- Full Claude Code functionality in the remote environment

**Via CLI (Option 3)**:
- SSH into the instance and run `claude` command
- Claude operates directly in the terminal on the remote machine
- Useful for quick tasks or when you prefer terminal-based workflow

## Running ComfyUI

### Quick Start

Use the helper script:
```bash
ssh comfyui-ec2
~/start-comfyui.sh
```

### Manual Start

```bash
ssh comfyui-ec2
cd ~/ComfyUI
source venv/bin/activate
python main.py
```

### With Custom Options

```bash
cd ~/ComfyUI
source venv/bin/activate

# Listen on all interfaces
python main.py --listen 0.0.0.0 --port 8188

# Enable auto-launch browser (if using X11 forwarding)
python main.py --auto-launch

# Specify custom model paths
python main.py --extra-model-paths-config extra_model_paths.yaml

# Enable preview method
python main.py --preview-method auto

# Run with specific GPU
CUDA_VISIBLE_DEVICES=0 python main.py
```

## Common Development Workflows

### 1. Editing Custom Nodes

Custom nodes are located in `~/ComfyUI/custom_nodes/`:

```bash
# From your local machine with VS Code Remote SSH:
# 1. Connect to comfyui-ec2
# 2. Navigate to /home/ubuntu/ComfyUI/custom_nodes
# 3. Edit Python files directly
# 4. Claude Code can now see errors and iterate on fixes
```

### 2. Testing Workflow Changes

```bash
# Workflows are JSON files, typically in:
cd ~/ComfyUI/user/default/workflows/

# Edit with Claude Code, then test in running ComfyUI instance
```

### 3. Installing Custom Nodes

```bash
ssh comfyui-ec2
cd ~/ComfyUI/custom_nodes
git clone <custom-node-repo>
cd <custom-node-repo>
source ~/ComfyUI/venv/bin/activate
pip install -r requirements.txt
```

### 4. Downloading Models

Models go in specific directories:

```bash
# Checkpoints (Stable Diffusion models)
~/ComfyUI/models/checkpoints/

# VAE models
~/ComfyUI/models/vae/

# LoRA models
~/ComfyUI/models/loras/

# ControlNet models
~/ComfyUI/models/controlnet/

# Example: Download a model
cd ~/ComfyUI/models/checkpoints/
wget https://huggingface.co/...model.safetensors
```

### 5. Viewing Logs

```bash
# If running ComfyUI in the background
tail -f ~/ComfyUI/comfyui.log

# Or run in foreground to see logs directly
cd ~/ComfyUI
source venv/bin/activate
python main.py
```

## Instance Management

### Starting the Instance

```bash
# Start the stopped instance
aws ec2 start-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1

# Wait for it to be running
aws ec2 wait instance-running --region us-east-1 --instance-ids i-05e0226ee5b99ace1

# Get the new public IP
NEW_IP=$(aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-05e0226ee5b99ace1 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "New IP: $NEW_IP"

# Update SSH config
sed -i.bak "s/HostName .*/HostName $NEW_IP/" ~/.ssh/config
```

### Stopping the Instance

**Important**: Always stop the instance when not in use to avoid charges!

```bash
# Stop the instance
aws ec2 stop-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1

# Verify it's stopped
aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-05e0226ee5b99ace1 \
  --query 'Reservations[0].Instances[0].State.Name'
```

### Checking Instance Status

```bash
# Quick status check
aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-05e0226ee5b99ace1 \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress,InstanceType]' \
  --output table
```

### Checking Costs

```bash
# Check current month's EC2 costs (requires AWS Cost Explorer)
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter file://<(echo '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Elastic Compute Cloud - Compute"]}}')
```

## GPU Monitoring

### Check GPU Usage

```bash
ssh comfyui-ec2

# Real-time GPU monitoring
nvidia-smi

# Continuous monitoring (updates every 2 seconds)
watch -n 2 nvidia-smi

# Detailed GPU info
nvidia-smi -q

# Check temperature and power
nvidia-smi --query-gpu=temperature.gpu,power.draw,utilization.gpu --format=csv
```

### Check VRAM Usage

```bash
# Inside ComfyUI Python environment
cd ~/ComfyUI
source venv/bin/activate
python -c "import torch; print(f'Allocated: {torch.cuda.memory_allocated(0)/1024**3:.2f}GB'); print(f'Reserved: {torch.cuda.memory_reserved(0)/1024**3:.2f}GB')"
```

## Backup and Snapshots

### Create EBS Snapshot

```bash
# Get the volume ID
VOLUME_ID=$(aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-05e0226ee5b99ace1 \
  --query 'Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId' \
  --output text)

# Create snapshot
aws ec2 create-snapshot \
  --region us-east-1 \
  --volume-id $VOLUME_ID \
  --description "ComfyUI instance backup $(date +%Y-%m-%d)" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=ComfyUI-Backup}]'
```

### Backup Custom Work

```bash
# From local machine, backup custom nodes and workflows
rsync -av --progress comfyui-ec2:~/ComfyUI/custom_nodes/ ./backup/custom_nodes/
rsync -av --progress comfyui-ec2:~/ComfyUI/user/ ./backup/user/
rsync -av --progress comfyui-ec2:~/ComfyUI/output/ ./backup/output/
```

## Troubleshooting

### ComfyUI Won't Start

```bash
# Check Python environment
ssh comfyui-ec2
cd ~/ComfyUI
source venv/bin/activate
python --version  # Should be 3.10+

# Check dependencies
pip list | grep torch

# Reinstall if needed
pip install -r requirements.txt
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clear old outputs
rm -rf ~/ComfyUI/output/*

# Clear pip cache
rm -rf ~/.cache/pip

# Clear apt cache
sudo apt-get clean
```

### Connection Issues After Restart

The public IP changes when you stop/start the instance:

```bash
# Get new IP
aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-05e0226ee5b99ace1 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# Update ~/.ssh/config with new HostName
```

### GPU Out of Memory

```bash
# Inside Python/ComfyUI
import torch
torch.cuda.empty_cache()

# Or restart ComfyUI to clear VRAM
```

## Performance Tips

### Optimize ComfyUI Performance

1. **Use FP16/BF16** for faster inference with lower VRAM
2. **Enable xformers** if compatible with your PyTorch version
3. **Adjust batch sizes** in workflows to fit within 24GB VRAM
4. **Use model offloading** for very large models

### Monitor Resource Usage

```bash
# CPU and memory
htop

# Disk I/O
iotop

# Network
iftop
```

## SSH Key Location

Your SSH private key is stored at:
```
~/.ssh/comfyui-claude-code.pem
```

**Keep this secure!** This key provides access to your EC2 instance.

## Quick Reference

| Command | Description |
|---------|-------------|
| `ssh comfyui-ec2` | Connect to instance |
| `claude` | Start Claude Code CLI (after SSH) |
| `~/start-comfyui.sh` | Start ComfyUI |
| `nvidia-smi` | Check GPU status |
| `aws ec2 stop-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1` | Stop instance |
| `aws ec2 start-instances --region us-east-1 --instance-ids i-05e0226ee5b99ace1` | Start instance |
| `cd ~/ComfyUI && source venv/bin/activate` | Activate Python environment |
