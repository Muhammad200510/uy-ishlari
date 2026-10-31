"""Ovoz: nutqni matnga (STT) va matnni nutqqa (TTS). Hammasi ixtiyoriy.

Agar kerakli kutubxonalar o'rnatilmagan bo'lsa, dastur matnli rejimga tushadi va
xatolik bermaydi.
"""

from __future__ import annotations

import os
import tempfile


class VoiceIO:
    def __init__(self, stt_language: str = "uz-UZ", tts_language: str = "uz"):
        self.stt_language = stt_language
        self.tts_language = tts_language
        self._recognizer = None
        self._mic = None
        self._available = self._try_init()

    def _try_init(self) -> bool:
        try:
            import speech_recognition as sr  # noqa: F401

            self._sr = sr
            self._recognizer = sr.Recognizer()
            self._mic = sr.Microphone()
            return True
        except Exception as exc:  # noqa: BLE001
            print(f"[ovoz] Mikrofon/STT mavjud emas ({exc}). Matnli rejim ishlatiladi.")
            return False

    @property
    def available(self) -> bool:
        return self._available

    def listen(self) -> str | None:
        """Mikrofondan eshitib, matnga aylantiradi. Xato bo'lsa None."""
        if not self._available:
            return None
        try:
            with self._mic as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                print("🎙️  Eshityapman... (gapiring)")
                audio = self._recognizer.listen(source, timeout=8, phrase_time_limit=15)
            text = self._recognizer.recognize_google(audio, language=self.stt_language)
            return text
        except self._sr.WaitTimeoutError:
            return None
        except self._sr.UnknownValueError:
            print("[ovoz] Tushunolmadim, qaytaring.")
            return None
        except Exception as exc:  # noqa: BLE001
            print(f"[ovoz] Eshitishda xato: {exc}")
            return None

    def speak(self, text: str) -> None:
        """Matnni o'zbekcha ovozda o'qiydi. Imkoni bo'lmasa — shunchaki yozadi."""
        if not text:
            return
        try:
            from gtts import gTTS

            tts = gTTS(text=text, lang=self.tts_language)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
                path = fp.name
            tts.save(path)
            self._play(path)
            try:
                os.remove(path)
            except OSError:
                pass
        except Exception as exc:  # noqa: BLE001
            print(f"[ovoz] Ovozli o'qish imkoni bo'lmadi ({exc}).")

    @staticmethod
    def _play(path: str) -> None:
        # 1-urinish: playsound
        try:
            from playsound import playsound

            playsound(path)
            return
        except Exception:  # noqa: BLE001
            pass
        # 2-urinish: tizim pleyeri
        import platform
        import subprocess

        system = platform.system()
        try:
            if system == "Darwin":
                subprocess.run(["afplay", path], check=False)
            elif system == "Windows":
                os.startfile(path)  # type: ignore[attr-defined]  # noqa: S606
            else:
                for player in ("mpg123", "ffplay", "aplay"):
                    if subprocess.run(["which", player], capture_output=True).returncode == 0:
                        extra = ["-nodisp", "-autoexit"] if player == "ffplay" else []
                        subprocess.run([player, *extra, path], check=False)
                        break
        except Exception:  # noqa: BLE001
            pass
