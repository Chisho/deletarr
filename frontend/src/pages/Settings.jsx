import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select } from '@/components/ui/select'
import { RefreshCw, Settings as SettingsIcon, Server, Map, Activity, Save, RotateCcw, CheckCircle2, AlertCircle } from 'lucide-react'

export default function Settings() {
    const [config, setConfig] = useState(null)
    const [editedConfig, setEditedConfig] = useState(null)
    const [serviceHealth, setServiceHealth] = useState(null)
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [statusMessage, setStatusMessage] = useState(null)

    const fetchData = async () => {
        try {
            const [configRes, healthRes] = await Promise.all([
                fetch('/api/config'),
                fetch('/api/health/services')
            ])
            const configData = await configRes.json()
            const healthData = await healthRes.json()
            setConfig(configData)
            setEditedConfig(JSON.parse(JSON.stringify(configData))) // Deep clone for editing
            setServiceHealth(healthData)
        } catch (error) {
            console.error("Error fetching settings:", error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const handleSave = async () => {
        setSaving(true)
        setStatusMessage(null)
        try {
            const res = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(editedConfig)
            })
            if (res.ok) {
                setConfig(JSON.parse(JSON.stringify(editedConfig)))
                setStatusMessage({ type: 'success', text: 'Settings saved successfully!' })
                // Refresh health after change
                const healthRes = await fetch('/api/health/services')
                setServiceHealth(await healthRes.json())
            } else {
                setStatusMessage({ type: 'error', text: 'Failed to save settings.' })
            }
        } catch (error) {
            setStatusMessage({ type: 'error', text: 'Error saving settings.' })
        } finally {
            setSaving(false)
            setTimeout(() => setStatusMessage(null), 5000)
        }
    }

    const handleReset = () => {
        setEditedConfig(JSON.parse(JSON.stringify(config)))
        setStatusMessage(null)
    }

    const updateField = (path, value) => {
        const newConfig = { ...editedConfig }
        const keys = path.split('.')
        let current = newConfig
        for (let i = 0; i < keys.length - 1; i++) {
            current = current[keys[i]]
        }
        current[keys[keys.length - 1]] = value
        setEditedConfig(newConfig)
    }

    if (loading && !config) {
        return <div className="p-8 text-muted-foreground">Loading configuration...</div>
    }

    const isChanged = JSON.stringify(config) !== JSON.stringify(editedConfig)

    const HealthBadge = ({ service }) => {
        const status = serviceHealth?.[service]
        if (!status) return <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground uppercase tracking-wider font-bold">Checking...</span>

        if (status.status === 'ok') {
            return (
                <div className="flex items-center gap-1.5">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                    <span className="text-[10px] font-bold text-green-500 uppercase tracking-tighter">Connected</span>
                    {status.version && <span className="text-[10px] text-muted-foreground">v{status.version}</span>}
                </div>
            )
        }

        if (status.status === 'disabled') {
            return <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground uppercase tracking-tighter font-bold">Disabled</span>
        }

        return (
            <div className="flex items-center gap-1.5" title={status.message}>
                <span className="inline-flex rounded-full h-2 w-2 bg-destructive"></span>
                <span className="text-[10px] font-bold text-destructive uppercase tracking-tighter">Failed</span>
            </div>
        )
    }

    const SectionHeader = ({ icon: Icon, title, description, service }) => (
        <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
                <div className="p-2 bg-primary/10 rounded-lg text-primary">
                    <Icon size={18} />
                </div>
                <div>
                    <h3 className="text-lg font-semibold tracking-tight">{title}</h3>
                    {description && <p className="text-xs text-muted-foreground">{description}</p>}
                </div>
            </div>
            {service && <HealthBadge service={service} />}
        </div>
    )

    const Field = ({ label, path, type = "text", placeholder, options }) => {
        const keys = path.split('.')
        let value = editedConfig
        for (const key of keys) {
            value = value?.[key]
        }

        const renderInput = () => {
            if (type === "switch") {
                return (
                    <div className="flex items-center h-10">
                        <Switch checked={!!value} onCheckedChange={(val) => updateField(path, val)} />
                    </div>
                )
            }
            if (type === "select") {
                return (
                    <Select
                        value={value || ''}
                        onValueChange={(val) => updateField(path, val)}
                        options={options}
                        className="h-9 bg-background/50"
                    />
                )
            }
            return (
                <Input
                    type={type}
                    value={value || ''}
                    onChange={(e) => updateField(path, type === 'number' ? parseFloat(e.target.value) : e.target.value)}
                    placeholder={placeholder}
                    className="h-9 bg-background/50"
                />
            )
        }

        return (
            <div className="space-y-1.5">
                <Label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</Label>
                {renderInput()}
            </div>
        )
    }

    return (
        <div className="space-y-8 pb-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                    <p className="text-muted-foreground">Manage your connections and deletion rules.</p>
                </div>
                <div className="flex items-center gap-3">
                    {isChanged && (
                        <Button variant="ghost" size="sm" onClick={handleReset} disabled={saving}>
                            <RotateCcw className="mr-2 h-4 w-4" />
                            Reset
                        </Button>
                    )}
                    <Button onClick={handleSave} disabled={!isChanged || saving} className="shadow-lg shadow-primary/20">
                        {saving ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                        {saving ? 'Saving...' : 'Save Changes'}
                    </Button>
                </div>
            </div>

            {statusMessage && (
                <div className={`p-3 rounded-lg flex items-center gap-3 animate-in fade-in slide-in-from-top-2 duration-300 ${statusMessage.type === 'success' ? 'bg-green-500/10 text-green-500 border border-green-500/20' : 'bg-destructive/10 text-destructive border border-destructive/20'
                    }`}>
                    {statusMessage.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                    <span className="text-sm font-medium">{statusMessage.text}</span>
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-2">
                {/* General Settings */}
                <Card className="border-border/60 bg-card/40 backdrop-blur-sm">
                    <CardHeader>
                        <SectionHeader icon={SettingsIcon} title="General" description="Global application behavior" />
                    </CardHeader>
                    <CardContent className="grid grid-cols-2 gap-4">
                        <div className="col-span-2">
                            <Field label="Dry Run Mode" path="dry_run" type="switch" />
                        </div>
                        <Field
                            label="Log Level"
                            path="logging.level"
                            type="select"
                            options={[
                                { label: 'Debug', value: 'DEBUG' },
                                { label: 'Info', value: 'INFO' },
                                { label: 'Warning', value: 'WARNING' },
                                { label: 'Error', value: 'ERROR' }
                            ]}
                        />
                        <Field label="Max Delete %" path="logging.max_delete_percent" type="number" />
                    </CardContent>
                </Card>

                {/* qBittorrent Settings */}
                <Card className="border-border/60 bg-card/40 backdrop-blur-sm">
                    <CardHeader>
                        <SectionHeader icon={Activity} title="qBittorrent" description="Download client connectivity" service="qBittorrent" />
                    </CardHeader>
                    <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="md:col-span-2">
                            <Field label="API URL" path="qBittorrent.url" placeholder="http://ip:port/" />
                        </div>
                        <Field label="Username" path="qBittorrent.username" />
                        <Field label="Password" path="qBittorrent.password" type="password" />
                    </CardContent>
                </Card>

                {/* Radarr Settings */}
                <Card className="border-border/60 bg-card/40 backdrop-blur-sm">
                    <CardHeader>
                        <SectionHeader icon={Server} title="Radarr" description="Movie library integration" service="Radarr" />
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <Field label="Enabled" path="Radarr.enabled" type="switch" />
                            <Field label="Category" path="Radarr.category" />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <Field label="Min Seed Days" path="Radarr.min_seed_days" type="number" />
                            <Field label="API Key" path="Radarr.api_key" type="password" />
                        </div>
                        <Field label="Root Folder" path="Radarr.root_folder" />
                    </CardContent>
                </Card>

                {/* Sonarr Settings */}
                <Card className="border-border/60 bg-card/40 backdrop-blur-sm">
                    <CardHeader>
                        <SectionHeader icon={Server} title="Sonarr" description="TV library integration" service="Sonarr" />
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <Field label="Enabled" path="Sonarr.enabled" type="switch" />
                            <Field label="Category" path="Sonarr.category" />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <Field label="Min Seed Days" path="Sonarr.min_seed_days" type="number" />
                            <Field label="API Key" path="Sonarr.api_key" type="password" />
                        </div>
                        <Field label="Root Folder" path="Sonarr.root_folder" />
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
