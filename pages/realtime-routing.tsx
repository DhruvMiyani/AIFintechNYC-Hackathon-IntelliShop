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
}

export default function RealtimeRouting() {
  const [processors, setProcessors] = useState<ProcessorHealth[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [isSimulating, setIsSimulating] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('Disconnected')
  const [messagesReceived, setMessagesReceived] = useState(0)
  
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
              break
              
            case 'simulation_status':
              setIsSimulating(message.running)
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
            🔄 Real-Time Payment Routing
          </h1>
          <p className="text-lg sm:text-xl text-blue-200 mb-6">
            Live WebSocket-powered payment orchestration with Claude intelligence
          </p>
          
          {/* Connection Status */}
          <div className="flex flex-wrap justify-center items-center space-x-4 mb-6">
            <div className="flex items-center space-x-2">
              <div 
                className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} 
                            ${isConnected ? 'animate-pulse' : ''}`}
              ></div>
              <span className="text-sm text-white">{connectionStatus}</span>
            </div>
            <span className="text-sm text-gray-400">Messages: {messagesReceived}</span>
          </div>
          
          {/* Controls */}
          <div className="flex flex-wrap justify-center space-x-4">
            <button
              onClick={startSimulation}
              disabled={!isConnected || isSimulating}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-medium transition text-sm sm:text-base"
            >
              {isSimulating ? '🟢 Live Simulation Active' : '▶️ Start Live Demo'}
            </button>
            <button
              onClick={stopSimulation}
              disabled={!isConnected || !isSimulating}
              className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-medium transition text-sm sm:text-base"
            >
              ⏹️ Stop Demo
            </button>
            <button
              onClick={connectWebSocket}
              disabled={isConnected}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-medium transition text-sm sm:text-base"
            >
              🔗 Reconnect
            </button>
          </div>
        </div>

        {/* Processor Health Dashboard */}
        <div className="bg-black/20 backdrop-blur-lg rounded-2xl p-4 sm:p-6 border border-white/20 mb-8">
          <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">🏥 Live Processor Health</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {processors.map(processor => (
              <div key={processor.name} className="bg-white/10 rounded-lg p-4 border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-white text-sm sm:text-base">{processor.name}</h3>
                  <div 
                    className="w-3 h-3 rounded-full animate-pulse"
                    style={{ backgroundColor: getStatusColor(processor.status) }}
                  ></div>
                </div>
                <div className="text-xs sm:text-sm space-y-1">
                  <p className="text-gray-300">
                    Status: <span style={{ color: getStatusColor(processor.status) }}>
                      {processor.status.toUpperCase()}
                    </span>
                  </p>
                  <p className="text-gray-300">Risk: {processor.risk}%</p>
                  <p className="text-gray-300">Freeze Resist: {processor.freezeResistance}%</p>
                  {processor.issues.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {processor.issues.map((issue, i) => (
                        <p key={i} className="text-xs text-red-300">⚠️ {issue}</p>
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-gray-400 mt-2">
                    Updated: {new Date(processor.lastUpdate * 1000).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Transaction Stream */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 sm:p-6 border border-white/20">
          <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">📡 Live Transaction Stream</h2>
          
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
                <div key={transaction.id} className="bg-white/10 rounded-lg p-4 border border-white/10">
                  {/* Transaction Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-3">
                    <div className="mb-2 sm:mb-0">
                      <h3 className="text-white font-medium text-sm sm:text-base">{transaction.description}</h3>
                      <p className="text-xs sm:text-sm text-gray-400">
                        ${transaction.amount} {transaction.currency} • {transaction.id}
                      </p>
                    </div>
                    <div className="text-left sm:text-right">
                      <div className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                        transaction.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                        transaction.status === 'routing' ? 'bg-yellow-500/20 text-yellow-300 animate-pulse' :
                        'bg-blue-500/20 text-blue-300'
                      }`}>
                        {transaction.status.toUpperCase()}
                      </div>
                      {transaction.selectedProcessor && (
                        <p className="text-xs sm:text-sm text-blue-300 mt-1">→ {transaction.selectedProcessor}</p>
                      )}
                    </div>
                  </div>

                  {/* Routing Steps */}
                  {transaction.routingSteps.length > 0 && (
                    <div className="space-y-2">
                      {transaction.routingSteps.map(step => (
                        <div 
                          key={`${transaction.id}-${step.step}`}
                          className={`flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3 p-3 rounded border text-xs sm:text-sm ${getActionColor(step.action)}`}
                        >
                          <div className="w-6 h-6 rounded-full bg-current/20 flex items-center justify-center text-xs font-bold flex-shrink-0">
                            {step.step}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="break-words">{step.reason}</p>
                            {step.confidence > 0 && (
                              <p className="text-xs opacity-75 mt-1">Confidence: {step.confidence}%</p>
                            )}
                          </div>
                          <div className="text-xs opacity-75 flex items-center space-x-2">
                            <span>{step.processingTime}ms</span>
                            <span className="text-xs">
                              {new Date(step.timestamp * 1000).toLocaleTimeString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-lg sm:text-xl font-bold text-white mb-3">⚡ WebSocket Real-Time</h3>
            <p className="text-blue-200 text-sm sm:text-base">
              True real-time updates via WebSocket connection. Watch live processor health changes and routing decisions as they happen.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-lg sm:text-xl font-bold text-white mb-3">🔄 Auto Re-routing</h3>
            <p className="text-blue-200 text-sm sm:text-base">
              Intelligent fallback when processors become frozen or unavailable. No transaction failures, just seamless re-routing.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-lg sm:text-xl font-bold text-white mb-3">🤖 Claude Intelligence</h3>
            <p className="text-blue-200 text-sm sm:text-base">
              Context-aware processor selection with confidence scoring and detailed reasoning for every routing decision.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}