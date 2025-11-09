# ComfyUI Workflows

This directory contains ComfyUI workflow JSON files. The workflows are symlinked to the ComfyUI installation for easy access.

## Available Workflows

### Combine Styles Workflow.json
Combines style transfer with pose control using:
- **IP-Adapter** for style reference from an image
- **ControlNet MLSD** for pose/structure guidance
- **SDXL Base** for high-quality image generation

**Required Models:**
- sd_xl_base_1.0.safetensors
- control_v11p_sd15_mlsd.pth
- ip-adapter_sdxl.safetensors

**Required Inputs:**
- `sunset_smoke_3_small_balls.png` - Style reference image
- `pose_reference.png` - Pose/structure control image

## Usage

### In ComfyUI Web Interface
1. Start ComfyUI: `~/start-comfyui.sh`
2. Open browser: http://localhost:8188
3. Load workflow: Drag and drop the JSON file onto the interface

### Programmatically (Python)
```python
import json
from urllib import request

# Load workflow
with open('Combine Styles Workflow.json', 'r') as f:
    workflow = json.load(f)

# Queue the workflow
data = json.dumps({"prompt": workflow}).encode('utf-8')
req = request.Request("http://127.0.0.1:8188/prompt", data=data)
response = request.urlopen(req)
```

## Creating New Workflows

1. Design workflow in ComfyUI web interface
2. Export workflow: `File → Export (API Format)`
3. Save to this directory
4. Document required models and inputs
5. Commit to git

## Workflow Structure

ComfyUI workflows are JSON files containing:
- **nodes**: Individual processing steps (loaders, samplers, encoders, etc.)
- **links**: Connections between nodes
- **widgets_values**: Parameters for each node

## Testing Workflows

Before committing a new workflow:
1. Test it runs successfully in ComfyUI
2. Document all model requirements in models/models_manifest.txt
3. Include sample input images in ../input/
4. Add any custom nodes to ../custom_nodes/

## Symlink

This directory is symlinked from ComfyUI:
```
/home/ubuntu/ComfyUI/workflows → /home/ubuntu/refgen/workflows
```

Changes made here are immediately visible in ComfyUI.
