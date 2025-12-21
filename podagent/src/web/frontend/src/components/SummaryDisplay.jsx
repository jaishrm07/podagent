import { BookOpenText, Clock3, MessageCircle, Quote, Tag, UserRound } from "lucide-react"
import ReactMarkdown from "react-markdown"

const SummaryDisplay = ({ podcast, summary, model, renderKey }) => {
  if (!podcast) {
    return (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white/60 p-10 text-center text-gray-500">
        Select a podcast to view its summaries.
      </div>
    )
  }

  const isRichObject = summary && typeof summary === "object"
  const abstract = isRichObject ? summary.abstract || "" : summary || ""
  const outline = isRichObject ? summary.outline || [] : []
  const quotes = isRichObject ? summary.quotes || [] : []
  const qAndA = isRichObject
    ? Array.isArray(summary.q_and_a)
      ? summary.q_and_a
      : []
    : []
  const rawKeywords = isRichObject && Array.isArray(summary.keywords) ? summary.keywords : []
  const keywords = Array.from(new Set(rawKeywords.filter(Boolean))).slice(0, 7)

  return (
    <div
      key={renderKey}
      className="glass animate-fadeIn rounded-2xl border border-gray-200 bg-white/90 p-8 shadow-panel"
    >
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-gray-500">Summary</p>
          <h2 className="font-display text-2xl text-ink">{podcast.title}</h2>
        </div>
        <span className="inline-flex items-center gap-2 rounded-full border border-ink/15 bg-ink/10 px-3 py-1 text-xs font-semibold text-ink">
          <BookOpenText className="h-4 w-4" />
          {model || "Select a model"}
        </span>
      </div>

      <div className="mt-4 space-y-3 text-lg leading-relaxed text-gray-800">
        {abstract ? (
          <div className="leading-relaxed text-gray-800">
            <ReactMarkdown
              components={{
                p: (props) => <p className="leading-relaxed text-gray-800" {...props} />,
                ul: (props) => <ul className="list-disc space-y-2 pl-5" {...props} />,
                ol: (props) => <ol className="list-decimal space-y-2 pl-5" {...props} />,
                li: (props) => <li className="leading-relaxed text-gray-800" {...props} />,
                strong: (props) => <strong className="font-semibold text-ink" {...props} />,
              }}
            >
              {abstract}
            </ReactMarkdown>
          </div>
        ) : (
          <p className="text-gray-500">Pick a model to see its summary.</p>
        )}
      </div>

      {outline?.length ? (
        <div className="mt-6">
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Outline</h3>
          <ul className="mt-2 list-disc space-y-2 pl-5 text-sm leading-relaxed text-gray-800">
            {outline.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {quotes?.length ? (
        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Quotes</h3>
          {quotes.map((quote, idx) => {
            const text = typeof quote === "string" ? quote : quote.text
            const ts = typeof quote === "string" ? "" : quote.timestamp
            if (!text) return null
            return (
              <div key={`${text}-${idx}`} className="rounded-xl border border-gray-100 bg-gray-50/70 px-4 py-3 text-sm">
                <div className="flex items-start gap-2">
                  <Quote className="mt-0.5 h-4 w-4 text-accent" />
                  <div>
                    <p className="text-gray-800">{text}</p>
                    {ts ? <p className="mt-1 text-xs text-gray-500">{ts}</p> : null}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      ) : null}

      {qAndA?.length ? (
        <div className="mt-6 space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Q&A</h3>
          {qAndA.map((qa, idx) => (
            <div key={`${qa.question}-${idx}`} className="rounded-xl border border-gray-100 bg-gray-50/70 px-4 py-3 text-sm">
              <p className="font-semibold text-ink">{qa.question}</p>
              <div className="mt-1 leading-relaxed text-gray-800">
                <ReactMarkdown>{qa.answer || ""}</ReactMarkdown>
              </div>
              {(() => {
                const evidenceList = Array.isArray(qa.evidence)
                  ? qa.evidence
                  : qa.evidence
                    ? [qa.evidence]
                    : []
                return evidenceList.length ? (
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-gray-600">
                    {evidenceList.map((ev, evIdx) => {
                      const text = typeof ev === "string" ? ev : ev?.text ?? ""
                      const ts = typeof ev === "string" ? "" : ev?.timestamp
                      if (!text) return null
                      return (
                        <li key={`${text}-${evIdx}`}>
                          {text} {ts ? <span className="text-gray-500">({ts})</span> : null}
                        </li>
                      )
                    })}
                  </ul>
                ) : null
              })()}
            </div>
          ))}
        </div>
      ) : null}

      {keywords?.length ? (
        <div className="mt-6">
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-500">Keywords</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {keywords.map((kw) => (
              <span key={kw} className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700">
                <Tag className="h-4 w-4 text-accent" />
                {kw}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      <div className="mt-8 flex flex-wrap items-center gap-3 text-sm text-gray-600">
        <span className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1">
          <UserRound className="h-4 w-4 text-accent" />
          {podcast.host}
        </span>
        <span className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1">
          <Clock3 className="h-4 w-4 text-accent" />
          {podcast.duration}
        </span>
        {!isRichObject &&
          podcast.tags?.map((tag) => (
            <span key={tag} className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1">
              <Tag className="h-4 w-4 text-accent" />
              {tag}
            </span>
          ))}
      </div>
    </div>
  )
}

export default SummaryDisplay
