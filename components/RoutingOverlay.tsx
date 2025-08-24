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

interface RoutingOverlayProps {
  isOpen: boolean
  onClose: () => void
}

export default function RoutingOverlay({ isOpen, onClose }: RoutingOverlayProps) {
  const [processors, setProcessors] = useState<ProcessorHealth[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [isSimulating, setIsSimulating] = useState(false)
  const [reRoutingActive, setReRoutingActive] = useState(false)
  const [reRoutedCount, setReRoutedCount] = useState(0)
  
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (isOpen) {
      connectWebSocket()
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [isOpen])

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8080')
      
      ws.onopen = () => {
        setIsConnected(true)
        console.log('🔗 Connected to routing service')
      }
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          
          switch (message.type) {
            case 'processor_health':
              setProcessors(message.data)
              break
              
            case 'new_transaction':
              setTransactions(prev => {
                const updated = [message.data, ...prev.slice(0, 4)] // Keep only 5 transactions
                return updated
              })
              break
              
            case 'routing_step':
              setTransactions(prev => prev.map(txn => {
                if (txn.id === message.transaction_id) {
                  if (message.step.action === 'fallback' || 
                      (message.step.action === 'rejected' && message.step.reason.includes('FROZEN'))) {
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
              if (message.data.status === 'completed' && 
                  message.data.routingSteps.some(s => s.action === 'fallback' || s.action === 'rejected')) {
                setReRoutedCount(prev => prev + 1)
              }
              break
              
            case 'simulation_status':
              setIsSimulating(message.running)
              break
              
            case 'rerouting_alert':
              setReRoutingActive(true)
              setTimeout(() => setReRoutingActive(false), 4000)
              break
          }
        } catch (error) {
          console.error('Error processing message:', error)
        }
      }
      
      ws.onclose = () => setIsConnected(false)
      ws.onerror = (error) => console.error('WebSocket error:', error)
      
      wsRef.current = ws
      
    } catch (error) {
      console.error('Failed to connect:', error)
    }
  }

  const startSimulation = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command: 'start_simulation' }))
    }
  }

  const stopSimulation = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command: 'stop_simulation' }))
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
      case 'stripe': return 'bg-purple-600/20 text-purple-300 border border-purple-500/30'
      case 'paypal': return 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
      case 'square': return 'bg-gray-600/20 text-gray-300 border border-gray-500/30'
      case 'visa': return 'bg-yellow-600/20 text-yellow-300 border border-yellow-500/30'
      case 'adyen': return 'bg-green-600/20 text-green-300 border border-green-500/30'
      case 'crossmint': return 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
      default: return 'bg-gray-600/20 text-gray-300 border border-gray-500/30'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      ></div>
      
      {/* Modal */}
      <div className="relative w-full h-full flex items-center justify-center p-4">
        <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 rounded-3xl border-2 border-white/20 shadow-2xl w-full max-w-6xl h-[90vh] overflow-hidden">
          
          {/* Header */}
          <div className="relative p-6 bg-gradient-to-r from-blue-600/30 via-purple-600/30 to-pink-600/30 border-b border-white/20">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 animate-pulse"></div>
            
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-10 h-10 bg-red-500/20 hover:bg-red-500/40 rounded-full flex items-center justify-center text-red-300 hover:text-red-200 transition-all z-10"
            >
              ✕
            </button>
            
            <div className="relative z-10">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent mb-2">
                ⚡ Intelligent Payment Routing
              </h1>
              <p className="text-lg text-blue-100 mb-4">
                Real-Time AI Decision Engine with Automatic Re-Routing
              </p>
              
              {/* Status Row */}
              <div className="flex flex-wrap gap-3 mb-4">
                <div className="bg-white/10 rounded-lg px-3 py-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                    <span className="text-sm font-medium text-white">
                      {isConnected ? 'CONNECTED' : 'OFFLINE'}
                    </span>
                  </div>
                </div>
                
                <div className="bg-white/10 rounded-lg px-3 py-2">
                  <span className="text-sm text-gray-300">Transactions: </span>
                  <span className="text-sm font-bold text-blue-400">{transactions.length}</span>
                </div>
                
                {reRoutedCount > 0 && (
                  <div className="bg-yellow-500/20 rounded-lg px-3 py-2 border border-yellow-500/50">
                    <span className="text-sm text-yellow-300">🔄 Re-routed: {reRoutedCount}</span>
                  </div>
                )}
              </div>
              
              {/* Re-routing Alert */}
              {reRoutingActive && (
                <div className="animate-pulse bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-3 mb-4">
                  <div className="flex items-center justify-center space-x-2">
                    <span className="text-yellow-400 font-bold animate-spin">🔄</span>
                    <span className="text-yellow-300 font-medium">INTELLIGENT RE-ROUTING ACTIVE</span>
                    <span className="text-yellow-400 font-bold animate-spin">🔄</span>
                  </div>
                </div>
              )}
              
              {/* Controls */}
              <div className="flex gap-3">
                <button
                  onClick={startSimulation}
                  disabled={!isConnected || isSimulating}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all transform hover:scale-105 ${
                    isSimulating 
                      ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white animate-pulse' 
                      : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white disabled:opacity-50'
                  }`}
                >
                  {isSimulating ? '🟢 Live' : '▶️ Start'}
                </button>
                
                <button
                  onClick={stopSimulation}
                  disabled={!isConnected || !isSimulating}
                  className="px-4 py-2 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500 disabled:opacity-50 text-white rounded-lg font-semibold transition-all transform hover:scale-105"
                >
                  ⏹️ Stop
                </button>
              </div>
            </div>
          </div>
          
          {/* Content */}
          <div className="h-full overflow-y-auto p-6">
            
            {/* Processor Health */}
            <div className="mb-6">
              <h2 className="text-xl font-bold text-white mb-4">
                🏥 Live Processor Health
                {processors.some(p => p.status === 'frozen') && (
                  <span className="ml-3 text-sm bg-red-500/20 px-2 py-1 rounded-full border border-red-500/50 text-red-300">
                    ⚠️ FREEZE DETECTED
                  </span>
                )}
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                {processors.map(processor => {
                  const isFrozen = processor.status === 'frozen'
                  return (
                    <div 
                      key={processor.name}
                      className={`relative p-3 rounded-lg transition-all ${
                        isFrozen ? 'bg-red-500/20 border-2 border-red-500/50 animate-pulse' : 'bg-white/10 border border-white/20'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{getProcessorIcon(processor.name)}</span>
                          <span className="font-bold text-white text-sm">{processor.name}</span>
                        </div>
                        <div className={`text-xs px-2 py-1 rounded ${
                          isFrozen ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
                        }`}>
                          {isFrozen ? '❌' : '✅'}
                        </div>
                      </div>
                      
                      <div className="text-xs space-y-1">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Risk:</span>
                          <span className={processor.risk > 70 ? 'text-red-400' : 'text-green-400'}>
                            {processor.risk}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Resist:</span>
                          <span className="text-blue-400">{processor.freezeResistance}%</span>
                        </div>
                        
                        {processor.issues.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {processor.issues.slice(0, 2).map((issue, i) => (
                              <p key={i} className="text-xs text-red-300 leading-tight">{issue}</p>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
            
            {/* Live Transaction Stream */}
            <div>
              <h2 className="text-xl font-bold text-white mb-4">📡 Live Transaction Stream</h2>
              
              {transactions.length === 0 ? (
                <div className="text-center py-8 text-gray-400 bg-white/5 rounded-lg">
                  <p>Click "Start" to see live routing decisions...</p>
                </div>
              ) : (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {transactions.map(transaction => (
                    <div key={transaction.id} className="bg-white/10 rounded-lg p-4 border border-white/10">
                      
                      {/* Transaction Header */}
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="text-white font-medium">{transaction.description}</h3>
                          <p className="text-sm text-gray-400">
                            ${transaction.amount} • {transaction.id} • {new Date(transaction.startTime * 1000).toLocaleTimeString()}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className={`px-2 py-1 rounded text-xs font-medium ${
                            transaction.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                            transaction.status === 'routing' ? 'bg-yellow-500/20 text-yellow-300 animate-pulse' :
                            'bg-blue-500/20 text-blue-300'
                          }`}>
                            {transaction.status.toUpperCase()}
                          </div>
                          
                          {transaction.selectedProcessor && (
                            <div className={`px-3 py-1 rounded-lg font-medium ${getProcessorBadgeStyle(transaction.selectedProcessor)}`}>
                              {getProcessorIcon(transaction.selectedProcessor)} {transaction.selectedProcessor.toUpperCase()}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* Routing Steps */}
                      {transaction.routingSteps.length > 0 && (
                        <div className="space-y-2">
                          {transaction.routingSteps.map(step => (
                            <div 
                              key={`${transaction.id}-${step.step}`}
                              className={`p-3 rounded border text-xs ${
                                step.action === 'selected' || step.action === 'fallback' ? 'bg-green-500/10 text-green-300 border-green-500/20' :
                                step.action === 'rejected' ? 'bg-red-500/10 text-red-300 border-red-500/20' :
                                'bg-blue-500/10 text-blue-300 border-blue-500/20'
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2 mb-1">
                                    <span className="font-bold">#{step.step}</span>
                                    {step.processor !== 'Claude' && (
                                      <span className={`px-2 py-1 rounded text-xs ${getProcessorBadgeStyle(step.processor)}`}>
                                        {getProcessorIcon(step.processor)} {step.processor.toUpperCase()}
                                      </span>
                                    )}
                                    <span className="text-xs opacity-75">
                                      {step.action.toUpperCase()}
                                    </span>
                                  </div>
                                  <p className="leading-tight">{step.reason}</p>
                                  {step.confidence > 0 && (
                                    <div className="mt-2 flex items-center space-x-2">
                                      <span>Confidence:</span>
                                      <div className="flex-1 max-w-20 bg-white/20 rounded-full h-1">
                                        <div 
                                          className="bg-current h-full rounded-full"
                                          style={{ width: `${step.confidence}%` }}
                                        ></div>
                                      </div>
                                      <span className="font-medium">{step.confidence}%</span>
                                    </div>
                                  )}
                                </div>
                                <span className="text-xs opacity-75 ml-2">{step.processingTime}ms</span>
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
          </div>
        </div>
      </div>
    </div>
  )
}