import type { NextApiRequest, NextApiResponse } from 'next'

interface PaymentRequest {
  amount: number
  currency: string
  description: string
  analysis_complexity: string
}

interface PaymentResponse {
  success: boolean
  processor: string
  claude_analysis: string
  decision_time_ms: number
  transaction_id?: string
  error?: string
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<PaymentResponse>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ 
      success: false, 
      processor: '', 
      claude_analysis: '',
      decision_time_ms: 0,
      error: 'Method not allowed' 
    })
  }

  const { amount, currency, description, analysis_complexity }: PaymentRequest = req.body

  try {
    // Call the real FastAPI backend
    const response = await fetch('http://localhost:8000/payments/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount,
        currency,
        description,
        analysis_complexity
      })
    })

    const backendData = await response.json()
    
    if (backendData.success) {
      res.status(200).json({
        success: true,
        processor: backendData.processor_used?.toUpperCase() || 'UNKNOWN',
        claude_analysis: backendData.reasoning || 'Claude processing completed',
        decision_time_ms: backendData.processing_time_ms || 0,
        transaction_id: backendData.payment_id
      })
    } else {
      res.status(400).json({
        success: false,
        processor: '',
        claude_analysis: '',
        decision_time_ms: 0,
        error: backendData.error || 'Payment failed'
      })
    }

  } catch (error) {
    res.status(500).json({
      success: false,
      processor: '',
      claude_analysis: '',
      decision_time_ms: 0,
      error: 'Payment processing failed'
    })
  }
}