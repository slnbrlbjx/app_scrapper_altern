"use client"
import { useState, useEffect, useCallback } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const SOURCE_LABELS: Record<string, string> = {
  linkedin: "LinkedIn",
  linkedin_posts: "LinkedIn Posts",
  welcometothejungle: "WTTJ",
  hellowork: "Hellowork",
  apec: "APEC",
  indeed: "Indeed",
  lesjeudis: "LesJeudis",
  france_travail: "France Travail",
  reddit: "Reddit",
  twitter: "X / Twitter",
  discord: "Discord",
  telegram: "Telegram",
  companies: "Entreprises",
}

const SOURCE_COLORS: Record<string, string> = {
  linkedin: "bg-blue-100 text-blue-800",
  linkedin_posts: "bg-blue-50 text-blue-600",
  welcometothejungle: "bg-green-100 text-green-800",
  hellowork: "bg-orange-100 text-orange-800",
  apec: "bg-purple-100 text-purple-800",
  indeed: "bg-indigo-100 text-indigo-800",
  lesjeudis: "bg-pink-100 text-pink-800",
  france_travail: "bg-red-100 text-red-800",
  reddit: "bg-orange-200 text-orange-900",
  twitter: "bg-sky-100 text-sky-800",
  discord: "bg-violet-100 text-violet-800",
  telegram: "bg-cyan-100 text-cyan-800",
  companies: "bg-gray-100 text-gray-800",
}

interface Job {
  id: number
  title: string
  company: string
  city?: string
  source: string
  url: string
  contract_type?: string
  salary?: string
  remote_type?: string
  description?: string
  created_at: string
}

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [total, setTotal] = useState(0)
  const [sources, setSources] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [activeSource, setActiveSource] = useState("")
  const [page, setPage] = useState(0)
  const [error, setError] = useState("")

  const PER_PAGE = 30

  const fetchJobs = useCallback(async () => {
    setLoading(true)
    setError("")
    try {
      const params = new URLSearchParams({
        limit: String(PER_PAGE),
        offset: String(page * PER_PAGE),
      })
      if (search) params.set("keyword", search)
      if (activeSource) params.set("source", activeSource)
      const r = await fetch(`${API_URL}/api/jobs?${params}`)
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const data = await r.json()
      setJobs(data.jobs || [])
      setTotal(data.total || 0)
    } catch (e: any) {
      setError("Impossible de charger les offres. Le backend est-il démarré ?")
    } finally {
      setLoading(false)
    }
  }, [search, activeSource, page])

  const fetchSources = async () => {
    try {
      const r = await fetch(`${API_URL}/api/sources`)
      if (r.ok) setSources(await r.json())
    } catch {}
  }

  useEffect(() => { fetchSources() }, [])
  useEffect(() => { setPage(0) }, [search, activeSource])
  useEffect(() => { fetchJobs() }, [fetchJobs])

  const totalPages = Math.ceil(total / PER_PAGE)

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900 px-6 py-5">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">
              🔐 Alternance Cyber
            </h1>
            <p className="text-gray-400 text-sm mt-0.5">
              {total} offres agrégées depuis {sources.length} sources
            </p>
          </div>
          <button
            onClick={fetchJobs}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-medium transition"
          >
            ↻ Rafraîchir
          </button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-6 space-y-6">
        {/* Search */}
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Rechercher (titre, entreprise, description…)"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Source filters */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveSource("")}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
              !activeSource ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            Toutes
          </button>
          {sources.map(s => (
            <button
              key={s}
              onClick={() => setActiveSource(s === activeSource ? "" : s)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
                s === activeSource
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700"
              }`}
            >
              {SOURCE_LABELS[s] || s}
            </button>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-lg px-4 py-3 text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Jobs grid */}
        {loading ? (
          <div className="grid gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-24 bg-gray-800 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-20 text-gray-500">
            Aucune offre trouvée.
          </div>
        ) : (
          <div className="grid gap-3">
            {jobs.map(job => (
              <a
                key={job.id}
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-gray-800 hover:bg-gray-750 border border-gray-700 hover:border-indigo-600 rounded-xl p-4 transition group"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${SOURCE_COLORS[job.source] || "bg-gray-700 text-gray-300"}`}>
                        {SOURCE_LABELS[job.source] || job.source}
                      </span>
                      {job.contract_type && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-700 text-gray-300">
                          {job.contract_type}
                        </span>
                      )}
                    </div>
                    <h2 className="font-semibold text-white group-hover:text-indigo-300 transition truncate">
                      {job.title}
                    </h2>
                    <p className="text-gray-400 text-sm mt-0.5">
                      {[job.company, job.city].filter(Boolean).join(" · ")}
                    </p>
                    {job.salary && (
                      <p className="text-green-400 text-xs mt-1">{job.salary}</p>
                    )}
                  </div>
                  <span className="text-gray-600 group-hover:text-indigo-400 text-xl flex-shrink-0 mt-1">→</span>
                </div>
              </a>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-4 py-2 bg-gray-800 rounded-lg text-sm disabled:opacity-40 hover:bg-gray-700 transition"
            >
              ← Précédent
            </button>
            <span className="text-gray-400 text-sm px-2">
              Page {page + 1} / {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="px-4 py-2 bg-gray-800 rounded-lg text-sm disabled:opacity-40 hover:bg-gray-700 transition"
            >
              Suivant →
            </button>
          </div>
        )}
      </div>
    </main>
  )
}
