import { useState } from 'react'

interface CrossmintPayment {
  amount: number
  currency: string
  chain: string
  customerEmail: string
  description: string
  analysisComplexity: 'simple' | 'balanced' | 'comprehensive'
}

interface CrossmintResult {
  success: boolean
  processor_used?: string
  transaction_id?: string
  wallet_address?: string
  explorer_link?: string
  chain?: string
  currency?: string
  processing_time_ms?: number
  crossmint_features?: any
  wallet_info?: any
  processor_capabilities?: any
  claude_analysis?: any
  error?: string
}

export default function CrossmintDemo() {
  const [payment, setPayment] = useState<CrossmintPayment>({
    amount: 100,
    currency: 'usdc',
    chain: 'solana',
    customerEmail: 'demo@web3user.com',
    description: 'NFT marketplace purchase',
    analysisComplexity: 'comprehensive'
  })
  const [result, setResult] = useState<CrossmintResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [processorInfo, setProcessorInfo] = useState<any>(null)

  const handlePayment = async () => {
    setLoading(true)
    setResult(null)

    try {
      const response = await fetch('/api/crossmint/payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: payment.amount,
          currency: payment.currency,
          chain: payment.chain,
          customer_email: payment.customerEmail,
          description: payment.description,
          analysis_complexity: payment.analysisComplexity
        })
      })

      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({
        success: false,
        error: 'Failed to process Crossmint payment'
      })
    }

    setLoading(false)
  }

  const loadProcessorInfo = async () => {
    try {
      const response = await fetch('http://localhost:8000/payments/crossmint/info')
      const data = await response.json()
      setProcessorInfo(data)
    } catch (error) {
      console.error('Failed to load processor info:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🌐 Crossmint Wallets Integration
          </h1>
          <p className="text-xl text-blue-200">
            Web3 Payment Processing with Multi-Chain Wallet Support
          </p>
          <div className="flex justify-center space-x-4 mt-4">
            <span className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm">
              Solana ◉
            </span>
            <span className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm">
              Ethereum ⟡
            </span>
            <span className="px-3 py-1 bg-indigo-600 text-white rounded-full text-sm">
              Polygon ⬟
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Payment Form */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h2 className="text-2xl font-bold text-white mb-4">💰 Crypto Payment</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Amount
                </label>
                <input
                  type="number"
                  value={payment.amount}
                  onChange={(e) => setPayment({...payment, amount: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300"
                  placeholder="100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Currency
                </label>
                <select
                  value={payment.currency}
                  onChange={(e) => setPayment({...payment, currency: e.target.value})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                >
                  <option value="usdc">USDC</option>
                  <option value="sol">SOL</option>
                  <option value="eth">ETH</option>
                  <option value="matic">MATIC</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Chain
                </label>
                <select
                  value={payment.chain}
                  onChange={(e) => setPayment({...payment, chain: e.target.value})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                >
                  <option value="solana">Solana</option>
                  <option value="ethereum">Ethereum</option>
                  <option value="polygon">Polygon</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Customer Email
                </label>
                <input
                  type="email"
                  value={payment.customerEmail}
                  onChange={(e) => setPayment({...payment, customerEmail: e.target.value})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300"
                  placeholder="user@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Description
                </label>
                <select
                  value={payment.description}
                  onChange={(e) => setPayment({...payment, description: e.target.value})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                >
                  <option value="NFT marketplace purchase">NFT marketplace purchase</option>
                  <option value="DeFi protocol payment">DeFi protocol payment</option>
                  <option value="Web3 gaming token purchase">Web3 gaming token purchase</option>
                  <option value="Crypto wallet transfer">Crypto wallet transfer</option>
                  <option value="Blockchain service payment">Blockchain service payment</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-200 mb-2">
                  Analysis Complexity
                </label>
                <select
                  value={payment.analysisComplexity}
                  onChange={(e) => setPayment({...payment, analysisComplexity: e.target.value as any})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                >
                  <option value="simple">Simple</option>
                  <option value="balanced">Balanced</option>
                  <option value="comprehensive">Comprehensive</option>
                </select>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handlePayment}
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-lg transition duration-300"
                >
                  {loading ? 'Processing...' : '🚀 Process Payment'}
                </button>
                
                <button
                  onClick={loadProcessorInfo}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300"
                >
                  📋 Info
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h2 className="text-2xl font-bold text-white mb-4">📊 Results</h2>
            
            {result && (
              <div className="space-y-4">
                {result.success ? (
                  <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-4">
                    <h3 className="text-lg font-bold text-green-300 mb-2">✅ Payment Successful</h3>
                    <div className="text-sm text-green-200 space-y-1">
                      <p><strong>Processor:</strong> {result.processor_used?.toUpperCase()}</p>
                      <p><strong>Transaction ID:</strong> {result.transaction_id}</p>
                      <p><strong>Wallet:</strong> {result.wallet_address}</p>
                      <p><strong>Chain:</strong> {result.chain}</p>
                      <p><strong>Currency:</strong> {result.currency}</p>
                      <p><strong>Processing Time:</strong> {result.processing_time_ms}ms</p>
                      {result.explorer_link && (
                        <p>
                          <strong>Explorer:</strong>{' '}
                          <a 
                            href={result.explorer_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-300 hover:text-blue-200 underline"
                          >
                            View Transaction
                          </a>
                        </p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                    <h3 className="text-lg font-bold text-red-300 mb-2">❌ Payment Failed</h3>
                    <p className="text-sm text-red-200">{result.error}</p>
                  </div>
                )}

                {/* Crossmint Features */}
                {result.crossmint_features && (
                  <div className="bg-purple-500/20 border border-purple-500/50 rounded-lg p-4">
                    <h3 className="text-lg font-bold text-purple-300 mb-2">🌟 Crossmint Features</h3>
                    <div className="text-sm text-purple-200 space-y-1">
                      {Object.entries(result.crossmint_features).map(([key, value]) => (
                        <p key={key}>
                          <strong>{key.replace(/_/g, ' ')}:</strong> {value ? '✅' : '❌'}
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Wallet Info */}
                {result.wallet_info && (
                  <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-4">
                    <h3 className="text-lg font-bold text-blue-300 mb-2">💳 Wallet Info</h3>
                    <div className="text-sm text-blue-200 space-y-1">
                      <p><strong>Address:</strong> {result.wallet_info.address}</p>
                      <p><strong>Chain:</strong> {result.wallet_info.chain}</p>
                      {result.wallet_info.balances && (
                        <div>
                          <strong>Balances:</strong>
                          <div className="ml-4 mt-1">
                            {result.wallet_info.balances.native_token && (
                              <p>• {result.wallet_info.balances.native_token.symbol}: {result.wallet_info.balances.native_token.amount}</p>
                            )}
                            {result.wallet_info.balances.usdc && (
                              <p>• {result.wallet_info.balances.usdc.symbol}: {result.wallet_info.balances.usdc.amount}</p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Claude Analysis */}
                {result.claude_analysis && (
                  <div className="bg-indigo-500/20 border border-indigo-500/50 rounded-lg p-4">
                    <h3 className="text-lg font-bold text-indigo-300 mb-2">🤖 Claude Analysis</h3>
                    <div className="text-sm text-indigo-200 space-y-1">
                      <p><strong>Routing Reason:</strong> {result.claude_analysis.routing_reason}</p>
                      <p><strong>Confidence:</strong> {Math.round(result.claude_analysis.confidence * 100)}%</p>
                      <p><strong>Processor Health:</strong> {result.claude_analysis.processor_health}</p>
                      <p><strong>Decentralized Advantage:</strong> {result.claude_analysis.decentralized_advantage ? '✅' : '❌'}</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Processor Info */}
            {processorInfo && (
              <div className="mt-6 bg-gray-500/20 border border-gray-500/50 rounded-lg p-4">
                <h3 className="text-lg font-bold text-gray-300 mb-2">📋 Processor Information</h3>
                <div className="text-sm text-gray-200 space-y-2">
                  <p><strong>Name:</strong> {processorInfo.processor?.processor_name}</p>
                  <p><strong>Type:</strong> {processorInfo.processor?.type}</p>
                  <p><strong>Chains:</strong> {processorInfo.processor?.supported_chains?.join(', ')}</p>
                  <p><strong>Currencies:</strong> {processorInfo.processor?.supported_currencies?.join(', ')}</p>
                  <p><strong>Freeze Resistance:</strong> {Math.round((processorInfo.processor?.freeze_resistance || 0) * 100)}%</p>
                  <p><strong>Max Amount:</strong> ${(processorInfo.processor?.max_amount || 0).toLocaleString()}</p>
                  <p><strong>SDK Version:</strong> {processorInfo.sdk_version}</p>
                  <p><strong>Status:</strong> {processorInfo.integration_status}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-3">🔗 Multi-Chain Support</h3>
            <p className="text-blue-200">
              Support for Solana, Ethereum, and Polygon networks with native token and USDC transfers.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-3">📧 Email-Based Wallets</h3>
            <p className="text-blue-200">
              Create and manage wallets using email addresses - no seed phrases or private key management required.
            </p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-3">🌍 Global Access</h3>
            <p className="text-blue-200">
              Decentralized payments with 95% freeze resistance and instant cross-border transactions.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}