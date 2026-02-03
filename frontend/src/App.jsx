import { useState } from 'react'
import Layout from '@/layout/Layout'
import Dashboard from '@/pages/Dashboard'
import DryRun from '@/pages/DryRun'
import Settings from '@/pages/Settings'

function App() {
  const [activePage, setActivePage] = useState('dashboard')

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard setActivePage={setActivePage} />
      case 'dry-run':
        return <DryRun />
      case 'settings':
        return <Settings />
      default:
        return <Dashboard />
    }
  }

  return (
    <Layout activePage={activePage} setActivePage={setActivePage}>
      {renderPage()}
    </Layout>
  )
}

export default App
