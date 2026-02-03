import React, { useState, useEffect, useRef } from 'react'
import { Terminal, ChevronUp, ChevronDown, Minimize2, Maximize2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Console() {
    const [logs, setLogs] = useState([])
    const [isOpen, setIsOpen] = useState(false)
    const logsEndRef = useRef(null)

    const fetchLogs = async () => {
        try {
            const res = await fetch('/api/logs')
            const data = await res.json()
            if (data.logs) {
                setLogs(data.logs)
            }
        } catch (err) {
            console.error("Failed to fetch logs:", err)
        }
    }

    useEffect(() => {
        fetchLogs()
        const interval = setInterval(fetchLogs, 2000)
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        if (isOpen && logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: "smooth" })
        }
    }, [logs, isOpen])

    return (
        <div className={`fixed bottom-0 left-0 right-0 bg-black border-t border-border transition-all duration-300 z-50 flex flex-col ${isOpen ? 'h-64' : 'h-10'}`}>
            {/* Header */}
            <div
                className="flex items-center justify-between px-4 h-10 bg-muted/50 cursor-pointer hover:bg-muted"
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="flex items-center space-x-2 text-xs font-mono text-muted-foreground">
                    <Terminal className="w-4 h-4" />
                    <span>Console Logs</span>
                </div>
                <div className="flex items-center">
                    {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
                </div>
            </div>

            {/* Log Content */}
            {isOpen && (
                <div className="flex-1 overflow-y-auto p-4 font-mono text-xs text-green-400 bg-black/95">
                    {logs.length === 0 ? (
                        <div className="text-muted-foreground italic">No logs execution yet...</div>
                    ) : (
                        logs.map((log, i) => (
                            <div key={i} className="break-all whitespace-pre-wrap">{log}</div>
                        ))
                    )}
                    <div ref={logsEndRef} />
                </div>
            )}
        </div>
    )
}
