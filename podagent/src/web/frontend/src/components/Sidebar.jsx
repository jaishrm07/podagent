import { Headphones, PlayCircle } from "lucide-react"

const Sidebar = ({ podcasts, selectedId, onSelect }) => {
  const entries = Object.entries(podcasts || {})

  return (
    <aside className="glass w-72 shrink-0 border-r border-gray-200 bg-white/90">
      <div className="border-b border-gray-200 px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-ink text-white shadow-panel">
            <Headphones className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-[0.28em] text-gray-500">PodAgent</p>
            <p className="font-display text-lg text-ink">Summary Viewer</p>
          </div>
        </div>
      </div>

      <div className="flex max-h-[calc(100vh-82px)] flex-col gap-2 overflow-y-auto p-4">
        {entries.map(([id, podcast]) => {
          const isActive = id === selectedId
          return (
            <button
              key={id}
              onClick={() => onSelect(id)}
              className={`group w-full rounded-xl border px-4 py-3 text-left transition ${
                isActive
                  ? "border-ink bg-accent-soft/60 text-ink shadow-sm"
                  : "border-transparent bg-white/80 hover:border-gray-200 hover:bg-white"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="font-semibold leading-snug text-ink">{podcast.title}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    {podcast.host} • {podcast.duration}
                  </p>
                </div>
                <span
                  className={`flex h-9 w-9 items-center justify-center rounded-full border transition ${
                    isActive
                      ? "border-ink bg-ink text-white"
                      : "border-gray-200 text-gray-500 group-hover:border-gray-400"
                  }`}
                  aria-hidden
                >
                  <PlayCircle className="h-4 w-4" />
                </span>
              </div>
              {podcast.tags?.length ? (
                <div className="mt-2 flex flex-wrap gap-2">
                  {podcast.tags.slice(0, 2).map((tag) => (
                    <span
                      key={tag}
                      className={`rounded-full px-2 py-1 text-[11px] ${
                        isActive ? "bg-white/70 text-ink" : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              ) : null}
            </button>
          )
        })}
        {entries.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-200 bg-white/70 px-4 py-6 text-center text-sm text-gray-500">
            No podcasts available yet.
          </div>
        ) : null}
      </div>
    </aside>
  )
}

export default Sidebar
