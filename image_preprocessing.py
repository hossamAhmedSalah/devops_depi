import numpy as np
import json
from PIL import Image
import sys

# Check if the correct number of arguments were provided
if len(sys.argv) != 3:
    print("Usage: python script.py <image_path> <mode>")
    sys.exit(1)

image_path = sys.argv[1]
mode = sys.argv[2]

# Load and preprocess image
image = Image.open(image_path).resize((224, 224))
image_array = np.array(image) / 255.0
image_array = np.expand_dims(image_array, axis=0)

# Prepare the JSON payload
request_payload = {"instances": [image_array[0].tolist()]}

# Load the existing request_payload.json file if it exists
try:
    with open('request_payload.json', 'r') as f:
        existing_payload = json.load(f)
except FileNotFoundError:
    existing_payload = {"instances": []}

# Append to the existing payload if mode is 'append', otherwise start from scratch
if mode == 'append':
    existing_payload["instances"].append(request_payload["instances"][0])
    request_payload = existing_payload
elif mode == 'overwrite':
    pass  # Do nothing, just use the new payload
else:
    print("Invalid mode. Please use 'append' or 'overwrite'.")
    sys.exit(1)

# Save the request payload to a JSON file
with open('request_payload.json', 'w') as f:
    json.dump(request_payload, f)
