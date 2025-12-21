# Podcast Summary Viewer

A lightweight React + Vite UI for browsing podcast transcripts and comparing summaries from different models. Tailwind CSS and Lucide provide styling and icons; summaries support markdown via `react-markdown`.

## Quick start

```bash
npm install
npm run dev
```

## Data shape

Edit `src/data/podcasts.json` to add episodes. The app expects an object keyed by a stable id:

```json
{
  "episode-id": {
    "title": "Episode title",
    "host": "Host name",
    "date": "2024-01-01",
    "duration": "55m",
    "tags": ["tag a", "tag b"],
    "summaries": {
      "GPT-3.5": "model summary text or markdown",
      "Llama3-8B": "model summary text or markdown",
      "Llama3-8B (Fine-tuned)": "model summary text or markdown"
    },
    "transcript": "Full transcript text"
  }
}
```

Restart the dev server after changing the JSON file to ensure the import picks up the latest content.
