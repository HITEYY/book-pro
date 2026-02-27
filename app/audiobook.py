import json
import logging
import re
import wave
from pathlib import Path
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field

from app.schemas import AudioScriptLine, AudioScriptPayload, ChapterSummary

logger = logging.getLogger("uvicorn.error")


class _AudioScriptEnvelope(BaseModel):
    title: str
    lines: list[AudioScriptLine] = Field(default_factory=list)


def _safe_name(name: str, fallback: str) -> str:
    safe = re.sub(r"[^\w\-.가-힣 ]+", "-", name or "").strip(" .-")
    return safe or fallback


def _json_object(raw: str) -> dict[str, Any]:
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("오디오북 대본 응답이 비어 있습니다.")

    try:
        loaded = json.loads(raw)
        if isinstance(loaded, dict):
            return loaded
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end > start:
        return json.loads(raw[start : end + 1])

    raise ValueError("오디오북 대본 JSON 파싱에 실패했습니다.")


class AudiobookGenerator:
    def __init__(
        self,
        *,
        llm_client: OpenAI,
        llm_model: str,
        tts_client: OpenAI,
        tts_model: str,
    ) -> None:
        self.llm_client = llm_client
        self.llm_model = llm_model
        self.tts_client = tts_client
        self.tts_model = tts_model

    def generate_script(
        self,
        *,
        book_title: str,
        chapter_summaries: list[ChapterSummary],
        character_summaries_text: str,
        language: str,
        target_minutes: int,
    ) -> AudioScriptPayload:
        compact_chapters = [
            {
                "chapter_index": ch.chapter_index,
                "chapter_title": ch.chapter_title,
                "summary": ch.summary,
                "key_events": ch.key_events,
            }
            for ch in chapter_summaries
        ]
        prompt = (
            "아래 소설 요약을 오디오북 대본으로 변환하라. 반드시 JSON 객체만 응답하라.\\n"
            "스키마: {title:string, lines:[{speaker:string, text:string}]}\\n"
            "규칙:\\n"
            f"- language는 {language}\\n"
            f"- target_minutes={target_minutes} 분 분량\\n"
            "- line은 20~120자 내외로 끊고, speaker는 narrator 또는 캐릭터 이름\\n"
            "- lines는 최소 30개 이상\\n"
            "- 설명 문장 금지, JSON 이외 텍스트 금지\\n\\n"
            f"book_title: {book_title}\\n"
            f"chapters: {json.dumps(compact_chapters, ensure_ascii=False)}\\n"
            f"characters: {character_summaries_text}"
        )

        res = self.llm_client.responses.create(
            model=self.llm_model,
            input=prompt,
            temperature=0.7,
        )
        raw = getattr(res, "output_text", "")
        payload = _AudioScriptEnvelope.model_validate(_json_object(raw))
        lines = [line for line in payload.lines if line.text.strip()]
        if not lines:
            raise ValueError("생성된 대본의 line이 비어 있습니다.")
        return AudioScriptPayload(title=payload.title or book_title, lines=lines)

    def synthesize(
        self,
        *,
        script: AudioScriptPayload,
        out_dir: Path,
        narrator_voice: str,
        character_voices: dict[str, str],
    ) -> tuple[Path, Path, Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        script_path = out_dir / "script.json"
        script_path.write_text(script.model_dump_json(indent=2), encoding="utf-8")

        seg_dir = out_dir / "segments"
        seg_dir.mkdir(parents=True, exist_ok=True)

        segment_paths: list[Path] = []
        for idx, line in enumerate(script.lines, start=1):
            speaker = (line.speaker or "narrator").strip()
            voice = character_voices.get(speaker, narrator_voice)
            seg_path = seg_dir / f"{idx:04d}-{_safe_name(speaker, 'narrator')}.wav"
            with self.tts_client.audio.speech.with_streaming_response.create(
                model=self.tts_model,
                voice=voice,
                input=line.text,
                response_format="wav",
            ) as response:
                response.stream_to_file(seg_path)
            segment_paths.append(seg_path)

        final_audio = out_dir / "audiobook.wav"
        self._merge_wav(segment_paths, final_audio)
        return script_path, seg_dir, final_audio

    @staticmethod
    def _merge_wav(parts: list[Path], destination: Path) -> None:
        if not parts:
            raise ValueError("병합할 오디오 세그먼트가 없습니다.")

        with wave.open(str(parts[0]), "rb") as first:
            params = first.getparams()
            frames = [first.readframes(first.getnframes())]

        for part in parts[1:]:
            with wave.open(str(part), "rb") as current:
                if current.getparams()[:3] != params[:3]:
                    raise ValueError("오디오 파라미터가 서로 달라 WAV 병합이 불가능합니다.")
                frames.append(current.readframes(current.getnframes()))

        with wave.open(str(destination), "wb") as out:
            out.setparams(params)
            for frame in frames:
                out.writeframes(frame)

        logger.info("[오디오북 생성 완료] path='%s'", destination)
