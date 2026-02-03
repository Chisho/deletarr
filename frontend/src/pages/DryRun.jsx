import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
import { Play, Activity, AlertTriangle, ShieldCheck, ChevronDown, ChevronRight, Clapperboard, Tv, Zap, Trash2 } from 'lucide-react'

export default function DryRun() {
    const [config, setConfig] = useState(null)
    const [configLoading, setConfigLoading] = useState(true)
    const [loading, setLoading] = useState(false)
    const [results, setResults] = useState(null)
    const [error, setError] = useState(null)
    const [expandedServices, setExpandedServices] = useState({ Radarr: false, Sonarr: false })

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const res = await fetch('/api/config')
                const data = await res.json()
                setConfig(data)
            } catch (err) {
                console.error("Error fetching config:", err)
            } finally {
                setConfigLoading(false)
            }
        }
        fetchConfig()
    }, [])

    const toggleService = (service) => {
        setExpandedServices(prev => ({ ...prev, [service]: !prev[service] }))
    }

    const handleRun = async (forceReal = false) => {
        const isDryRun = forceReal ? false : true
        setLoading(true)
        if (!forceReal) setResults(null) // Only clear results when starting a new simulation
        setError(null)
        setExpandedServices({ Radarr: false, Sonarr: false })

        if (forceReal) {
            if (!confirm("Are you sure you want to PERMANENTLY delete these items? This action cannot be undone.")) {
                setLoading(false)
                return
            }
        }

        const endpoint = isDryRun ? '/api/dry-run' : '/api/run'
        try {
            const options = isDryRun ? { method: 'GET' } : { method: 'POST' }
            const res = await fetch(endpoint, options)
            if (!res.ok) throw new Error(`Request failed: ${res.statusText}`)
            const data = await res.json()
            if (data.success === false) throw new Error(data.error || "Unknown error occurred")
            setResults(data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const renderServiceCol = (serviceName, list, icon) => {
        const Icon = icon;
        const sortedList = list ? [...list].sort((a, b) => a.name.localeCompare(b.name)) : []
        const hasItems = sortedList.length > 0

        return (
            <Card className="flex-1 border-border/50 bg-card/30 backdrop-blur-sm overflow-hidden h-fit">
                <CardHeader className="bg-muted/30 pb-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="p-2 bg-primary/10 rounded-lg text-primary">
                                <Icon size={18} />
                            </div>
                            <CardTitle className="text-lg">{serviceName}</CardTitle>
                        </div>
                        <div className="px-2 py-0.5 rounded text-xs font-bold bg-primary/20 text-primary">
                            {sortedList.length} items
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    {!hasItems ? (
                        <div className="p-8 text-center text-muted-foreground text-sm italic">
                            No items to delete for {serviceName}.
                        </div>
                    ) : (
                        <div className="divide-y divide-border/30">
                            {/* Summary section - Showing what will be deleted */}
                            <div className="p-4 space-y-3">
                                <div className="text-xs font-bold text-primary/70 uppercase tracking-widest pl-1">To Be Deleted</div>
                                <div className="space-y-2">
                                    {sortedList.slice(0, 5).map((t) => (
                                        <div key={t.hash} className="flex items-center justify-between text-sm group">
                                            <span className="truncate flex-1 font-medium group-hover:text-primary transition-colors">{t.name}</span>
                                        </div>
                                    ))}
                                    {sortedList.length > 5 && (
                                        <div className="text-xs text-muted-foreground italic pl-1">
                                            ... and {sortedList.length - 5} more
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Expandable Candidates section */}
                            <button
                                onClick={() => toggleService(serviceName)}
                                className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors text-left"
                            >
                                <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Full Candidate List</span>
                                {expandedServices[serviceName] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                            </button>

                            {expandedServices[serviceName] && (
                                <div className="bg-muted/20 max-h-[400px] overflow-y-auto">
                                    {sortedList.map((t) => (
                                        <div key={t.hash} className="px-4 py-3 text-sm flex justify-between items-center border-b border-border/10 last:border-0 hover:bg-muted/30 transition-colors">
                                            <span className="truncate flex-1 font-medium">{t.name}</span>
                                            <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded font-mono text-muted-foreground ml-3 shrink-0">
                                                {t.hash.substring(0, 8)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        )
    }

    if (configLoading) {
        return (
            <div className="h-96 flex items-center justify-center">
                <Activity className="animate-spin text-primary" size={48} />
            </div>
        )
    }

    const isGlobalDryRun = config?.dry_run
    const hasDeletions = results?.deleted_count > 0 || (results?.summary && (results.summary.Sonarr.length > 0 || results.summary.Radarr.length > 0))

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Manual Execution</h1>
                    <p className="text-muted-foreground mt-1">
                        {isGlobalDryRun
                            ? "Review items and trigger a safety-first simulation run."
                            : "Analyze candidates and optionally apply deletions."}
                    </p>
                </div>
            </div>

            <div className="space-y-6">
                {!isGlobalDryRun && (
                    <div className="bg-destructive/15 border-2 border-destructive/30 rounded-2xl p-6 md:p-8 animate-pulse shadow-lg shadow-destructive/5">
                        <div className="flex flex-col md:flex-row items-center gap-6 text-center md:text-left">
                            <div className="p-4 bg-destructive/20 rounded-full text-destructive">
                                <AlertTriangle size={48} strokeWidth={2.5} />
                            </div>
                            <div className="space-y-2">
                                <h2 className="text-2xl md:text-3xl font-black text-destructive uppercase tracking-tight">Dry Run is OFF</h2>
                                <p className="text-destructive font-bold text-lg leading-tight">
                                    You are in Productive Mode. Deletions can be applied after running a simulation and reviewing the results.
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                <Card className={`overflow-hidden border-2 transition-all duration-300 border-primary/20 bg-primary/5`}>
                    <CardContent className="p-8">
                        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <div className="p-2 bg-primary/20 rounded-lg text-primary">
                                        <ShieldCheck size={24} />
                                    </div>
                                    <h3 className="text-xl font-bold tracking-tight">Simulation Mode</h3>
                                </div>
                                <p className="text-muted-foreground">
                                    Safely analyze which torrents meet the deletion criteria without making any changes.
                                </p>
                            </div>

                            <Button
                                onClick={() => handleRun(false)}
                                disabled={loading}
                                size="lg"
                                className={`h-16 px-8 text-xl font-black uppercase tracking-wider shadow-xl transition-all hover:scale-[1.02] active:scale-[0.98]`}
                            >
                                {loading && !results ? (
                                    <Activity className="animate-spin mr-3" size={24} />
                                ) : (
                                    <Play className="mr-3" size={24} fill="currentColor" />
                                )}
                                {loading && !results ? 'Processing...' : 'Start Simulation'}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {error && (
                <div className="p-4 rounded-xl border border-destructive/50 bg-destructive/10 text-destructive text-sm font-medium flex items-center gap-3">
                    <AlertTriangle size={20} />
                    <span>Error: {error}</span>
                </div>
            )}

            {results && (
                <div className="space-y-6 animate-in slide-in-from-bottom-5 duration-500">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pl-1">
                        <div className="flex items-center gap-3">
                            {results.dry_run ? (
                                <div className="flex items-center gap-2 text-primary font-bold tracking-tight">
                                    <Activity size={24} />
                                    <span className="text-2xl uppercase">Simulation Results</span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2 text-green-500 font-bold tracking-tight">
                                    <ShieldCheck size={24} />
                                    <span className="text-2xl uppercase">Execution Results</span>
                                </div>
                            )}
                            <span className="text-muted-foreground text-sm mt-1">•</span>
                            <span className="text-muted-foreground text-sm mt-1">
                                {results.dry_run ? 'No changes made' : `Deleted ${results.deleted_count} items`}
                            </span>
                        </div>

                        {!isGlobalDryRun && results.dry_run && hasDeletions && (
                            <Button
                                onClick={() => handleRun(true)}
                                disabled={loading}
                                variant="destructive"
                                size="lg"
                                className="h-12 px-6 font-bold uppercase tracking-tighter shadow-lg shadow-destructive/20 animate-in zoom-in duration-300"
                            >
                                {loading ? (
                                    <Activity className="animate-spin mr-2" size={18} />
                                ) : (
                                    <Trash2 className="mr-2" size={18} />
                                )}
                                Apply Deletions Now
                            </Button>
                        )}
                    </div>

                    <div className="flex flex-col lg:flex-row gap-6">
                        {renderServiceCol('Sonarr', results.summary.Sonarr, Tv)}
                        {renderServiceCol('Radarr', results.summary.Radarr, Clapperboard)}
                    </div>
                </div>
            )}
        </div>
    )
}

