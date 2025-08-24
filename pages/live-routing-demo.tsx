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

export default function LiveRoutingDemo() {
  const [processors, setProcessors] = useState<ProcessorHealth[]>([
    { name: 'Stripe', status: 'frozen', risk: 95, freezeResistance: 30, lastUpdate: Date.now(), issues: ['Chargeback rate: 100%', 'Refund rate: 123%'], color: '#E11D48' },
    { name: 'PayPal', status: 'healthy', risk: 15, freezeResistance: 60, lastUpdate: Date.now(), issues: [], color: '#10B981' },
    { name: 'Square', status: 'healthy', risk: 20, freezeResistance: 70, lastUpdate: Date.now(), issues: [], color: '#10B981' },
    { name: 'Visa', status: 'healthy', risk: 8, freezeResistance: 90, lastUpdate: Date.now(), issues: [], color: '#10B981' },
    { name: 'Crossmint', status: 'healthy', risk: 5, freezeResistance: 95, lastUpdate: Date.now(), issues: [], color: '#8B5CF6' }
  ])

  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isSimulating, setIsSimulating] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const intervalRef = useRef<NodeJS.Timeout>()

  // Simulate processor health changes
  const simulateProcessorHealthChanges = () => {
    setProcessors(prev => prev.map(processor => {
      // Random chance for status changes
      const rand = Math.random()
      let newStatus = processor.status
      let newRisk = processor.risk
      let issues = [...processor.issues]

      if (processor.name === 'Stripe' && rand < 0.1) {
        newStatus = newStatus === 'frozen' ? 'warning' : 'frozen'
        newRisk = newStatus === 'frozen' ? 95 : 60
        issues = newStatus === 'frozen' ? 
          ['Chargeback rate: 100%', 'Refund rate: 123%'] : 
          ['Elevated refund rate: 8%']
      } else if (processor.name !== 'Stripe' && rand < 0.05) {
        newStatus = newStatus === 'healthy' ? 'warning' : 'healthy'
        newRisk = newStatus === 'warning' ? processor.risk + 20 : Math.max(5, processor.risk - 10)
        issues = newStatus === 'warning' ? ['Temporary network issues'] : []
      }

      return {
        ...processor,
        status: newStatus as any,
        risk: newRisk,
        issues,
        lastUpdate: Date.now()
      }
    }))
  }

  // Start real-time simulation
  const startSimulation = () => {
    if (isSimulating) return
    
    setIsSimulating(true)
    
    // Health monitoring every 3 seconds
    intervalRef.current = setInterval(() => {
      simulateProcessorHealthChanges()
    }, 3000)

    // Process transactions every 5 seconds
    setTimeout(() => {
      processTestTransaction()
    }, 1000)
  }

  const stopSimulation = () => {
    setIsSimulating(false)
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
  }

  // Simulate transaction processing with real-time routing
  const processTestTransaction = async () => {
    const testTransactions = [
      { amount: 500, description: "B2B software subscription", currency: "USD" },
      { amount: 200, description: "NFT marketplace purchase", currency: "USD" },
      { amount: 1500, description: "Enterprise software license", currency: "USD" },
      { amount: 300, description: "DeFi protocol payment", currency: "USDC" },
      { amount: 75, description: "Consumer purchase", currency: "USD" }
    ]

    const transaction: Transaction = {
      id: `txn_${Date.now()}`,
      ...testTransactions[Math.floor(Math.random() * testTransactions.length)],
      status: 'routing',
      routingSteps: [],
      startTime: Date.now()
    }

    // Add transaction
    setTransactions(prev => [transaction, ...prev.slice(0, 4)])

    // Simulate Claude routing analysis
    await simulateClaudeRouting(transaction)

    // Schedule next transaction
    if (isSimulating) {
      setTimeout(processTestTransaction, Math.random() * 8000 + 5000) // 5-13 seconds
    }
  }

  const simulateClaudeRouting = async (transaction: Transaction) => {
    const steps: RoutingStep[] = []
    let stepNum = 1

    // Step 1: Analyze transaction context
    await delay(500)
    steps.push({
      step: stepNum++,
      timestamp: Date.now(),
      processor: 'Claude',
      action: 'evaluating',
      reason: `Analyzing: "${transaction.description}" - $${transaction.amount}`,
      confidence: 0,
      processingTime: 500
    })
    updateTransactionSteps(transaction.id, steps)

    // Step 2: Check processor health
    await delay(800)
    const healthyProcessors = processors.filter(p => p.status === 'healthy')
    steps.push({
      step: stepNum++,
      timestamp: Date.now(),
      processor: 'Claude',
      action: 'evaluating',
      reason: `Processor health check: ${healthyProcessors.length}/5 processors healthy`,
      confidence: 0,
      processingTime: 800
    })
    updateTransactionSteps(transaction.id, steps)

    // Step 3: Apply routing logic
    await delay(600)
    let selectedProcessor = getOptimalProcessor(transaction, processors)
    
    // If Stripe is selected but frozen, demonstrate re-routing
    if (selectedProcessor === 'Stripe' && processors.find(p => p.name === 'Stripe')?.status === 'frozen') {
      steps.push({
        step: stepNum++,
        timestamp: Date.now(),
        processor: 'Stripe',
        action: 'rejected',
        reason: 'Primary processor frozen - account freeze risk: 95%',
        confidence: 0,
        processingTime: 600
      })
      updateTransactionSteps(transaction.id, steps)

      await delay(400)
      selectedProcessor = getFallbackProcessor(transaction, processors)
      steps.push({
        step: stepNum++,
        timestamp: Date.now(),
        processor: selectedProcessor,
        action: 'fallback',
        reason: `Auto-rerouting to ${selectedProcessor} (freeze avoidance active)`,
        confidence: 92,
        processingTime: 400
      })
    } else {
      steps.push({
        step: stepNum++,
        timestamp: Date.now(),
        processor: selectedProcessor,
        action: 'selected',
        reason: getSelectionReason(selectedProcessor, transaction),
        confidence: 95,
        processingTime: 600
      })
    }
    
    updateTransactionSteps(transaction.id, steps)

    // Step 4: Finalize routing
    await delay(300)
    steps.push({
      step: stepNum++,
      timestamp: Date.now(),
      processor: selectedProcessor,
      action: 'selected',
      reason: `Payment routed to ${selectedProcessor} - processing initiated`,
      confidence: 100,
      processingTime: 300
    })
    
    // Update final transaction status
    setTransactions(prev => prev.map(txn => 
      txn.id === transaction.id ? {
        ...txn,
        status: 'completed',
        selectedProcessor,
        routingSteps: steps
      } : txn
    ))
  }

  const updateTransactionSteps = (txnId: string, steps: RoutingStep[]) => {
    setTransactions(prev => prev.map(txn => 
      txn.id === txnId ? { ...txn, routingSteps: [...steps] } : txn
    ))
  }

  const getOptimalProcessor = (transaction: Transaction, processors: ProcessorHealth[]): string => {
    // Crypto transactions -> Crossmint
    if (['nft', 'defi', 'crypto', 'web3', 'token', 'blockchain'].some(keyword => 
      transaction.description.toLowerCase().includes(keyword))) {
      return 'Crossmint'
    }
    
    // High value -> Visa
    if (transaction.amount > 1000) {
      return 'Visa'
    }
    
    // B2B -> Stripe (if healthy)
    if (transaction.description.toLowerCase().includes('b2b') || 
        transaction.description.toLowerCase().includes('enterprise')) {
      return processors.find(p => p.name === 'Stripe')?.status === 'healthy' ? 'Stripe' : 'Visa'
    }
    
    // Default -> PayPal
    return 'PayPal'
  }

  const getFallbackProcessor = (transaction: Transaction, processors: ProcessorHealth[]): string => {
    const healthy = processors.filter(p => p.status === 'healthy').sort((a, b) => b.freezeResistance - a.freezeResistance)
    
    // For crypto, prefer Crossmint
    if (['nft', 'defi', 'crypto', 'web3', 'token', 'blockchain'].some(keyword => 
      transaction.description.toLowerCase().includes(keyword))) {
      return 'Crossmint'
    }
    
    // For high amounts, prefer Visa
    if (transaction.amount > 1000) {
      return 'Visa'
    }
    
    // Otherwise, use the healthiest processor
    return healthy[0]?.name || 'PayPal'
  }

  const getSelectionReason = (processor: string, transaction: Transaction): string => {
    if (processor === 'Crossmint') return 'Web3/Crypto transaction detected'
    if (processor === 'Visa') return 'High-value enterprise transaction'
    if (processor === 'PayPal') return 'Consumer-friendly processor selected'
    if (processor === 'Square') return 'Retail/POS transaction optimized'
    return 'Default routing logic applied'
  }

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🔄 Live Payment Routing Demo
          </h1>
          <p className="text-xl text-blue-200 mb-6">
            Real-time Claude-powered payment orchestration with dynamic re-routing
          </p>
          
          <div className="flex justify-center space-x-4">
            <button
              onClick={startSimulation}
              disabled={isSimulating}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition"
            >
              {isSimulating ? '🟢 Simulation Running...' : '▶️ Start Live Demo'}
            </button>
            <button
              onClick={stopSimulation}
              disabled={!isSimulating}
              className="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition"
            >
              ⏹️ Stop Demo
            </button>
          </div>
        </div>

        {/* Processor Health Bar */}
        <div className="bg-black/20 backdrop-blur-lg rounded-2xl p-6 border border-white/20 mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">🏥 Live Processor Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {processors.map(processor => (
              <div key={processor.name} className="bg-white/10 rounded-lg p-4 border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-white">{processor.name}</h3>
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: processor.color }}
                  ></div>
                </div>
                <div className="text-sm space-y-1">
                  <p className="text-gray-300">Status: <span style={{ color: processor.color }}>{processor.status.toUpperCase()}</span></p>
                  <p className="text-gray-300">Risk: {processor.risk}%</p>
                  <p className="text-gray-300">Freeze Resist: {processor.freezeResistance}%</p>
                  {processor.issues.length > 0 && (
                    <div className="mt-2">
                      {processor.issues.map((issue, i) => (
                        <p key={i} className="text-xs text-red-300">⚠️ {issue}</p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Transaction Feed */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-4">📡 Live Transaction Feed</h2>
          
          {transactions.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <p>Start the simulation to see live routing decisions...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {transactions.map(transaction => (
                <div key={transaction.id} className="bg-white/10 rounded-lg p-4 border border-white/10">
                  {/* Transaction Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-white font-medium">{transaction.description}</h3>
                      <p className="text-sm text-gray-400">
                        ${transaction.amount} {transaction.currency} • {transaction.id}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                        transaction.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                        transaction.status === 'routing' ? 'bg-yellow-500/20 text-yellow-300' :
                        'bg-blue-500/20 text-blue-300'
                      }`}>
                        {transaction.status.toUpperCase()}
                      </div>
                      {transaction.selectedProcessor && (
                        <p className="text-sm text-blue-300 mt-1">→ {transaction.selectedProcessor}</p>
                      )}
                    </div>
                  </div>

                  {/* Routing Steps */}
                  {transaction.routingSteps.length > 0 && (
                    <div className="space-y-2">
                      {transaction.routingSteps.map(step => (
                        <div 
                          key={`${transaction.id}-${step.step}`}
                          className={`flex items-center space-x-3 p-2 rounded text-sm ${
                            step.action === 'rejected' ? 'bg-red-500/10 text-red-300' :
                            step.action === 'fallback' ? 'bg-yellow-500/10 text-yellow-300' :
                            step.action === 'selected' ? 'bg-green-500/10 text-green-300' :
                            'bg-blue-500/10 text-blue-300'
                          }`}
                        >
                          <div className="w-6 h-6 rounded-full bg-current/20 flex items-center justify-center text-xs font-bold">
                            {step.step}
                          </div>
                          <div className="flex-1">
                            <p>{step.reason}</p>
                            {step.confidence > 0 && (
                              <p className="text-xs opacity-75">Confidence: {step.confidence}%</p>
                            )}
                          </div>
                          <div className="text-xs opacity-75">
                            {step.processingTime}ms
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

        {/* Feature Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-3">⚡ Real-Time Routing</h3>
            <p className="text-blue-200">
              Watch Claude analyze transaction context and dynamically select the optimal processor in real-time.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-3">🛡️ Freeze Detection</h3>
            <p className="text-blue-200">
              Automatic detection of processor health issues with intelligent re-routing to maintain business continuity.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-3">🔄 Auto-Fallback</h3>
            <p className="text-blue-200">
              Seamless failover to backup processors when primary options become unavailable or risky.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}