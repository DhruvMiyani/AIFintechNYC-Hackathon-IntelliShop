import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { 
    count = 10, 
    pattern = 'normal', 
    delay_ms = 500 
  } = req.body

  try {
    // Connect to WebSocket and send synthetic transactions
    const WebSocket = require('ws')
    const ws = new WebSocket('ws://localhost:8080')
    
    await new Promise((resolve, reject) => {
      ws.on('open', resolve)
      ws.on('error', reject)
      setTimeout(() => reject(new Error('WebSocket connection timeout')), 5000)
    })

    // Generate synthetic transactions based on pattern
    const transactions = generateSyntheticTransactions(count, pattern)
    
    // Send transactions to WebSocket for routing
    for (const transaction of transactions) {
      const message = {
        command: 'route_transaction',
        transaction: transaction
      }
      
      ws.send(JSON.stringify(message))
      
      // Delay between transactions
      await new Promise(resolve => setTimeout(resolve, delay_ms))
    }
    
    ws.close()
    
    res.status(200).json({
      success: true,
      message: `Sent ${count} synthetic transactions for routing`,
      pattern: pattern,
      transactions_sent: count
    })
    
  } catch (error) {
    console.error('Failed to send synthetic transactions:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to connect to routing service',
      details: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}

function generateSyntheticTransactions(count: number, pattern: string) {
  const transactions = []
  
  for (let i = 0; i < count; i++) {
    let amount: number
    let description: string
    let metadata: any = {}
    
    switch (pattern) {
      case 'high_risk':
        amount = Math.random() * 5000 + 2000  // $2000-7000
        description = 'High-value transaction - Risk assessment required'
        metadata.risk_indicators = ['sudden_spike', 'unusual_amount']
        break
        
      case 'refunds':
        amount = Math.random() * 200 + 50  // $50-250
        description = i % 2 === 0 ? 'Purchase' : 'Refund requested'
        metadata.type = i % 2 === 0 ? 'charge' : 'refund'
        break
        
      case 'international':
        amount = Math.random() * 1000 + 100  // $100-1100
        description = 'International payment - Cross-border transaction'
        metadata.country = ['UK', 'FR', 'DE', 'JP', 'AU'][Math.floor(Math.random() * 5)]
        metadata.currency = ['GBP', 'EUR', 'EUR', 'JPY', 'AUD'][Math.floor(Math.random() * 5)]
        break
        
      case 'crypto':
        amount = Math.random() * 2000 + 100  // $100-2100
        description = 'Web3 payment - NFT marketplace transaction'
        metadata.payment_type = 'crypto'
        metadata.chain = ['solana', 'ethereum', 'polygon'][Math.floor(Math.random() * 3)]
        break
        
      default:  // normal
        amount = Math.random() * 300 + 20  // $20-320
        description = 'Standard e-commerce purchase'
        metadata.type = 'charge'
    }
    
    transactions.push({
      id: `syn_${Date.now()}_${i}`,
      amount: Math.round(amount * 100) / 100,
      currency: 'USD',
      description: description,
      customer_email: `customer_${Math.floor(Math.random() * 1000)}@example.com`,
      metadata: metadata,
      created: new Date().toISOString()
    })
  }
  
  return transactions
}