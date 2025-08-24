import type { NextApiRequest, NextApiResponse } from 'next'

interface CrossmintRequest {
  amount: number
  currency: string
  chain: string
  customer_email: string
  description: string
  analysis_complexity: string
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const {
    amount,
    currency,
    chain,
    customer_email,
    description,
    analysis_complexity
  }: CrossmintRequest = req.body

  try {
    // Call the Python FastAPI backend
    const response = await fetch('http://localhost:8000/payments/crossmint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount,
        currency,
        chain,
        customer_email,
        description,
        analysis_complexity
      })
    })

    const data = await response.json()

    if (response.ok) {
      res.status(200).json(data)
    } else {
      res.status(400).json({
        success: false,
        error: data.error || 'Crossmint payment failed'
      })
    }

  } catch (error) {
    console.error('Crossmint API error:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to process Crossmint payment'
    })
  }
}