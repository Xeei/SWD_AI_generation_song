import abc
import os
import uuid

import requests

SUNO_API_TOKEN = os.environ.get("SUNO_API_TOKEN", "")
SUNO_API_BASE_URL = os.environ.get("SUNO_API_BASE_URL", "https://api.sunoapi.org")
CALLBACK_BASE_URL = os.environ.get("CALLBACK_BASE_URL", "http://localhost:8000")

_MOCK_AUDIO_BASE = f"{CALLBACK_BASE_URL}/api/mock-audio"

_STYLE_TO_FILE = {
    "Happy, uplifting": "happy.mp3",
    "Sad, melancholic": "sad.mp3",
    "Upbeat, energetic": "upbeat.mp3",
    "Romantic, tender": "romantic.mp3",
    "Chill, relaxing": "chill.mp3",
    "Epic, cinematic": "epic.mp3",
}
_DEFAULT_MOCK_FILE = "happy.mp3"


# ABtract CLass for hide how it work inside 
class SongGenerateStrategy(abc.ABC):
    @abc.abstractmethod
    def generate(self, title: str, style: str, callback_url: str, vocal_gender: str, prompt: str = "") -> str:
        """Submit generation job. Returns task_id."""

    @abc.abstractmethod
    def check_task(self, task_id: str) -> dict:
        """Poll task status. Returns Suno-format response dict."""


class SunoStrategy(SongGenerateStrategy):
    def generate(self, title, style, callback_url, vocal_gender, prompt="") -> str:
        url = f"{SUNO_API_BASE_URL}/api/v1/generate"
        payload = {
            "customMode": True,
            "instrumental": False,
            "model": "V4",
            "title": title,
            "style": style,
            "callBackUrl": callback_url,
            "vocalGender": vocal_gender,
            "prompt": prompt,
        }
        headers = {
            "Authorization": f"Bearer {SUNO_API_TOKEN}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json()["data"]["taskId"]
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Suno API error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Suno API unreachable: {e}")

    def check_task(self, task_id: str) -> dict:
        url = f"{SUNO_API_BASE_URL}/api/v1/generate/record-info"
        headers = {"Authorization": f"Bearer {SUNO_API_TOKEN}"}
        resp = requests.get(url, params={"taskId": task_id}, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()


class MockStrategy(SongGenerateStrategy):
    _pending: dict[str, str] = {}  # task_id -> audio_url

    def generate(self, title, style, callback_url, vocal_gender, prompt="") -> str:
        task_id = f"mock_{uuid.uuid4().hex}"
        filename = _STYLE_TO_FILE.get(style, _DEFAULT_MOCK_FILE)
        MockStrategy._pending[task_id] = f"{_MOCK_AUDIO_BASE}/{filename}"
        return task_id

    def check_task(self, task_id: str) -> dict:
        audio_url = MockStrategy._pending.get(
            task_id, f"{_MOCK_AUDIO_BASE}/{_DEFAULT_MOCK_FILE}"
        )
        return {
            "code": 200,
            "data": {
                "taskId": task_id,
                "status": "SUCCESS",
                "response": {
                    "sunoData": [{
                        "audioUrl": audio_url,
                        "sourceAudioUrl": audio_url,
                        "duration": 180,
                        "title": "Mock Song",
                    }]
                },
            },
        }


_instance: SongGenerateStrategy | None = None


def get_strategy() -> SongGenerateStrategy:
    global _instance
    if _instance is None:
        name = os.environ.get("GENERATOR_STRATEGY", "suno").lower()
        _instance = MockStrategy() if name == "mock" else SunoStrategy()
    return _instance
