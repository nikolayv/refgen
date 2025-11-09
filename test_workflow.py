#!/usr/bin/env python3
"""Test the ComfyUI workflow via API"""

import json
import urllib.request
import urllib.parse
import time
import sys

def queue_prompt(prompt):
    """Queue a prompt to ComfyUI"""
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data, headers={'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response: {error_body}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def convert_ui_to_api(workflow_ui):
    """Convert UI format workflow to API format"""
    api_workflow = {}

    # Create a map of node IDs to their data
    for node in workflow_ui["nodes"]:
        node_id = str(node["id"])
        api_workflow[node_id] = {
            "class_type": node["type"],
            "inputs": {}
        }

        # Add widget values
        if "widgets_values" in node and node["widgets_values"]:
            # Map widget values to their parameter names based on node type
            # For now, we'll use them as positional parameters
            api_workflow[node_id]["inputs"]["_widgets"] = node["widgets_values"]

    # Process links to create input connections
    for link in workflow_ui["links"]:
        link_id, source_node, source_slot, target_node, target_slot, link_type = link
        source_node_str = str(source_node)
        target_node_str = str(target_node)

        # Find the target input name
        target_node_data = next((n for n in workflow_ui["nodes"] if n["id"] == target_node), None)
        if target_node_data and "inputs" in target_node_data:
            target_input = target_node_data["inputs"][target_slot]
            input_name = target_input["name"]

            # Connect source to target
            api_workflow[target_node_str]["inputs"][input_name] = [source_node_str, source_slot]

    # Add widget values properly
    for node in workflow_ui["nodes"]:
        node_id = str(node["id"])
        if "widgets_values" in node and node["widgets_values"]:
            widgets = node["widgets_values"]
            node_type = node["type"]

            # Map widgets to parameter names based on node type
            if node_type == "CheckpointLoaderSimple":
                api_workflow[node_id]["inputs"]["ckpt_name"] = widgets[0]
            elif node_type == "CLIPTextEncode":
                api_workflow[node_id]["inputs"]["text"] = widgets[0]
            elif node_type == "SaveImage":
                api_workflow[node_id]["inputs"]["filename_prefix"] = widgets[0]
            elif node_type == "EmptyLatentImage":
                api_workflow[node_id]["inputs"]["width"] = widgets[0]
                api_workflow[node_id]["inputs"]["height"] = widgets[1]
                api_workflow[node_id]["inputs"]["batch_size"] = widgets[2]
            elif node_type == "LoadImage":
                api_workflow[node_id]["inputs"]["image"] = widgets[0]
            elif node_type == "ControlNetLoader":
                api_workflow[node_id]["inputs"]["control_net_name"] = widgets[0]
            elif node_type == "ControlNetApply":
                api_workflow[node_id]["inputs"]["strength"] = widgets[0]
            elif node_type == "KSampler":
                api_workflow[node_id]["inputs"]["seed"] = widgets[0]
                api_workflow[node_id]["inputs"]["control_after_generate"] = widgets[1]
                api_workflow[node_id]["inputs"]["steps"] = widgets[2]
                api_workflow[node_id]["inputs"]["cfg"] = widgets[3]
                api_workflow[node_id]["inputs"]["sampler_name"] = widgets[4]
                api_workflow[node_id]["inputs"]["scheduler"] = widgets[5]
                api_workflow[node_id]["inputs"]["denoise"] = widgets[6]
            elif node_type == "IPAdapter":
                # IPAdapterSimple requires: weight, start_at, end_at, weight_type
                api_workflow[node_id]["inputs"]["weight"] = widgets[0] if len(widgets) > 0 else 1.0
                api_workflow[node_id]["inputs"]["start_at"] = widgets[1] if len(widgets) > 1 else 0.0
                api_workflow[node_id]["inputs"]["end_at"] = widgets[2] if len(widgets) > 2 else 1.0
                api_workflow[node_id]["inputs"]["weight_type"] = widgets[3] if len(widgets) > 3 else "standard"
                # If the old format had 4 values like [weight, noise, something, weight_type], use them properly
                if len(widgets) >= 4 and isinstance(widgets[3], str):
                    api_workflow[node_id]["inputs"]["weight_type"] = widgets[3]
            elif node_type == "IPAdapterUnifiedLoader":
                api_workflow[node_id]["inputs"]["preset"] = widgets[0]

        # Remove temporary _widgets key
        if "_widgets" in api_workflow[node_id]["inputs"]:
            del api_workflow[node_id]["inputs"]["_widgets"]

    return api_workflow

def get_queue_status():
    """Get current queue status from ComfyUI"""
    try:
        req = urllib.request.Request("http://127.0.0.1:8188/queue")
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except Exception as e:
        return None

def get_history(prompt_id):
    """Get execution history for a specific prompt"""
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except Exception as e:
        return None

def monitor_progress(prompt_id):
    """Monitor workflow execution progress"""
    print(f"\nMonitoring prompt {prompt_id}...")
    start_time = time.time()
    dots = 0

    while True:
        # Check queue status
        queue = get_queue_status()
        if not queue:
            print("\n✗ Could not get queue status")
            return False

        # Check if prompt is in running queue
        queue_running = queue.get('queue_running', [])
        queue_pending = queue.get('queue_pending', [])

        is_running = any(item[1] == prompt_id for item in queue_running)
        is_pending = any(item[1] == prompt_id for item in queue_pending)

        if is_running:
            # Still executing
            dots += 1
            print("." * (dots % 4) + " " * (3 - (dots % 4)), end='\r', flush=True)
        elif is_pending:
            # In queue, waiting
            print(f"Waiting in queue (position {len([p for p in queue_pending if p[1] != prompt_id]) + 1})...", end='\r', flush=True)
        else:
            # Check if completed successfully
            history = get_history(prompt_id)
            if history and prompt_id in history:
                elapsed = time.time() - start_time
                print(f"\n✓ Workflow completed successfully in {elapsed:.1f} seconds!")

                # Show output info
                outputs = history[prompt_id].get('outputs', {})
                for node_id, node_output in outputs.items():
                    if 'images' in node_output:
                        for img in node_output['images']:
                            filename = img.get('filename', 'unknown')
                            print(f"  Generated: /home/ubuntu/ComfyUI/output/{filename}")
                return True
            else:
                print(f"\n✗ Workflow execution failed or was cancelled")
                return False

        time.sleep(0.5)

if __name__ == "__main__":
    # Load the workflow
    with open('/home/ubuntu/refgen/workflows/workflow.json', 'r') as f:
        workflow_ui = json.load(f)

    print("Converting UI format to API format...")
    api_workflow = convert_ui_to_api(workflow_ui)

    print("\nQueueing prompt...")
    result = queue_prompt(api_workflow)

    if result:
        prompt_id = result.get('prompt_id')
        print(f"✓ Prompt queued with ID: {prompt_id}")

        # Monitor progress
        success = monitor_progress(prompt_id)
        sys.exit(0 if success else 1)
    else:
        print("✗ Failed to queue prompt")
        sys.exit(1)
