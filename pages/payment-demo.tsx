import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import styles from '../styles/Dashboard.module.css';

interface Processor {
  id: string;
  name: string;
  fee_percentage: number;
  success_rate: number;
  supported_regions: string[];
  status?: string;
  features?: string[];
}

export default function PaymentDemo() {
  const [amount, setAmount] = useState('1000');
  const [currency, setCurrency] = useState('USDC');
  const [selectedProcessor, setSelectedProcessor] = useState<string>('');
  const [processors, setProcessors] = useState<Processor[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    loadProcessors();
  }, []);

  const loadProcessors = async () => {
    try {
      const response = await fetch('http://localhost:8000/processors');
      const data = await response.json();
      setProcessors(data.processors || []);
      console.log('Loaded processors:', data.processors);
    } catch (error) {
      console.error('Failed to load processors:', error);
    }
  };

  const processPayment = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/route-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(amount),
          currency: currency,
          merchant_id: 'demo_merchant',
          urgency: 'normal'
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Payment failed:', error);
      setResult({ error: 'Failed to process payment' });
    }
    setLoading(false);
  };

  const getProcessorIcon = (processorId: string) => {
    const icons: { [key: string]: string } = {
      'stripe': '💳',
      'paypal': '🅿️', 
      'visa': '💎',
      'crossmint': '🚀'
    };
    return icons[processorId] || '💰';
  };

  const getProcessorColor = (processorId: string) => {
    const colors: { [key: string]: string } = {
      'stripe': '#635BFF',
      'paypal': '#0070BA',
      'visa': '#1A1F71', 
      'crossmint': '#00D4FF'
    };
    return colors[processorId] || '#666666';
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Payment Demo - IntelliShop</title>
        <meta name="description" content="Demo payment interface showing Crossmint, Stripe, PayPal, and Visa" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <nav className={styles.nav}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoIcon}>💳</span>
          IntelliShop Payment Demo
        </Link>
        <div className={styles.navLinks}>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/comprehensive-insights-demo">Insights</Link>
          <span style={{ color: '#00d4ff', fontWeight: 'bold' }}>Payment Demo</span>
        </div>
      </nav>

      <main className={styles.main}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
          
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <h1 style={{ 
              color: 'white', 
              fontSize: '32px', 
              marginBottom: '10px',
              background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              🚀 Payment Processor Demo
            </h1>
            <p style={{ color: '#a0a0a0', fontSize: '16px' }}>
              Test payments with Crossmint, Stripe, PayPal, and Visa integration
            </p>
          </div>

          {/* Payment Form */}
          <div className={styles.card} style={{ marginBottom: '30px' }}>
            <h2>💰 Make a Payment</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
              <div className={styles.inputGroup}>
                <label>Amount</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className={styles.input}
                  placeholder="Enter amount"
                />
              </div>
              <div className={styles.inputGroup}>
                <label>Currency</label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className={styles.select}
                >
                  <option value="USD">USD (Stripe, PayPal, Visa)</option>
                  <option value="USDC">USDC (Crossmint)</option>
                  <option value="EUR">EUR</option>
                </select>
              </div>
            </div>
            
            <button
              onClick={processPayment}
              disabled={loading}
              className={styles.submitButton}
              style={{
                background: loading ? '#666' : 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                width: '100%',
                padding: '15px'
              }}
            >
              {loading ? 'Processing Payment...' : `Pay $${amount} ${currency}`}
            </button>
          </div>

          {/* Available Processors */}
          <div className={styles.card} style={{ marginBottom: '30px' }}>
            <h2>🏦 Available Payment Processors</h2>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
              gap: '20px',
              marginTop: '20px'
            }}>
              {processors.map((processor) => (
                <div
                  key={processor.id}
                  style={{
                    background: `linear-gradient(135deg, ${getProcessorColor(processor.id)}15, rgba(255,255,255,0.05))`,
                    border: `2px solid ${getProcessorColor(processor.id)}40`,
                    borderRadius: '12px',
                    padding: '20px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    ':hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 10px 30px ${getProcessorColor(processor.id)}30`
                    }
                  }}
                  onClick={() => setSelectedProcessor(processor.id)}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    marginBottom: '15px'
                  }}>
                    <span style={{ fontSize: '32px', marginRight: '12px' }}>
                      {getProcessorIcon(processor.id)}
                    </span>
                    <div>
                      <h3 style={{ 
                        color: 'white', 
                        margin: 0, 
                        fontSize: '18px' 
                      }}>
                        {processor.name}
                      </h3>
                      <span style={{ 
                        color: getProcessorColor(processor.id), 
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {processor.id.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  
                  <div style={{ color: '#e0e0e0', fontSize: '14px', marginBottom: '15px' }}>
                    <div>💰 Fee: <strong style={{ color: getProcessorColor(processor.id) }}>
                      {processor.fee_percentage}%
                    </strong></div>
                    <div>✅ Success Rate: <strong style={{ color: '#00ff88' }}>
                      {(processor.success_rate * 100).toFixed(1)}%
                    </strong></div>
                    <div>🌍 Regions: <strong>{processor.supported_regions.join(', ')}</strong></div>
                  </div>

                  {processor.id === 'crossmint' && (
                    <div style={{
                      background: 'linear-gradient(45deg, #00d4ff20, #ff6b3520)',
                      border: '1px solid #00d4ff40',
                      borderRadius: '8px',
                      padding: '10px',
                      marginTop: '10px'
                    }}>
                      <div style={{ 
                        color: '#00d4ff', 
                        fontSize: '12px', 
                        fontWeight: 'bold',
                        marginBottom: '5px'
                      }}>
                        🚀 CRYPTO PAYMENTS
                      </div>
                      <div style={{ color: '#e0e0e0', fontSize: '11px' }}>
                        • USDC stablecoin support<br />
                        • Arbitrum & Polygon networks<br />
                        • Instant settlement<br />
                        • Lowest fees in market
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Results */}
          {result && (
            <div className={styles.card}>
              <h2>📋 Payment Result</h2>
              {result.error ? (
                <div style={{ 
                  color: '#ff4757', 
                  background: 'rgba(255,71,87,0.1)',
                  border: '1px solid #ff4757',
                  borderRadius: '8px',
                  padding: '15px'
                }}>
                  ❌ Error: {result.error}
                </div>
              ) : (
                <div>
                  <div style={{
                    background: 'rgba(0,255,136,0.1)',
                    border: '1px solid #00ff88',
                    borderRadius: '8px',
                    padding: '20px',
                    marginBottom: '20px'
                  }}>
                    <h3 style={{ color: '#00ff88', margin: '0 0 10px 0' }}>
                      ✅ Payment Processed Successfully
                    </h3>
                    <div style={{ color: 'white', fontSize: '14px' }}>
                      <p><strong>Selected Processor:</strong> {result.routing_decision?.selected_processor}</p>
                      <p><strong>Confidence:</strong> {(result.routing_decision?.confidence * 100).toFixed(1)}%</p>
                      <p><strong>Processing Time:</strong> {result.routing_decision?.decision_time_ms.toFixed(0)}ms</p>
                    </div>
                  </div>

                  {/* Processor Comparison */}
                  <div style={{ marginTop: '20px' }}>
                    <h3 style={{ color: 'white', marginBottom: '15px' }}>🏆 Processor Comparison</h3>
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                      gap: '15px' 
                    }}>
                      {result.processor_comparison?.map((proc: any, index: number) => (
                        <div
                          key={proc.id}
                          style={{
                            background: proc.id === result.routing_decision?.selected_processor 
                              ? 'rgba(0,255,136,0.1)' 
                              : 'rgba(255,255,255,0.05)',
                            border: proc.id === result.routing_decision?.selected_processor
                              ? '2px solid #00ff88'
                              : '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            padding: '12px',
                            position: 'relative'
                          }}
                        >
                          {proc.id === result.routing_decision?.selected_processor && (
                            <div style={{
                              position: 'absolute',
                              top: '-8px',
                              right: '-8px',
                              background: '#00ff88',
                              color: 'black',
                              borderRadius: '50%',
                              width: '24px',
                              height: '24px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '12px',
                              fontWeight: 'bold'
                            }}>
                              ✓
                            </div>
                          )}
                          
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            marginBottom: '8px'
                          }}>
                            <span style={{ marginRight: '8px' }}>
                              {getProcessorIcon(proc.id)}
                            </span>
                            <strong style={{ color: 'white', fontSize: '14px' }}>
                              {proc.name}
                            </strong>
                          </div>
                          
                          <div style={{ color: '#a0a0a0', fontSize: '12px' }}>
                            <div>Fee: {proc.original_fee}%</div>
                            <div>Success: {(proc.success_rate * 100).toFixed(1)}%</div>
                            <div>Priority: {proc.priority_score.toFixed(2)}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Footer */}
          <div style={{ 
            textAlign: 'center', 
            marginTop: '40px', 
            padding: '20px', 
            color: '#666' 
          }}>
            <p>🚀 Crossmint integration complete! Try USDC payments to see crypto processing in action.</p>
            <div style={{ marginTop: '10px' }}>
              <span style={{ color: '#00d4ff' }}>Crossmint: 1.5% fees</span> • 
              <span style={{ color: '#635BFF' }}> Stripe: 2.9% fees</span> • 
              <span style={{ color: '#0070BA' }}> PayPal: 3.49% fees</span> • 
              <span style={{ color: '#1A1F71' }}> Visa: 2.5% fees</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}