import requests
import json
import base64
import time
from typing import Optional

class FusionBrainAPI:
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://api-key.fusionbrain.ai/"):
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.headers = {
            "X-Key": f"Key {api_key}",
            "X-Secret": f"Secret {secret_key}",
        }

    def get_pipelines(self):
        url = self.base_url + "key/api/v1/pipelines"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def generate(self, prompt: str, pipeline_id: str, width: int = 1024, height: int = 1024, num_images: int = 1) -> str:
        url = self.base_url + "key/api/v1/pipeline/run"
        params = {
            "type": "GENERATE",
            "numImages": num_images,
            "width": width,
            "height": height,
            "generateParams": {"query": prompt}
        }
        files = {
            "pipeline_id": (None, pipeline_id),
            "params": (None, json.dumps(params), "application/json"),
        }
        r = requests.post(url, headers=self.headers, files=files)
        r.raise_for_status()
        data = r.json()
        return data["uuid"]

    def get_status(self, uuid: str) -> dict:
        url = self.base_url + f"key/api/v1/pipeline/status/{uuid}"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def get_image(self, prompt: str, output_file: str = "generated.png",
                  width: int = 1024, height: int = 1024,
                  timeout: int = 120, poll_interval: float = 2.0) -> str:
        # 1️⃣ Берём первый пайплайн (Kandinsky 3.1)
        pipelines = self.get_pipelines()
        if not pipelines:
            raise RuntimeError("❌ Нет доступных моделей (pipelines).")
        pipeline_id = pipelines[0].get("uuid") or pipelines[0].get("id")

        # 2️⃣ Запускаем генерацию
        uuid = self.generate(prompt, pipeline_id, width, height)

        # 3️⃣ Ждём завершения
        start = time.time()
        while True:
            status_json = self.get_status(uuid)
            status = status_json.get("status")
            if status == "DONE":
                files = status_json.get("result", {}).get("files", [])
                if not files:
                    raise RuntimeError("❌ Генерация завершилась без файлов.")
                b64 = files[0]
                img_bytes = base64.b64decode(b64)
                with open(output_file, "wb") as f:
                    f.write(img_bytes)
                return output_file
            if status == "FAIL":
                raise RuntimeError(f"❌ Ошибка генерации: {status_json}")
            if time.time() - start > timeout:
                raise TimeoutError("⏳ Время ожидания истекло.")
            time.sleep(poll_interval)