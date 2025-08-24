import { useState, useEffect, useRef } from 'react'

interface ProcessorHealth {
  name: string
  status: 'healthy' | 'warning' | 'frozen' | 'unavailable'
  risk: number
  freezeResistance: number
  lastUpdate: number
  issues: string[]
  color: string
}

interface RoutingStep {
  step: number
  timestamp: number
  processor: string
  action: 'evaluating' | 'selected' | 'rejected' | 'fallback'
  reason: string
  confidence: number
  processingTime: number
}

interface Transaction {
  id: string
  amount: number
  description: string
  currency: string
  status: 'routing' | 'processing' | 'completed' | 'failed'
  selectedProcessor?: string
  routingSteps: RoutingStep[]
  startTime: number
  metadata?: any
  routingDuration?: number
  decisionPath?: string[]
}

export default function RealtimeRouting() {
  const [processors, setProcessors] = useState<ProcessorHealth[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [isSimulating, setIsSimulating] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('Disconnected')
  const [messagesReceived, setMessagesReceived] = useState(0)
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)
  const [viewMode, setViewMode] = useState<'flow' | 'timeline' | 'tree'>('flow')
  const [reRoutingActive, setReRoutingActive] = useState(false)
  const [reRoutedCount, setReRoutedCount] = useState(0)
  const [failedCount, setFailedCount] = useState(0)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8080')
      
      ws.onopen = () => {
        setIsConnected(true)
        setConnectionStatus('Connected')
        console.log('🔗 Connected to real-time routing service')
      }
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          setMessagesReceived(prev => prev + 1)
          
          switch (message.type) {
            case 'processor_health':
              setProcessors(message.data)
              break
              
            case 'new_transaction':
              setTransactions(prev => {
                const updated = [message.data, ...prev.slice(0, 9)]
                return updated
              })
              break
              
            case 'routing_step':
              setTransactions(prev => prev.map(txn => {
                if (txn.id === message.transaction_id) {
                  // Check if this is a re-routing (fallback action)
                  if (message.step.action === 'fallback' || 
                      (message.step.action === 'rejected' && message.step.reason.includes('frozen'))) {
                    setReRoutingActive(true)
                    setTimeout(() => setReRoutingActive(false), 3000)
                  }
                  return {
                    ...txn,
                    routingSteps: [...txn.routingSteps, message.step]
                  }
                }
                return txn
              }))
              break
              
            case 'transaction_complete':
              setTransactions(prev => prev.map(txn => 
                txn.id === message.data.id ? message.data : txn
              ))
              // Track re-routed and failed transactions
              if (message.data.status === 'completed' && message.data.routingSteps.some(s => s.action === 'fallback' || s.action === 'rejected')) {
                setReRoutedCount(prev => prev + 1)
              } else if (message.data.status === 'failed') {
                setFailedCount(prev => prev + 1)
              }
              break
              
            case 'simulation_status':
              setIsSimulating(message.running)
              break
              
            case 'rerouting_alert':
              // Show re-routing alert for specific transaction
              setReRoutingActive(true)
              setTimeout(() => setReRoutingActive(false), 5000)
              console.log('🔄 RE-ROUTING:', message.message)
              break
          }
        } catch (error) {
          console.error('Error processing WebSocket message:', error)
        }
      }
      
      ws.onclose = () => {
        setIsConnected(false)
        setConnectionStatus('Disconnected')
        console.log('❌ WebSocket connection closed')
        
        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...')
          connectWebSocket()
        }, 3000)
      }
      
      ws.onerror = (error) => {
        setConnectionStatus('Error')
        console.error('WebSocket error:', error)
      }
      
      wsRef.current = ws
      
    } catch (error) {
      setConnectionStatus('Failed to connect')
      console.error('Failed to connect to WebSocket:', error)
    }
  }

  const sendCommand = (command: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command }))
    }
  }

  const startSimulation = () => {
    sendCommand('start_simulation')
  }

  const stopSimulation = () => {
    sendCommand('stop_simulation')
  }

  useEffect(() => {
    connectWebSocket()
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#10B981'
      case 'warning': return '#F59E0B'
      case 'frozen': return '#E11D48'
      case 'unavailable': return '#6B7280'
      default: return '#6B7280'
    }
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'evaluating': return 'bg-blue-500/10 text-blue-300 border-blue-500/20'
      case 'selected': return 'bg-green-500/10 text-green-300 border-green-500/20'
      case 'rejected': return 'bg-red-500/10 text-red-300 border-red-500/20'
      case 'fallback': return 'bg-yellow-500/10 text-yellow-300 border-yellow-500/20'
      default: return 'bg-gray-500/10 text-gray-300 border-gray-500/20'
    }
  }

  const getProcessorIcon = (processor: string) => {
    switch (processor.toLowerCase()) {
      case 'stripe': return '💳'
      case 'paypal': return '🅿️'
      case 'square': return '⬛'
      case 'visa': return '💰'
      case 'adyen': return '🔷'
      case 'crossmint': return '🌐'
      default: return '💳'
    }
  }

  const getProcessorBadgeStyle = (processor: string) => {
    switch (processor.toLowerCase()) {
      case 'stripe':
        return 'bg-purple-600/20 text-purple-300 border-purple-500/30'
      case 'paypal':
        return 'bg-blue-600/20 text-blue-300 border-blue-500/30'
      case 'square':
        return 'bg-gray-600/20 text-gray-300 border-gray-500/30'
      case 'visa':
        return 'bg-yellow-600/20 text-yellow-300 border-yellow-500/30'
      case 'adyen':
        return 'bg-green-600/20 text-green-300 border-green-500/30'
      case 'crossmint':
        return 'bg-indigo-600/20 text-indigo-300 border-indigo-500/30'
      default:
        return 'bg-gray-600/20 text-gray-300 border-gray-500/30'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Enhanced Header with Gradient */}
        <div className="relative mb-8 p-8 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-pink-600/20 backdrop-blur-lg rounded-3xl border border-white/20 overflow-hidden">
          {/* Animated Background Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 animate-pulse"></div>
          
          <div className="relative z-10">
            <h1 className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent mb-3">
              ⚡ Intelligent Payment Routing
            </h1>
            <p className="text-xl sm:text-2xl text-blue-100 mb-6">
              AI-Powered Real-Time Decision Engine with Automatic Re-Routing
            </p>
            
            {/* Status Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
              {/* Connection Status */}
              <div className="bg-white/10 backdrop-blur rounded-xl p-3 border border-white/20">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-300">CONNECTION</span>
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                </div>
                <div className={`text-lg font-bold ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                  {isConnected ? 'LIVE' : 'OFFLINE'}
                </div>
              </div>
              
              {/* Messages Count */}
              <div className="bg-white/10 backdrop-blur rounded-xl p-3 border border-white/20">
                <div className="text-xs text-gray-300 mb-1">MESSAGES</div>
                <div className="text-lg font-bold text-blue-400">{messagesReceived}</div>
              </div>
              
              {/* Re-Routing Status */}
              <div className="bg-white/10 backdrop-blur rounded-xl p-3 border border-white/20">
                <div className="text-xs text-gray-300 mb-1">RE-ROUTED</div>
                <div className={`text-lg font-bold ${reRoutedCount > 0 ? 'text-yellow-400' : 'text-gray-400'}`}>
                  {reRoutedCount} {reRoutedCount > 0 && '🔄'}
                </div>
              </div>
              
              {/* Success Rate */}
              <div className="bg-white/10 backdrop-blur rounded-xl p-3 border border-white/20">
                <div className="text-xs text-gray-300 mb-1">SUCCESS RATE</div>
                <div className="text-lg font-bold text-green-400">
                  {transactions.length > 0 
                    ? `${Math.round((transactions.filter(t => t.status === 'completed').length / transactions.length) * 100)}%`
                    : '100%'
                  }
                </div>
              </div>
            </div>
            
            {/* Re-Routing Alert */}
            {reRoutingActive && (
              <div className="animate-pulse bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-3 mb-4">
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-yellow-400 font-bold animate-spin">🔄</span>
                  <span className="text-yellow-300 font-medium">RE-ROUTING IN PROGRESS - Processor Frozen/Unavailable</span>
                  <span className="text-yellow-400 font-bold animate-spin">🔄</span>
                </div>
              </div>
            )}
          </div>
          
          {/* Enhanced Control Buttons */}
          <div className="relative z-10 flex flex-wrap justify-center gap-3">
            <button
              onClick={startSimulation}
              disabled={!isConnected || isSimulating}
              className={`relative px-6 py-3 rounded-xl font-semibold transition-all transform hover:scale-105 ${
                isSimulating 
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg shadow-green-500/50 animate-pulse' 
                  : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white disabled:from-gray-600 disabled:to-gray-700 disabled:opacity-50'
              }`}
            >
              {isSimulating ? (
                <>
                  <span className="animate-pulse mr-2">🟢</span>
                  Live Simulation Active
                </>
              ) : (
                <>
                  <span className="mr-2">▶️</span>
                  Start Live Demo
                </>
              )}
            </button>
            
            <button
              onClick={stopSimulation}
              disabled={!isConnected || !isSimulating}
              className="px-6 py-3 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-700 disabled:opacity-50 text-white rounded-xl font-semibold transition-all transform hover:scale-105"
            >
              <span className="mr-2">⏹️</span>
              Stop Demo
            </button>
            
            <button
              onClick={connectWebSocket}
              disabled={isConnected}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-gray-600 disabled:to-gray-700 disabled:opacity-50 text-white rounded-xl font-semibold transition-all transform hover:scale-105"
            >
              <span className="mr-2">🔗</span>
              Reconnect
            </button>
          </div>
        </div>

        {/* Routing Statistics */}
        {transactions.length > 0 && (
          <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 backdrop-blur-lg rounded-2xl p-4 sm:p-6 border border-white/20 mb-8">
            <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">📈 Routing Statistics</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-white/10 rounded-lg p-3">
                <div className="text-2xl font-bold text-white">{transactions.length}</div>
                <div className="text-xs text-gray-300">Total Transactions</div>
              </div>
              <div className="bg-white/10 rounded-lg p-3">
                <div className="text-2xl font-bold text-green-400">
                  {transactions.filter(t => t.status === 'completed').length}
                </div>
                <div className="text-xs text-gray-300">Successfully Routed</div>
              </div>
              <div className="bg-white/10 rounded-lg p-3">
                <div className="text-2xl font-bold text-blue-400">
                  {transactions.reduce((sum, t) => sum + t.routingSteps.length, 0) / Math.max(transactions.length, 1) | 0}
                </div>
                <div className="text-xs text-gray-300">Avg Steps/Transaction</div>
              </div>
              <div className="bg-white/10 rounded-lg p-3">
                <div className="text-2xl font-bold text-purple-400">
                  {transactions.reduce((sum, t) => sum + t.routingSteps.reduce((s, step) => s + step.processingTime, 0), 0) / Math.max(transactions.length, 1) | 0}ms
                </div>
                <div className="text-xs text-gray-300">Avg Processing Time</div>
              </div>
            </div>
            
            {/* Processor Usage Distribution */}
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="text-sm font-medium text-gray-300 mb-2">Processor Selection Distribution</div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(
                  transactions.reduce((acc, t) => {
                    if (t.selectedProcessor) {
                      acc[t.selectedProcessor] = (acc[t.selectedProcessor] || 0) + 1
                    }
                    return acc
                  }, {} as Record<string, number>)
                ).map(([processor, count]) => (
                  <div key={processor} className={`px-3 py-1 rounded-full text-xs font-medium ${getProcessorBadgeStyle(processor)}`}>
                    {getProcessorIcon(processor)} {processor.toUpperCase()}: {count}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Processor Health Dashboard */}
        <div className="bg-gradient-to-r from-black/30 to-purple-900/30 backdrop-blur-lg rounded-2xl p-6 border border-white/20 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">
              <span className="mr-2">🏥</span>
              Live Processor Health Monitor
            </h2>
            {processors.some(p => p.status === 'frozen') && (
              <div className="flex items-center space-x-2 bg-red-500/20 px-3 py-1 rounded-full border border-red-500/50">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <span className="text-sm font-medium text-red-300">FREEZE DETECTED</span>
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {processors.map(processor => {
              const isFrozen = processor.status === 'frozen'
              const isWarning = processor.status === 'warning'
              const isHealthy = processor.status === 'healthy'
              
              return (
                <div 
                  key={processor.name} 
                  className={`relative rounded-xl p-4 transition-all transform hover:scale-105 ${
                    isFrozen ? 'bg-red-500/20 border-2 border-red-500/50 animate-pulse' :
                    isWarning ? 'bg-yellow-500/20 border-2 border-yellow-500/50' :
                    'bg-white/10 border border-white/20'
                  }`}
                >
                  {/* Status Badge */}
                  <div className="absolute -top-2 -right-2">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      isFrozen ? 'bg-red-500 animate-pulse' :
                      isWarning ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}>
                      {isFrozen ? '❌' : isWarning ? '⚠️' : '✅'}
                    </div>
                  </div>
                  
                  {/* Processor Info */}
                  <div className="mb-3">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-2xl">{getProcessorIcon(processor.name)}</span>
                      <h3 className="font-bold text-white text-lg">{processor.name}</h3>
                    </div>
                    <div className={`text-sm font-medium ${
                      isFrozen ? 'text-red-300' :
                      isWarning ? 'text-yellow-300' :
                      'text-green-300'
                    }`}>
                      {processor.status.toUpperCase()}
                    </div>
                  </div>
                  
                  {/* Metrics */}
                  <div className="space-y-2">
                    {/* Risk Level */}
                    <div>
                      <div className="flex justify-between text-xs text-gray-400 mb-1">
                        <span>Risk</span>
                        <span>{processor.risk}%</span>
                      </div>
                      <div className="w-full bg-black/30 rounded-full h-2">
                        <div 
                          className={`h-full rounded-full transition-all ${
                            processor.risk > 70 ? 'bg-red-500' :
                            processor.risk > 40 ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${processor.risk}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    {/* Freeze Resistance */}
                    <div>
                      <div className="flex justify-between text-xs text-gray-400 mb-1">
                        <span>Freeze Resist</span>
                        <span>{processor.freezeResistance}%</span>
                      </div>
                      <div className="w-full bg-black/30 rounded-full h-2">
                        <div 
                          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500"
                          style={{ width: `${processor.freezeResistance}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Issues */}
                  {processor.issues.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-white/10 space-y-1">
                      {processor.issues.map((issue, i) => (
                        <p key={i} className="text-xs text-red-300 flex items-start">
                          <span className="mr-1">⚠️</span>
                          <span>{issue}</span>
                        </p>
                      ))}
                    </div>
                  )}
                  
                  {/* Last Update */}
                  <p className="text-xs text-gray-500 mt-3">
                    {new Date(processor.lastUpdate * 1000).toLocaleTimeString()}
                  </p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Visualization Mode Selector */}
        <div className="bg-black/20 backdrop-blur-lg rounded-2xl p-4 mb-8 border border-white/20">
          <div className="flex flex-wrap items-center justify-between">
            <h2 className="text-lg font-bold text-white mb-3 sm:mb-0">📊 Visualization Mode</h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setViewMode('flow')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  viewMode === 'flow' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                🔄 Flow View
              </button>
              <button
                onClick={() => setViewMode('timeline')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  viewMode === 'timeline' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                ⏱️ Timeline
              </button>
              <button
                onClick={() => setViewMode('tree')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  viewMode === 'tree' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                🌳 Decision Tree
              </button>
            </div>
          </div>
        </div>

        {/* Live Transaction Stream */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 sm:p-6 border border-white/20">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl sm:text-2xl font-bold text-white">📡 Live Transaction Stream</h2>
            <div className="text-sm text-gray-400">
              Total Processed: {transactions.length}
            </div>
          </div>
          
          {!isConnected ? (
            <div className="text-center py-8">
              <div className="text-gray-400 mb-4">
                <div className="animate-spin inline-block w-8 h-8 border-4 border-current border-t-transparent rounded-full" role="status" aria-label="loading">
                  <span className="sr-only">Loading...</span>
                </div>
              </div>
              <p className="text-gray-400">Connecting to real-time routing service...</p>
            </div>
          ) : transactions.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <p>Start the simulation to see live routing decisions...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {transactions.map(transaction => (
                <div key={transaction.id} className="bg-white/10 rounded-lg p-4 sm:p-6 border border-white/10 hover:border-white/30 transition-all">
                  {/* Transaction Header with Routing Flow */}
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between mb-4">
                    <div className="mb-3 lg:mb-0 flex-1">
                      <h3 className="text-white font-medium text-base sm:text-lg mb-1">{transaction.description}</h3>
                      <div className="flex flex-wrap items-center gap-2 text-xs sm:text-sm text-gray-400">
                        <span className="bg-gray-600/30 px-2 py-1 rounded">${transaction.amount} {transaction.currency}</span>
                        <span>•</span>
                        <span className="font-mono">{transaction.id}</span>
                        <span>•</span>
                        <span>{new Date(transaction.startTime * 1000).toLocaleTimeString()}</span>
                        {transaction.metadata?.type && (
                          <>
                            <span>•</span>
                            <span className="bg-purple-600/30 px-2 py-1 rounded text-purple-300">
                              {transaction.metadata.type}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    {/* Routing Flow Visualization */}
                    <div className="flex items-center space-x-3">
                      <div className={`px-3 py-2 rounded-lg text-xs font-medium border ${
                        transaction.status === 'completed' ? 'bg-green-500/20 text-green-300 border-green-500/30' :
                        transaction.status === 'routing' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30 animate-pulse' :
                        'bg-blue-500/20 text-blue-300 border-blue-500/30'
                      }`}>
                        {transaction.status.toUpperCase()}
                      </div>
                      
                      {transaction.selectedProcessor && (
                        <>
                          <div className="text-gray-400">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                            </svg>
                          </div>
                          <div className={`px-4 py-2 rounded-lg font-medium text-sm ${getProcessorBadgeStyle(transaction.selectedProcessor)}`}>
                            <div className="flex items-center space-x-2">
                              <span>{getProcessorIcon(transaction.selectedProcessor)}</span>
                              <span>{transaction.selectedProcessor.toUpperCase()}</span>
                            </div>
                            {transaction.status === 'completed' && (
                              <div className="text-xs opacity-75 mt-1">
                                Processing Time: {transaction.routingSteps.reduce((sum, step) => sum + step.processingTime, 0)}ms
                              </div>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Routing Visualization Based on Mode */}
                  {transaction.routingSteps.length > 0 && (
                    <div className="space-y-3">
                      <div className="flex items-center space-x-2 mb-4">
                        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-blue-400/30 to-transparent"></div>
                        <span className="text-xs font-medium text-blue-300 px-2">
                          {viewMode === 'flow' && 'ROUTING LOGIC FLOW'}
                          {viewMode === 'timeline' && 'DECISION TIMELINE'}
                          {viewMode === 'tree' && 'DECISION TREE'}
                        </span>
                        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-blue-400/30 to-transparent"></div>
                      </div>
                      
                      {/* Flow View - Default */}
                      {viewMode === 'flow' && (
                        <>
                      
                      {transaction.routingSteps.map((step, index) => (
                        <div key={`${transaction.id}-${step.step}`} className="relative">
                          <div className={`flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3 p-4 rounded-lg border-2 text-xs sm:text-sm ${getActionColor(step.action)}`}>
                            {/* Step Number */}
                            <div className="w-8 h-8 rounded-full bg-current/20 flex items-center justify-center text-sm font-bold flex-shrink-0 border border-current/30">
                              {step.step}
                            </div>
                            
                            {/* Processor Being Evaluated */}
                            <div className="flex items-center space-x-2 flex-shrink-0">
                              <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getProcessorBadgeStyle(step.processor)}`}>
                                <span className="mr-1">{getProcessorIcon(step.processor)}</span>
                                {step.processor.toUpperCase()}
                              </div>
                              <div className="text-current/60">
                                {step.action === 'evaluating' && '🔍'}
                                {step.action === 'selected' && '✅'}
                                {step.action === 'rejected' && '❌'}
                                {step.action === 'fallback' && '🔄'}
                              </div>
                            </div>
                            
                            {/* Routing Logic Explanation */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start space-x-2">
                                <span className="text-current/80 font-medium text-xs">LOGIC:</span>
                                <p className="break-words text-current">{step.reason}</p>
                              </div>
                              {step.confidence > 0 && (
                                <div className="flex items-center space-x-2 mt-2">
                                  <span className="text-xs opacity-75">Confidence:</span>
                                  <div className="flex-1 max-w-24 bg-current/20 rounded-full h-2">
                                    <div 
                                      className="bg-current h-full rounded-full transition-all duration-300"
                                      style={{ width: `${step.confidence}%` }}
                                    ></div>
                                  </div>
                                  <span className="text-xs opacity-75 font-medium">{step.confidence}%</span>
                                </div>
                              )}
                            </div>
                            
                            {/* Timing & Status */}
                            <div className="text-xs opacity-75 flex flex-col items-end space-y-1 flex-shrink-0">
                              <div className="flex items-center space-x-1">
                                <span>⏱️</span>
                                <span>{step.processingTime}ms</span>
                              </div>
                              <span className="text-xs">
                                {new Date(step.timestamp * 1000).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>
                          
                          {/* Flow Arrow */}
                          {index < transaction.routingSteps.length - 1 && (
                            <div className="flex justify-center my-2">
                              <div className="text-gray-400">
                                <svg className="w-4 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                                </svg>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                      
                      {/* Final Destination */}
                      {transaction.selectedProcessor && (
                        <div className="mt-4 p-4 bg-green-500/10 border-2 border-green-500/30 rounded-lg">
                          <div className="flex items-center justify-center space-x-3">
                            <span className="text-green-300 font-medium">🎯 FINAL DESTINATION:</span>
                            <div className={`px-4 py-2 rounded-lg font-bold text-lg border-2 ${getProcessorBadgeStyle(transaction.selectedProcessor)} border-current/50`}>
                              <span className="mr-2">{getProcessorIcon(transaction.selectedProcessor)}</span>
                              {transaction.selectedProcessor.toUpperCase()}
                            </div>
                            {transaction.status === 'completed' && (
                              <span className="text-green-400 text-xl">✅</span>
                            )}
                          </div>
                          {transaction.status === 'completed' && (
                            <div className="text-center mt-2 text-xs text-green-300/75">
                              Total Processing Time: {transaction.routingSteps.reduce((sum, step) => sum + step.processingTime, 0)}ms
                            </div>
                          )}
                        </div>
                      )}
                      </>
                      )}
                      
                      {/* Timeline View */}
                      {viewMode === 'timeline' && (
                        <div className="relative">
                          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 via-purple-500 to-green-500"></div>
                          {transaction.routingSteps.map((step, index) => (
                            <div key={`${transaction.id}-timeline-${step.step}`} className="relative flex items-start mb-6">
                              <div className={`z-10 w-16 h-16 rounded-full flex items-center justify-center text-white font-bold border-4 ${
                                step.action === 'selected' ? 'bg-green-500 border-green-300' :
                                step.action === 'rejected' ? 'bg-red-500 border-red-300' :
                                step.action === 'evaluating' ? 'bg-blue-500 border-blue-300' :
                                'bg-yellow-500 border-yellow-300'
                              }`}>
                                {step.step}
                              </div>
                              <div className="ml-6 flex-1">
                                <div className={`p-4 rounded-lg ${getActionColor(step.action)}`}>
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-2">
                                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getProcessorBadgeStyle(step.processor)}`}>
                                        {getProcessorIcon(step.processor)} {step.processor.toUpperCase()}
                                      </span>
                                      <span className="text-xs text-gray-400">
                                        {new Date(step.timestamp * 1000).toLocaleTimeString('en-US', { 
                                          hour12: false, 
                                          hour: '2-digit', 
                                          minute: '2-digit', 
                                          second: '2-digit'
                                        })}
                                      </span>
                                    </div>
                                    <span className="text-xs font-medium">{step.processingTime}ms</span>
                                  </div>
                                  <p className="text-sm">{step.reason}</p>
                                  {step.confidence > 0 && (
                                    <div className="mt-2 flex items-center space-x-2">
                                      <span className="text-xs">Confidence:</span>
                                      <div className="flex-1 max-w-32 bg-white/20 rounded-full h-2">
                                        <div 
                                          className="bg-gradient-to-r from-blue-400 to-green-400 h-full rounded-full"
                                          style={{ width: `${step.confidence}%` }}
                                        ></div>
                                      </div>
                                      <span className="text-xs font-medium">{step.confidence}%</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                          {transaction.selectedProcessor && (
                            <div className="relative flex items-center">
                              <div className="z-10 w-16 h-16 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-white font-bold border-4 border-green-300 shadow-lg">
                                ✓
                              </div>
                              <div className="ml-6 flex-1 p-4 bg-green-500/20 border-2 border-green-500/30 rounded-lg">
                                <div className="flex items-center space-x-3">
                                  <span className="text-green-300 font-medium">Final Selection:</span>
                                  <span className={`px-4 py-2 rounded-lg font-bold ${getProcessorBadgeStyle(transaction.selectedProcessor)}`}>
                                    {getProcessorIcon(transaction.selectedProcessor)} {transaction.selectedProcessor.toUpperCase()}
                                  </span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Decision Tree View */}
                      {viewMode === 'tree' && (
                        <div className="p-6 bg-black/30 rounded-lg">
                          <div className="flex flex-col items-center">
                            <div className="mb-4 p-3 bg-blue-500/20 border-2 border-blue-500/30 rounded-lg">
                              <div className="text-center">
                                <div className="text-sm font-bold text-blue-300">TRANSACTION</div>
                                <div className="text-xs text-gray-300 mt-1">${transaction.amount} {transaction.currency}</div>
                              </div>
                            </div>
                            
                            <div className="w-0.5 h-8 bg-blue-400"></div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
                              {transaction.routingSteps.map((step, index) => (
                                <div key={`${transaction.id}-tree-${step.step}`} className="flex flex-col items-center">
                                  <div className="w-0.5 h-4 bg-gray-400"></div>
                                  <div className={`w-full p-3 rounded-lg border-2 ${
                                    step.action === 'selected' ? 'bg-green-500/20 border-green-500/30' :
                                    step.action === 'rejected' ? 'bg-red-500/20 border-red-500/30' :
                                    'bg-yellow-500/20 border-yellow-500/30'
                                  }`}>
                                    <div className="text-center mb-2">
                                      <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getProcessorBadgeStyle(step.processor)}`}>
                                        {getProcessorIcon(step.processor)} {step.processor.toUpperCase()}
                                      </span>
                                    </div>
                                    <div className="text-xs text-center">
                                      <div className={`font-medium mb-1 ${
                                        step.action === 'selected' ? 'text-green-300' :
                                        step.action === 'rejected' ? 'text-red-300' :
                                        'text-yellow-300'
                                      }`}>
                                        {step.action.toUpperCase()}
                                      </div>
                                      <div className="text-gray-400 text-xs leading-tight">{step.reason}</div>
                                      {step.confidence > 0 && (
                                        <div className="mt-2 text-blue-300">
                                          {step.confidence}% confidence
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                  {step.action === 'selected' && (
                                    <>
                                      <div className="w-0.5 h-4 bg-green-400"></div>
                                      <div className="text-green-400 text-2xl">✓</div>
                                    </>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Enhanced Feature Cards */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="group relative bg-gradient-to-br from-blue-600/20 to-purple-600/20 backdrop-blur-lg rounded-2xl p-6 border border-white/20 transition-all hover:scale-105 hover:shadow-xl hover:shadow-blue-500/20">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative z-10">
              <div className="flex items-center mb-3">
                <span className="text-3xl mr-3">⚡</span>
                <h3 className="text-xl font-bold text-white">WebSocket Real-Time</h3>
              </div>
              <p className="text-blue-100">
                True real-time updates via WebSocket connection. Watch live processor health changes and routing decisions as they happen.
              </p>
              <div className="mt-3 flex items-center text-xs text-blue-300">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></span>
                <span>Live Connection Active</span>
              </div>
            </div>
          </div>
          
          <div className="group relative bg-gradient-to-br from-yellow-600/20 to-orange-600/20 backdrop-blur-lg rounded-2xl p-6 border border-white/20 transition-all hover:scale-105 hover:shadow-xl hover:shadow-yellow-500/20">
            <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative z-10">
              <div className="flex items-center mb-3">
                <span className="text-3xl mr-3">🔄</span>
                <h3 className="text-xl font-bold text-white">Smart Re-routing</h3>
              </div>
              <p className="text-yellow-100">
                Intelligent fallback when processors freeze. Automatic re-routing ensures zero transaction failures.
              </p>
              <div className="mt-3 flex items-center text-xs text-yellow-300">
                {reRoutedCount > 0 ? (
                  <>
                    <span className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse mr-2"></span>
                    <span>{reRoutedCount} Transactions Re-routed</span>
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                    <span>All Routes Optimal</span>
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="group relative bg-gradient-to-br from-purple-600/20 to-pink-600/20 backdrop-blur-lg rounded-2xl p-6 border border-white/20 transition-all hover:scale-105 hover:shadow-xl hover:shadow-purple-500/20">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative z-10">
              <div className="flex items-center mb-3">
                <span className="text-3xl mr-3">🤖</span>
                <h3 className="text-xl font-bold text-white">AI Intelligence</h3>
              </div>
              <p className="text-purple-100">
                Claude-powered routing with confidence scoring and detailed reasoning for every decision.
              </p>
              <div className="mt-3 flex items-center text-xs text-purple-300">
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-pulse mr-2"></span>
                <span>AI Engine Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}