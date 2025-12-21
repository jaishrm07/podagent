import { Sparkles } from "lucide-react"

const ModelSelector = ({ models, selectedModel, onSelectModel }) => {
  if (!models?.length) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white/80 px-4 py-3 shadow-sm text-sm text-gray-600">
        No models available for this podcast.
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white/80 px-4 py-3 shadow-sm">
      <div className="mb-3 flex items-center gap-2 text-sm font-medium text-gray-700">
        <Sparkles className="h-4 w-4 text-accent" />
        <span>Model output</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {models.map((model) => {
          const active = model === selectedModel
          return (
            <button
              key={model}
              onClick={() => onSelectModel(model)}
              className={`rounded-full border px-4 py-2 text-sm transition ${
                active
                  ? "border-ink bg-ink text-white shadow-sm"
                  : "border-gray-200 bg-white text-gray-700 hover:border-ink/50 hover:text-ink"
              }`}
            >
              {model}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default ModelSelector
