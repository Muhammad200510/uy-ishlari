"""Ovoz: nutqni matnga (STT) va matnni nutqqa (TTS).

Ikki backend qo'llab-quvvatlanadi:
  1. Termux (Android) — termux-api orqali (termux-speech-to-text / termux-tts-speak)
  2. Desktop (Linux/macOS/Windows) — SpeechRecognition + gTTS

Kerakli vositalar bo'lmasa, dastur matnli rejimga tushadi va xatolik bermaydi.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile


def is_termux() -> bool:
    """Dastur Android/Termux ichida ishlayaptimi?"""
    prefix = os.environ.get("PREFIX", "")
    if "com.termux" in prefix:
        return True
    return shutil.which("termux-tts-speak") is not None


class BaseVoice:
    available = False

    def listen(self) -> str | None:  # pragma: no cover - interfeys
        return None

    def speak(self, text: str) -> None:  # pragma: no cover - interfeys
        pass


class TermuxVoice(BaseVoice):
    """Android/Termux uchun ovoz (termux-api kerak)."""

    def __init__(self, stt_language: str = "uz-UZ", tts_language: str = "uz"):
        self.stt_language = stt_language
        self.tts_language = tts_language
        self._stt = shutil.which("termux-speech-to-text")
        self._tts = shutil.which("termux-tts-speak")
        self._media = shutil.which("termux-media-player")
        self.available = self._stt is not None or self._tts is not None
        if not self.available:
            print(
                "[ovoz] termux-api topilmadi. O'rnatish: pkg install termux-api "
                "va 'Termux:API' ilovasini Play Store/F-Droid'dan o'rnating."
            )

    def listen(self) -> str | None:
        if not self._stt:
            return None
        try:
            print("🎙️  Eshityapman... (gapiring)")
            proc = subprocess.run(
                [self._stt], capture_output=True, text=True, timeout=30
            )
            text = (proc.stdout or "").strip()
            return text or None
        except subprocess.TimeoutExpired:
            return None
        except Exception as exc:  # noqa: BLE001
            print(f"[ovoz] Eshitishda xato: {exc}")
            return None

    def speak(self, text: str) -> None:
        if not text:
            return
        # 1-urinish: qurilmaning o'zbekcha TTS dvigatelidan foydalanish
        if self._tts:
            try:
                lang = (self.tts_language or "uz").split("-")[0]
                subprocess.run([self._tts, "-l", lang, text], check=False, timeout=60)
                return
            except Exception:  # noqa: BLE001
                pass
        # 2-urinish: gTTS + termux-media-player
        _gtts_fallback(text, self.tts_language, self._media)


class DesktopVoice(BaseVoice):
    """Linux/macOS/Windows uchun ovoz (SpeechRecognition + gTTS)."""

    def __init__(self, stt_language: str = "uz-UZ", tts_language: str = "uz"):
        self.stt_language = stt_language
        self.tts_language = tts_language
        self._recognizer = None
        self._mic = None
        self._sr = None
        self.available = self._try_init()

    def _try_init(self) -> bool:
        try:
            import speech_recognition as sr

            self._sr = sr
            self._recognizer = sr.Recognizer()
            self._mic = sr.Microphone()
            return True
        except Exception as exc:  # noqa: BLE001
            print(f"[ovoz] Mikrofon/STT mavjud emas ({exc}). Matnli rejim ishlatiladi.")
            return False

    def listen(self) -> str | None:
        if not self.available:
            return None
        try:
            with self._mic as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                print("🎙️  Eshityapman... (gapiring)")
                audio = self._recognizer.listen(source, timeout=8, phrase_time_limit=15)
            return self._recognizer.recognize_google(audio, language=self.stt_language)
        except self._sr.WaitTimeoutError:
            return None
        except self._sr.UnknownValueError:
            print("[ovoz] Tushunolmadim, qaytaring.")
            return None
        except Exception as exc:  # noqa: BLE001
            print(f"[ovoz] Eshitishda xato: {exc}")
            return None

    def speak(self, text: str) -> None:
        if not text:
            return
        _gtts_fallback(text, self.tts_language, None)


def _gtts_fallback(text: str, tts_language: str, media_player: str | None) -> None:
    """gTTS bilan mp3 yasab, imkoniyatga qarab ijro etadi."""
    try:
        from gtts import gTTS

        lang = (tts_language or "uz").split("-")[0]
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
            path = fp.name
        tts.save(path)
        _play_file(path, media_player)
        try:
            os.remove(path)
        except OSError:
            pass
    except Exception as exc:  # noqa: BLE001
        print(f"[ovoz] Ovozli o'qish imkoni bo'lmadi ({exc}).")


def _play_file(path: str, media_player: str | None) -> None:
    import platform

    # Termux media player
    if media_player:
        try:
            subprocess.run([media_player, "play", path], check=False, timeout=60)
            return
        except Exception:  # noqa: BLE001
            pass
    # playsound
    try:
        from playsound import playsound

        playsound(path)
        return
    except Exception:  # noqa: BLE001
        pass
    # Tizim pleyeri
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["afplay", path], check=False)
        elif system == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]  # noqa: S606
        else:
            for player in ("mpg123", "ffplay", "aplay"):
                if shutil.which(player):
                    extra = ["-nodisp", "-autoexit"] if player == "ffplay" else []
                    subprocess.run([player, *extra, path], check=False)
                    break
    except Exception:  # noqa: BLE001
        pass


def make_voice(stt_language: str = "uz-UZ", tts_language: str = "uz") -> BaseVoice:
    """Platformaga mos ovoz backendini tanlaydi."""
    if is_termux():
        return TermuxVoice(stt_language, tts_language)
    return DesktopVoice(stt_language, tts_language)


# Orqaga moslik uchun eski nom
def VoiceIO(stt_language: str = "uz-UZ", tts_language: str = "uz") -> BaseVoice:  # noqa: N802
    return make_voice(stt_language, tts_language)
