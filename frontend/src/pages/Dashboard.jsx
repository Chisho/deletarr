import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { RefreshCw, CheckCircle, AlertTriangle, AlertOctagon, Server, Activity, ArrowRight, Settings as SettingsIcon } from 'lucide-react'

export default function Dashboard({ setActivePage }) {
    const [status, setStatus] = useState(null)
    const [config, setConfig] = useState(null)
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        setLoading(true)
        try {
            const [healthRes, configRes] = await Promise.all([
                fetch('/api/health'),
                fetch('/api/config')
            ])
            const healthData = await healthRes.json()
            const configData = await configRes.json()
            setStatus(healthData)
            setConfig(configData)
        } catch (error) {
            console.error("Error fetching dashboard data:", error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    if (loading && !status) {
        return <div className="p-8 text-muted-foreground">Loading dashboard...</div>
    }

    const ServiceInfo = ({ name, icon: Icon, enabled, url }) => (
        <button
            onClick={() => setActivePage('settings')}
            className="w-full text-left p-5 border border-border/60 bg-card/30 rounded-2xl flex items-center justify-between group hover:border-primary/50 hover:bg-primary/5 transition-all duration-300 shadow-sm hover:shadow-md"
        >
            <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${enabled ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'} group-hover:scale-110 transition-transform`}>
                    <Icon size={22} />
                </div>
                <div className="space-y-0.5">
                    <h4 className="text-base font-bold tracking-tight">{name}</h4>
                    <p className="text-sm text-muted-foreground font-mono break-all">{enabled ? url : 'Service Disabled'}</p>
                </div>
            </div>
            <div className="flex items-center gap-3 pl-4">
                <span className={`text-[11px] font-black uppercase tracking-[0.2em] ${enabled ? 'text-green-500' : 'text-muted-foreground/60'}`}>
                    {enabled ? 'Active' : 'Off'}
                </span>
                <div className="p-2 rounded-full bg-primary/0 group-hover:bg-primary/10 transition-colors">
                    <ArrowRight size={18} className="text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
            </div>
        </button>
    )

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight">Dashboard</h1>
                    <p className="text-muted-foreground text-lg">System health and real-time connectivity.</p>
                </div>
                <div className="flex items-center gap-3">
                    <Button variant="outline" size="lg" onClick={fetchData} className="shadow-sm border-border/60">
                        <RefreshCw size={18} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                </div>
            </div>

            {status?.env === 'local' && (
                <div className="p-5 border-2 border-destructive/50 bg-destructive/5 rounded-2xl flex items-start gap-5 animate-in slide-in-from-top duration-500">
                    <div className="p-3 bg-destructive/10 rounded-full text-destructive shadow-sm">
                        <AlertOctagon size={28} />
                    </div>
                    <div className="space-y-1">
                        <h2 className="text-xl font-black text-destructive tracking-tight uppercase">Local Development Mode</h2>
                        <p className="text-sm text-destructive-foreground/90 leading-relaxed font-medium">
                            <strong>WARNING:</strong> Hardlink detection is unreliable on macOS / local mounts.
                            A real run in this environment **will likely cause data loss**.
                        </p>
                    </div>
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-2">
                {/* Status Card */}
                <Card className="border-border/60 bg-card/40 backdrop-blur-md overflow-hidden relative group hover:border-green-500/30 transition-colors">
                    <div className="absolute -top-4 -right-4 p-8 opacity-[0.03] group-hover:opacity-[0.07] transition-opacity">
                        <CheckCircle size={140} />
                    </div>
                    <CardHeader className="pb-3">
                        <CardTitle className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/70">System Status</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-4xl font-black text-green-500 tracking-tighter">Operational</div>
                        <div className="flex items-center gap-2 mt-2">
                            <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                            <p className="text-xs text-muted-foreground font-bold uppercase tracking-wider">
                                Deletarr v{status?.version || '1.3.0'}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                {/* Mode Card */}
                <Card className="border-border/60 bg-card/40 backdrop-blur-md overflow-hidden relative group hover:border-primary/30 transition-colors">
                    <div className="absolute -top-4 -right-4 p-8 opacity-[0.03] group-hover:opacity-[0.07] transition-opacity">
                        <AlertTriangle size={140} />
                    </div>
                    <CardHeader className="pb-3">
                        <CardTitle className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/70">Safety Mode</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className={`text-4xl font-black tracking-tighter ${config?.dry_run ? 'text-primary' : 'text-destructive'}`}>
                            {config?.dry_run ? 'Dry Run' : 'Live Mode'}
                        </div>
                        <p className="text-xs text-muted-foreground font-bold mt-2 uppercase tracking-wider">
                            {config?.dry_run ? 'Simulating deletions only' : 'CAUTION: Deleting real data'}
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Service Connections */}
            <Card className="border-border/60 bg-card/40 backdrop-blur-md shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6">
                    <div>
                        <CardTitle className="text-2xl font-black tracking-tight flex items-center gap-3">
                            <Activity className="text-primary" size={24} />
                            Service Connections
                        </CardTitle>
                        <CardDescription className="text-sm font-medium mt-1">Network endpoints and integration status.</CardDescription>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => setActivePage('settings')} className="text-primary font-bold hover:bg-primary/10">
                        <SettingsIcon size={16} className="mr-2" />
                        Configure
                    </Button>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col gap-4">
                        <ServiceInfo
                            name="Radarr"
                            icon={Server}
                            enabled={config?.Radarr?.enabled}
                            url={status?.Radarr?.status === 'ok' ? config?.Radarr?.url : (config?.Radarr?.url || 'No URL configured')}
                        />
                        <ServiceInfo
                            name="Sonarr"
                            icon={Server}
                            enabled={config?.Sonarr?.enabled}
                            url={status?.Sonarr?.status === 'ok' ? config?.Sonarr?.url : (config?.Sonarr?.url || 'No URL configured')}
                        />
                        <ServiceInfo
                            name="qBittorrent"
                            icon={Activity}
                            enabled={true}
                            url={config?.qBittorrent?.url || 'No URL configured'}
                        />
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
