from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from podagent import config
from podagent.models import OpenAISummarizer, PodcastSummarizer
from podagent.retriever import build_index_from_chunks
from podagent.utils import read_jsonl


app = FastAPI(title="PodAgent API", version="0.1.0")

# Allow local frontend/dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummarizeRequest(BaseModel):
    episode_id: str
    query: Optional[str] = None
    use_transformer: bool = False
    use_openai: bool = True
    use_extractive: bool = False
    model_name: Optional[str] = None
    context_chunks: int = 8
    hierarchical: bool = False
    group_size: int = 8
    structured: bool = False


@app.on_event("startup")
def _startup() -> None:
    # Ensure directories exist at startup
    config.ensure_directories()


@app.post("/summarize")
def summarize(req: SummarizeRequest):
    # Load chunks
    chunk_path = config.INTERIM_DIR / f"{req.episode_id}.jsonl"
    if not chunk_path.exists():
        raise HTTPException(status_code=404, detail="Episode chunks not found. Run ingest first.")

    retriever = None
    if req.query:
        try:
            retriever = build_index_from_chunks()
        except Exception:
            retriever = None

    if req.use_transformer or req.use_extractive or not req.use_openai:
        raise HTTPException(status_code=400, detail="Only OpenAI gpt-4o summarization is supported.")
    try:
        summarizer = OpenAISummarizer(model=req.model_name or "gpt-4o")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenAI summarizer failed: {exc}")

    agent = PodcastSummarizer(
        summarizer=summarizer,
        retriever=retriever,
        max_context_chunks=max(1, req.context_chunks),
    )
    result = agent.summarize_episode(
        req.episode_id,
        query=req.query,
        hierarchical=req.hierarchical,
        group_size=req.group_size,
        structured=req.structured,
    )
    return {
        "episode_id": result.episode_id,
        "abstract": result.abstract,
        "outline": result.outline,
        "quotes": result.quotes,
        "q_and_a": result.q_and_a,
        "keywords": result.keywords,
        "evidence": [
            {"chunk": r.chunk, "score": r.score} for r in (result.evidence or [])
        ],
    }


@app.get("/episodes")
def list_episodes():
    manifest_path = config.INTERIM_DIR / "manifest.jsonl"
    manifest = read_jsonl(manifest_path)
    return {"episodes": manifest}
