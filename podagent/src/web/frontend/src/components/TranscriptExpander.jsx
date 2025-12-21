import { ChevronDown, ChevronUp, FileText } from "lucide-react"

const TranscriptExpander = ({ open, onToggle, transcript }) => {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white/80 p-4 shadow-sm">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-3 rounded-xl bg-gray-50 px-4 py-3 text-left text-sm font-semibold text-ink transition hover:bg-gray-100"
      >
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-accent" />
          <span>{open ? "Hide full transcript" : "Show full transcript"}</span>
        </div>
        {open ? <ChevronUp className="h-4 w-4 text-gray-500" /> : <ChevronDown className="h-4 w-4 text-gray-500" />}
      </button>

      {open ? (
        <div className="glass mt-3 max-h-[420px] overflow-y-auto rounded-xl border border-gray-100 bg-white/90 p-4 text-sm leading-relaxed text-gray-800 animate-fadeIn whitespace-pre-line">
          {transcript}
        </div>
      ) : null}
    </div>
  )
}

export default TranscriptExpander
