import { useEffect, useMemo, useState } from "react"
import ModelSelector from "./components/ModelSelector"
import Sidebar from "./components/Sidebar"
import SummaryDisplay from "./components/SummaryDisplay"
import TranscriptExpander from "./components/TranscriptExpander"
import podcastData from "./data/podcastsCombined"

function App() {
  const [podcasts, setPodcasts] = useState({})
  const [selectedPodId, setSelectedPodId] = useState("")
  const [selectedModel, setSelectedModel] = useState("")
  const [showTranscript, setShowTranscript] = useState(false)

  useEffect(() => {
    setPodcasts(podcastData)
    const first = Object.keys(podcastData)[0]
    if (first) {
      setSelectedPodId(first)
    }
  }, [])

  const currentPodcast = useMemo(
    () => (selectedPodId ? podcasts[selectedPodId] : null),
    [podcasts, selectedPodId],
  )

  const availableModels = useMemo(
    () => (currentPodcast ? Object.keys(currentPodcast.summaries || {}) : []),
    [currentPodcast],
  )

  useEffect(() => {
    if (!currentPodcast) return
    if (!availableModels.length) {
      setSelectedModel("")
      return
    }
    if (!availableModels.includes(selectedModel)) {
      setSelectedModel(availableModels[0])
    }
  }, [availableModels, currentPodcast, selectedModel])

  const summary = currentPodcast?.summaries?.[selectedModel] ?? null

  useEffect(() => {
    setShowTranscript(false)
  }, [selectedPodId, selectedModel])

  const pageTitle = currentPodcast?.title ?? "Select a podcast"

  return (
    <div className="flex min-h-screen">
      <Sidebar podcasts={podcasts} selectedId={selectedPodId} onSelect={setSelectedPodId} />

      <main className="flex-1 space-y-6 px-8 py-10 sm:px-12">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-gray-500">Podcast</p>
            <h1 className="font-display text-3xl text-ink">{pageTitle}</h1>
            <p className="text-gray-600">
              Toggle models to compare summaries. Reveal the transcript to read the raw source.
            </p>
          </div>
          {currentPodcast ? (
            <div className="flex flex-wrap gap-2 text-sm text-gray-600">
              <span className="rounded-full bg-white/80 px-3 py-1">Date: {currentPodcast.date}</span>
              <span className="rounded-full bg-white/80 px-3 py-1">Duration: {currentPodcast.duration}</span>
            </div>
          ) : null}
        </header>

        <ModelSelector models={availableModels} selectedModel={selectedModel} onSelectModel={setSelectedModel} />

        <SummaryDisplay
          podcast={currentPodcast}
          summary={summary}
          model={selectedModel}
          renderKey={`${selectedPodId}-${selectedModel}`}
        />

        <TranscriptExpander
          open={showTranscript}
          onToggle={() => setShowTranscript((prev) => !prev)}
          transcript={currentPodcast?.transcript ?? ""}
        />
      </main>
    </div>
  )
}

export default App
