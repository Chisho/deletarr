import React from 'react'
import { LayoutDashboard, Settings, Activity, Trash2 } from 'lucide-react'
import Console from '@/components/Console'

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
    <button
        onClick={onClick}
        className={`flex items-center w-full px-4 py-2 text-sm font-medium transition-colors rounded-md hover:bg-accent hover:text-accent-foreground ${active ? 'bg-accent text-accent-foreground' : 'text-muted-foreground'
            }`}
    >
        <Icon className="w-4 h-4 mr-2" />
        {label}
    </button>
)

export default function Layout({ children, activePage, setActivePage }) {
    return (
        <div className="flex min-h-screen bg-background text-foreground">
            {/* Sidebar */}
            <div className="w-64 border-r border-border bg-card flex flex-col">
                <div className="p-6 flex items-center space-x-2">
                    <Trash2 className="w-6 h-6 text-primary" />
                    <span className="text-xl font-bold">Deletarr</span>
                </div>
                <nav className="flex-1 px-4 space-y-1">
                    <SidebarItem
                        icon={LayoutDashboard}
                        label="Dashboard"
                        active={activePage === 'dashboard'}
                        onClick={() => setActivePage('dashboard')}
                    />
                    <SidebarItem
                        icon={Activity}
                        label="Manual Run"
                        active={activePage === 'dry-run'}
                        onClick={() => setActivePage('dry-run')}
                    />
                    <SidebarItem
                        icon={Settings}
                        label="Settings"
                        active={activePage === 'settings'}
                        onClick={() => setActivePage('settings')}
                    />
                </nav>
                <div className="p-4 border-t border-border">
                    <div className="text-xs text-muted-foreground">
                        v1.3.0
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto pb-12">
                <div className="container py-6 max-w-7xl mx-auto px-6">
                    {children}
                </div>
            </main>

            {/* Console Overlay */}
            <Console />
        </div>
    )
}
