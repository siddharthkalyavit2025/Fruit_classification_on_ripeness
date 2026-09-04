import requests
from PIL import Image
import io
import json

img = Image.new('RGB', (224, 224), color=(200, 50, 50))
buffer = io.BytesIO()
img.save(buffer, format='JPEG')
buffer.seek(0)

print("Sending sample image to http://localhost:8000/predict...")
response = requests.post(
    "http://localhost:8000/predict",
    files={"file": ("test_apple.jpg", buffer, "image/jpeg")}
)

print("Status Code:", response.status_code)
print(json.dumps(response.json(), indent=2, ensure_ascii=True))
