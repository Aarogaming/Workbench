"""
AAS-283: Voice Input/Output Support

Integrates voice processing capabilities including speech recognition,
text-to-speech synthesis, and voice-based interactions.
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
import shutil
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""

    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"


class Language(Enum):
    """Supported languages"""

    EN_US = "en-US"
    EN_GB = "en-GB"
    ES = "es-ES"
    FR = "fr-FR"
    DE = "de-DE"
    ZH_CN = "zh-CN"
    JA = "ja-JP"


@dataclass
class VoiceConfig:
    """Voice interaction configuration"""

    language: Language = Language.EN_US
    audio_format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 16000  # Hz
    sample_width: int = 2  # bytes (16-bit PCM)
    enable_echo_cancellation: bool = True
    enable_noise_suppression: bool = True
    speech_recognition_timeout: int = 30  # seconds
    voice_activity_threshold: float = 0.5
    tts_backend: Optional[str] = None  # auto | pyttsx3 | system_speech | espeak | say | noop
    asr_backend: Optional[str] = None  # auto | google | sphinx | vosk | noop
    chunk_size: int = 4096
    input_device_index: Optional[int] = None


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def _is_windows() -> bool:
    return os.name == "nt"


class TextToSpeechEngine:
    """Convert text to speech"""

    def __init__(self, config: VoiceConfig):
        self.config = config
        self._voice_params = {"pitch": 1.0, "rate": 1.0, "volume": 1.0}
        self._pyttsx3_engine = None

    def synthesize(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Convert text to speech audio"""
        if not text:
            return b""

        backend = self._resolve_backend()
        if backend == "noop":
            return b""

        if backend == "pyttsx3":
            audio = self._synth_pyttsx3(text, voice_id=voice_id)
        elif backend == "system_speech":
            audio = self._synth_system_speech(text, voice_id=voice_id)
        elif backend == "espeak":
            audio = self._synth_espeak(text, voice_id=voice_id)
        elif backend == "say":
            audio = self._synth_say(text, voice_id=voice_id)
        else:
            raise RuntimeError(f"Unsupported TTS backend: {backend}")

        return self._convert_if_needed(audio)

    def synthesize_with_callbacks(
        self,
        text: str,
        on_chunk: Callable[[bytes], None],
        voice_id: Optional[str] = None,
    ):
        """Stream speech synthesis with callbacks"""
        audio = self.synthesize(text, voice_id=voice_id)
        chunk_size = max(256, int(self.config.chunk_size))
        for offset in range(0, len(audio), chunk_size):
            on_chunk(audio[offset : offset + chunk_size])

    def set_voice_params(
        self, pitch: float = 1.0, rate: float = 1.0, volume: float = 1.0
    ):
        """Adjust voice parameters"""
        self._voice_params = {
            "pitch": max(0.1, float(pitch)),
            "rate": max(0.1, float(rate)),
            "volume": max(0.0, min(1.0, float(volume))),
        }

    def _resolve_backend(self) -> str:
        override = (self.config.tts_backend or "").strip().lower()
        if override and override != "auto":
            return override

        if self._can_use_pyttsx3():
            return "pyttsx3"
        if _is_windows():
            return "system_speech"
        if _which("espeak"):
            return "espeak"
        if _which("say"):
            return "say"
        return "noop"

    def _can_use_pyttsx3(self) -> bool:
        try:
            import pyttsx3  # noqa: F401

            return True
        except Exception:
            return False

    def _synth_pyttsx3(self, text: str, voice_id: Optional[str]) -> bytes:
        import pyttsx3

        if self._pyttsx3_engine is None:
            self._pyttsx3_engine = pyttsx3.init()

        engine = self._pyttsx3_engine
        if voice_id:
            try:
                engine.setProperty("voice", voice_id)
            except Exception:
                logger.warning("pyttsx3 voice id not supported: %s", voice_id)

        engine.setProperty("rate", int(200 * self._voice_params["rate"]))
        engine.setProperty("volume", self._voice_params["volume"])

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            return _read_bytes(temp_path)
        finally:
            _safe_unlink(temp_path)

    def _synth_system_speech(self, text: str, voice_id: Optional[str]) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        script = [
            "Add-Type -AssemblyName System.Speech;",
            "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;",
        ]
        if voice_id:
            script.append(f"$synth.SelectVoice('{voice_id}');")
        rate = int(0 + (self._voice_params["rate"] - 1.0) * 5)
        volume = int(self._voice_params["volume"] * 100)
        script.append(f"$synth.Rate = {rate};")
        script.append(f"$synth.Volume = {volume};")
        script.append(f"$synth.SetOutputToWaveFile('{temp_path}');")
        script.append("$input = [Console]::In.ReadToEnd();")
        script.append("$synth.Speak($input);")
        script.append("$synth.Dispose();")
        command = ["powershell", "-NoProfile", "-Command", " ".join(script)]
        try:
            subprocess.run(command, input=text.encode("utf-8"), check=True)
            return _read_bytes(temp_path)
        finally:
            _safe_unlink(temp_path)

    def _synth_espeak(self, text: str, voice_id: Optional[str]) -> bytes:
        cmd = ["espeak", "--stdout"]
        if voice_id:
            cmd.extend(["-v", voice_id])
        rate = int(175 * self._voice_params["rate"])
        pitch = int(50 * self._voice_params["pitch"])
        volume = int(100 * self._voice_params["volume"])
        cmd.extend(["-s", str(rate), "-p", str(pitch), "-a", str(volume)])
        result = subprocess.run(cmd, input=text.encode("utf-8"), check=True, capture_output=True)
        return result.stdout

    def _synth_say(self, text: str, voice_id: Optional[str]) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        cmd = ["say", "-o", temp_path]
        if voice_id:
            cmd.extend(["-v", voice_id])
        cmd.append(text)
        try:
            subprocess.run(cmd, check=True)
            return _read_bytes(temp_path)
        finally:
            _safe_unlink(temp_path)

    def _convert_if_needed(self, audio_data: bytes) -> bytes:
        if self.config.audio_format == AudioFormat.WAV:
            return audio_data

        ffmpeg = _which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("ffmpeg is required to convert audio formats")

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "tts.wav")
            output_path = os.path.join(temp_dir, f"tts.{self.config.audio_format.value}")
            with open(input_path, "wb") as handle:
                handle.write(audio_data)
            subprocess.run(
                [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", input_path, output_path],
                check=True,
            )
            return _read_bytes(output_path)


class SpeechRecognitionEngine:
    """Convert speech to text"""

    def __init__(self, config: VoiceConfig):
        self.config = config
        self.is_listening = False
        self._confidence_threshold = 0.0
        self._stop_listening = None
        self._recognizer = None

    def recognize(self, audio_data: bytes) -> str:
        """Recognize speech from audio data"""
        if not audio_data:
            return ""

        sr = self._speech_recognition()
        recognizer = self._recognizer or sr.Recognizer()
        self._recognizer = recognizer

        if self.config.audio_format not in (AudioFormat.WAV, AudioFormat.FLAC):
            raise RuntimeError("Speech recognition expects WAV or FLAC audio data")

        with sr.AudioFile(io.BytesIO(audio_data)) as source:
            audio = recognizer.record(source)

        return self._recognize_audio(recognizer, audio, sr)

    def recognize_microphone(self, timeout_seconds: Optional[int] = None) -> str:
        sr = self._speech_recognition()
        recognizer = self._recognizer or sr.Recognizer()
        self._recognizer = recognizer

        with sr.Microphone(sample_rate=self.config.sample_rate, device_index=self.config.input_device_index) as source:
            audio = recognizer.listen(
                source,
                timeout=timeout_seconds,
                phrase_time_limit=timeout_seconds,
            )
        return self._recognize_audio(recognizer, audio, sr)

    def start_continuous_recognition(self, on_result: Callable[[str], None]):
        """Start continuous listening"""
        sr = self._speech_recognition()
        recognizer = self._recognizer or sr.Recognizer()
        self._recognizer = recognizer

        def callback(recognizer, audio):
            try:
                text = self._recognize_audio(recognizer, audio, sr)
                if text:
                    on_result(text)
            except Exception as exc:
                logger.warning("Continuous recognition error: %s", exc)

        microphone = sr.Microphone(sample_rate=self.config.sample_rate, device_index=self.config.input_device_index)
        self._stop_listening = recognizer.listen_in_background(microphone, callback)
        self.is_listening = True

    def stop_continuous_recognition(self):
        """Stop listening"""
        if self._stop_listening:
            self._stop_listening(wait_for_stop=False)
            self._stop_listening = None
        self.is_listening = False

    def set_confidence_threshold(self, threshold: float):
        """Set minimum confidence for results (0-1)"""
        self._confidence_threshold = max(0.0, min(1.0, float(threshold)))

    def _recognize_audio(self, recognizer, audio, sr) -> str:
        backend = (self.config.asr_backend or "auto").lower()
        language = self.config.language.value

        if backend == "noop":
            return ""
        if backend in ("auto", "google"):
            return recognizer.recognize_google(audio, language=language)
        if backend == "sphinx":
            return recognizer.recognize_sphinx(audio, language=language)
        raise RuntimeError(f"Unsupported ASR backend: {backend}")

    def _speech_recognition(self):
        try:
            import speech_recognition as sr

            return sr
        except Exception as exc:
            raise RuntimeError("speech_recognition package is required for ASR") from exc


class VoiceInteraction:
    """Unified voice input/output interface"""

    def __init__(self, config: VoiceConfig):
        self.config = config
        self.tts_engine = TextToSpeechEngine(config)
        self.asr_engine = SpeechRecognitionEngine(config)

    async def speak(self, text: str) -> None:
        """Speak text asynchronously"""
        audio_data = self.tts_engine.synthesize(text)
        await asyncio.to_thread(self._play_audio_bytes, audio_data)

    async def listen(self, timeout_seconds: Optional[int] = None) -> str:
        """Listen for speech and return text"""
        return await asyncio.to_thread(self.asr_engine.recognize_microphone, timeout_seconds)

    async def conversation_turn(self, prompt_text: str) -> str:
        """Single turn: speak prompt, listen for response"""
        await self.speak(prompt_text)
        response = await self.listen(self.config.speech_recognition_timeout)
        return response

    def configure_voice(
        self, language: Language, audio_format: AudioFormat, sample_rate: int
    ):
        """Reconfigure voice settings"""
        self.config.language = language
        self.config.audio_format = audio_format
        self.config.sample_rate = sample_rate

    def _play_audio_bytes(self, audio_data: bytes) -> None:
        if not audio_data:
            return

        if _is_windows() and self.config.audio_format == AudioFormat.WAV:
            try:
                import winsound

                winsound.PlaySound(audio_data, winsound.SND_MEMORY)
                return
            except Exception as exc:
                logger.warning("winsound playback failed: %s", exc)

        try:
            import simpleaudio  # type: ignore

            with wave.open(io.BytesIO(audio_data), "rb") as wav_file:
                wave_obj = simpleaudio.WaveObject.from_wave_read(wav_file)
                play_obj = wave_obj.play()
                play_obj.wait_done()
                return
        except Exception:
            pass

        player = _which("ffplay") or _which("afplay") or _which("aplay")
        if player:
            with tempfile.NamedTemporaryFile(
                suffix=f".{self.config.audio_format.value}", delete=False
            ) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            try:
                if os.path.basename(player).lower() == "ffplay":
                    subprocess.run(
                        [player, "-nodisp", "-autoexit", "-loglevel", "error", temp_path],
                        check=False,
                    )
                else:
                    subprocess.run([player, temp_path], check=False)
            finally:
                _safe_unlink(temp_path)
            return

        logger.warning("No audio playback backend available")


class VoiceCommandDispatcher:
    """Dispatch recognized commands to handlers"""

    def __init__(self):
        self.handlers: dict[str, Callable] = {}

    def register_command(self, command_pattern: str, handler: Callable):
        """Register voice command handler"""
        self.handlers[command_pattern] = handler

    def dispatch(self, recognized_text: str) -> Optional[str]:
        """Match text to handler and dispatch"""
        for pattern, handler in self.handlers.items():
            if pattern.lower() in recognized_text.lower():
                return handler(recognized_text)
        return None


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def _safe_unlink(path: str) -> None:
    try:
        os.unlink(path)
    except Exception:
        pass


# Export public API
__all__ = [
    "AudioFormat",
    "Language",
    "VoiceConfig",
    "TextToSpeechEngine",
    "SpeechRecognitionEngine",
    "VoiceInteraction",
    "VoiceCommandDispatcher",
]
