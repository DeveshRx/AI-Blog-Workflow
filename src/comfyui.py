import os
import websocket
import uuid
import json
import urllib.request
import urllib.parse
import io
from PIL import Image
import secrets
from src.ImgConvert import convert_png_to_webp
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

load_dotenv() 

COMFYUI_URL = os.getenv("COMFYUI_URL")

server_address = COMFYUI_URL
client_id = str(uuid.uuid4())
workflow_path = "src/workflows/blog_thumbnail.json"

def getDate():
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %I:%M:%S %p")
    return formatted_time


def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())


def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(
        f"http://{server_address}/view?{url_values}"
    ) as response:
        return response.read()


def get_history(prompt_id):
    with urllib.request.urlopen(
        f"http://{server_address}/history/{prompt_id}"
    ) as response:
        return json.loads(response.read())


def unload_models(unload_models=True, free_memory=True):
    """
    unload_models: Removes model weights (Checkpoints, LoRAs) from VRAM/RAM.
    free_memory: Clears the execution cache (garbage collection).
    """
    payload = {"unload_models": unload_models, "free_memory": free_memory}

    data = json.dumps(payload).encode("utf-8")
    url = f"http://{server_address}/free"

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            print("Successfully freed memory and unloaded models.")
        else:
            print(f"Failed to free memory. Status: {response.status}")


def generate_image_thumbnail(img_filename, prompt_text):
    # 1. Load the workflow
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)
        
    # Set a random seed for variability
    workflow["57:3"]["inputs"]["seed"] = secrets.randbelow(4294967295)

    # 2. (Optional) Modify the prompt dynamically
    # Note: You must find the ID of your 'CLIP Text Encode' node in the JSON
    if prompt_text:
        # Common default ID for positive prompt is "6"
        workflow["58"]["inputs"]["value"] = prompt_text
        print(f"Set prompt text to: {workflow['58']['inputs']['value']}")
    else:
        print("No prompt text provided; using default from workflow.")

    # 3. Connect to WebSocket to track progress
    ws = websocket.WebSocket()
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

    # 4. Queue the job
    print("Queuing prompt...")
    prompt_id = queue_prompt(workflow)["prompt_id"]

    # 5. Wait for the 'executing' message to finish
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break  # Execution is done
        else:
            continue  # Binary data (previews) are ignored here

    # 6. Retrieve the image from history
    history = get_history(prompt_id)[prompt_id]
    for node_id in history["outputs"]:
        node_output = history["outputs"][node_id]
        if "images" in node_output:
            for image in node_output["images"]:
                image_data = get_image(
                    image["filename"], image["subfolder"], image["type"]
                )
                img = Image.open(io.BytesIO(image_data))
                img.save(f"{img_filename}.png")
                convert_png_to_webp(f"{img_filename}.png", f"{img_filename}.webp", quality=80)
                old_img_file_path = Path(f"{img_filename}.png")

                if old_img_file_path.exists():
                    old_img_file_path.unlink()  # Delete the original PNG file
                else:
                    print(f"Error: {img_filename}.png not found for deletion.")                

                print(f"{getDate} Saved: {img_filename}.png")

    ws.close()
    


