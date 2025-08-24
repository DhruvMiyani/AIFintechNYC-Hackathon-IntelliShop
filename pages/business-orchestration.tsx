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

interface BusinessScenario {
  id: string;
  name: string;
  description: string;
  amount: number;
  currency: string;
  business_type: string;
  urgency: string;
  customer_region: string;
}

export default function BusinessOrchestration() {
  const [processors, setProcessors] = useState<Processor[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<BusinessScenario>({
    id: 'ecommerce_checkout',
    name: 'E-commerce Checkout',
    description: 'Customer purchasing products from online store',
    amount: 150,
    currency: 'USD',
    business_type: 'ecommerce',
    urgency: 'normal',
    customer_region: 'US'
  });
  const [recommendedProcessor, setRecommendedProcessor] = useState<string>('');
  const [recommendation, setRecommendation] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [realTimeAnalysis, setRealTimeAnalysis] = useState<any>(null);

  const businessScenarios: BusinessScenario[] = [
    {
      id: 'ecommerce_checkout',
      name: 'E-commerce Checkout',
      description: 'Customer purchasing products from online store',
      amount: 150,
      currency: 'USD',
      business_type: 'ecommerce',
      urgency: 'normal',
      customer_region: 'US'
    },
    {
      id: 'crypto_purchase',
      name: 'Crypto/NFT Purchase', 
      description: 'Customer buying NFTs or crypto-related products',
      amount: 500,
      currency: 'USDC',
      business_type: 'crypto_native',
      urgency: 'normal',
      customer_region: 'GLOBAL'
    },
    {
      id: 'subscription_payment',
      name: 'Subscription Payment',
      description: 'Monthly subscription renewal',
      amount: 29,
      currency: 'USD', 
      business_type: 'saas',
      urgency: 'low',
      customer_region: 'EU'
    },
    {
      id: 'high_value_b2b',
      name: 'High-Value B2B',
      description: 'Enterprise software license purchase',
      amount: 5000,
      currency: 'USD',
      business_type: 'enterprise',
      urgency: 'high',
      customer_region: 'US'
    }
  ];

  useEffect(() => {
    loadProcessors();
    getRecommendation();
  }, [selectedScenario]);

  const loadProcessors = async () => {
    try {
      const response = await fetch('http://localhost:8000/processors');
      const data = await response.json();
      setProcessors(data.processors || []);
    } catch (error) {
      console.error('Failed to load processors:', error);
    }
  };

  const getRecommendation = async () => {
    setLoading(true);
    try {
      // Get AI recommendation for this business scenario
      const response = await fetch('http://localhost:8000/route-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: selectedScenario.amount,
          currency: selectedScenario.currency,
          merchant_id: 'business_merchant',
          urgency: selectedScenario.urgency,
          business_type: selectedScenario.business_type
        })
      });
      const data = await response.json();
      setRecommendation(data);
      setRecommendedProcessor(data.routing_decision?.selected_processor || '');
    } catch (error) {
      console.error('Failed to get recommendation:', error);
    }
    setLoading(false);
  };

  const getCompetitiveAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:8000/competitive-analysis');
      const data = await response.json();
      setRealTimeAnalysis(data);
    } catch (error) {
      console.error('Failed to get competitive analysis:', error);
    }
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

  const getRecommendationReason = () => {
    if (!recommendation || !recommendedProcessor) return '';
    
    const selected = processors.find(p => p.id === recommendedProcessor);
    if (!selected) return '';

    if (recommendedProcessor === 'crossmint') {
      return 'Lowest fees (1.5%) and highest success rate (99.2%). Perfect for crypto-native customers.';
    } else if (recommendedProcessor === 'stripe') {
      return 'Reliable processing with good developer tools and wide currency support.';
    } else if (recommendedProcessor === 'visa') {
      return 'High success rate and enterprise-grade security for large transactions.';
    } else if (recommendedProcessor === 'paypal') {
      return 'Familiar to customers and good for international payments.';
    }
    return 'AI-selected based on current market conditions.';
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Business Payment Orchestration - IntelliShop</title>
        <meta name="description" content="AI-powered payment gateway selection for businesses" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <nav className={styles.nav}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoIcon}>🏢</span>
          IntelliShop Business
        </Link>
        <div className={styles.navLinks}>
          <Link href="/dashboard">Analytics</Link>
          <Link href="/comprehensive-insights-demo">Market Intel</Link>
          <span style={{ color: '#00d4ff', fontWeight: 'bold' }}>Orchestration</span>
        </div>
      </nav>

      <main className={styles.main}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
          
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <h1 style={{ 
              color: 'white', 
              fontSize: '36px', 
              marginBottom: '10px',
              background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              🏢 Business Payment Orchestration
            </h1>
            <p style={{ color: '#a0a0a0', fontSize: '18px', maxWidth: '600px', margin: '0 auto' }}>
              AI-powered gateway selection system. Choose the optimal payment processor for each transaction scenario in real-time.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginBottom: '30px' }}>
            
            {/* Business Scenario Selection */}
            <div className={styles.card}>
              <h2>🎯 Business Scenario</h2>
              <p style={{ color: '#a0a0a0', marginBottom: '20px' }}>
                Select your business scenario to get AI-powered gateway recommendations
              </p>
              
              <div style={{ marginBottom: '20px' }}>
                {businessScenarios.map((scenario) => (
                  <div
                    key={scenario.id}
                    onClick={() => setSelectedScenario(scenario)}
                    style={{
                      background: selectedScenario.id === scenario.id 
                        ? 'linear-gradient(45deg, #00d4ff20, #ff6b3520)' 
                        : 'rgba(255,255,255,0.05)',
                      border: selectedScenario.id === scenario.id
                        ? '2px solid #00d4ff'
                        : '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                      padding: '15px',
                      marginBottom: '10px',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <div style={{ 
                      color: selectedScenario.id === scenario.id ? '#00d4ff' : 'white',
                      fontWeight: 'bold',
                      marginBottom: '5px'
                    }}>
                      {scenario.name}
                    </div>
                    <div style={{ color: '#a0a0a0', fontSize: '14px', marginBottom: '8px' }}>
                      {scenario.description}
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      gap: '15px', 
                      fontSize: '12px',
                      color: selectedScenario.id === scenario.id ? '#00d4ff' : '#666'
                    }}>
                      <span>💰 ${scenario.amount} {scenario.currency}</span>
                      <span>🏢 {scenario.business_type}</span>
                      <span>🌍 {scenario.customer_region}</span>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={getCompetitiveAnalysis}
                className={styles.agentButton}
                style={{ width: '100%' }}
              >
                📊 Get Real-Time Market Analysis
              </button>
            </div>

            {/* AI Recommendation */}
            <div className={styles.card}>
              <h2>🤖 AI Gateway Recommendation</h2>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#00d4ff' }}>
                  <div style={{ fontSize: '18px', marginBottom: '10px' }}>
                    🤖 Analyzing optimal gateway...
                  </div>
                  <div style={{ fontSize: '14px', opacity: 0.7 }}>
                    Considering fees, success rates, and market conditions
                  </div>
                </div>
              ) : recommendedProcessor ? (
                <div>
                  {/* Recommended Processor */}
                  <div style={{
                    background: `linear-gradient(135deg, ${getProcessorColor(recommendedProcessor)}20, rgba(0,255,136,0.1))`,
                    border: `2px solid ${getProcessorColor(recommendedProcessor)}`,
                    borderRadius: '12px',
                    padding: '25px',
                    marginBottom: '20px',
                    position: 'relative'
                  }}>
                    <div style={{
                      position: 'absolute',
                      top: '-10px',
                      right: '20px',
                      background: '#00ff88',
                      color: 'black',
                      padding: '5px 15px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}>
                      RECOMMENDED
                    </div>
                    
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                      <span style={{ fontSize: '48px', marginRight: '20px' }}>
                        {getProcessorIcon(recommendedProcessor)}
                      </span>
                      <div>
                        <h3 style={{ color: 'white', margin: 0, fontSize: '24px' }}>
                          {processors.find(p => p.id === recommendedProcessor)?.name}
                        </h3>
                        <div style={{ color: getProcessorColor(recommendedProcessor), fontSize: '14px' }}>
                          {recommendedProcessor.toUpperCase()} • OPTIMAL CHOICE
                        </div>
                      </div>
                    </div>

                    <div style={{ color: '#e0e0e0', fontSize: '15px', marginBottom: '15px' }}>
                      {getRecommendationReason()}
                    </div>

                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(3, 1fr)', 
                      gap: '15px',
                      marginBottom: '20px'
                    }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ color: '#00ff88', fontSize: '20px', fontWeight: 'bold' }}>
                          {processors.find(p => p.id === recommendedProcessor)?.fee_percentage}%
                        </div>
                        <div style={{ color: '#a0a0a0', fontSize: '12px' }}>Fee Rate</div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ color: '#00ff88', fontSize: '20px', fontWeight: 'bold' }}>
                          {((processors.find(p => p.id === recommendedProcessor)?.success_rate || 0) * 100).toFixed(1)}%
                        </div>
                        <div style={{ color: '#a0a0a0', fontSize: '12px' }}>Success Rate</div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ color: '#00ff88', fontSize: '20px', fontWeight: 'bold' }}>
                          {(recommendation?.routing_decision?.confidence * 100).toFixed(0)}%
                        </div>
                        <div style={{ color: '#a0a0a0', fontSize: '12px' }}>AI Confidence</div>
                      </div>
                    </div>

                    <div style={{
                      background: 'rgba(0,0,0,0.3)',
                      borderRadius: '8px',
                      padding: '15px'
                    }}>
                      <div style={{ color: '#00d4ff', fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>
                        💡 Implementation Instructions:
                      </div>
                      <div style={{ color: '#e0e0e0', fontSize: '13px' }}>
                        • Configure your checkout to use <strong>{processors.find(p => p.id === recommendedProcessor)?.name}</strong><br />
                        • Expected transaction cost: <strong>${(selectedScenario.amount * ((processors.find(p => p.id === recommendedProcessor)?.fee_percentage || 0) / 100)).toFixed(2)}</strong><br />
                        • Estimated processing time: <strong>&lt;3 seconds</strong><br />
                        • Success probability: <strong>{((processors.find(p => p.id === recommendedProcessor)?.success_rate || 0) * 100).toFixed(1)}%</strong>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={getRecommendation}
                    className={styles.submitButton}
                    style={{ width: '100%' }}
                  >
                    🔄 Refresh AI Recommendation
                  </button>
                </div>
              ) : null}
            </div>
          </div>

          {/* All Available Processors Comparison */}
          <div className={styles.card} style={{ marginBottom: '30px' }}>
            <h2>⚖️ Gateway Performance Comparison</h2>
            <p style={{ color: '#a0a0a0', marginBottom: '25px' }}>
              Current market analysis of all available payment gateways for your business
            </p>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
              gap: '20px' 
            }}>
              {processors.map((processor) => {
                const isRecommended = processor.id === recommendedProcessor;
                const comparisonData = recommendation?.processor_comparison?.find((p: any) => p.id === processor.id);
                
                return (
                  <div
                    key={processor.id}
                    style={{
                      background: isRecommended 
                        ? `linear-gradient(135deg, ${getProcessorColor(processor.id)}20, rgba(0,255,136,0.1))`
                        : 'rgba(255,255,255,0.05)',
                      border: isRecommended
                        ? `2px solid ${getProcessorColor(processor.id)}`
                        : '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '12px',
                      padding: '20px',
                      position: 'relative',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    {isRecommended && (
                      <div style={{
                        position: 'absolute',
                        top: '-8px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        background: '#00ff88',
                        color: 'black',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 'bold'
                      }}>
                        AI SELECTED
                      </div>
                    )}
                    
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                      <span style={{ fontSize: '32px', marginRight: '12px' }}>
                        {getProcessorIcon(processor.id)}
                      </span>
                      <div>
                        <h3 style={{ color: 'white', margin: 0, fontSize: '18px' }}>
                          {processor.name}
                        </h3>
                        <span style={{ color: getProcessorColor(processor.id), fontSize: '12px', fontWeight: 'bold' }}>
                          {processor.id.toUpperCase()}
                        </span>
                      </div>
                    </div>

                    <div style={{ marginBottom: '15px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ color: '#a0a0a0', fontSize: '14px' }}>Processing Fee</span>
                        <span style={{ color: getProcessorColor(processor.id), fontWeight: 'bold' }}>
                          {processor.fee_percentage}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ color: '#a0a0a0', fontSize: '14px' }}>Success Rate</span>
                        <span style={{ color: '#00ff88', fontWeight: 'bold' }}>
                          {(processor.success_rate * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ color: '#a0a0a0', fontSize: '14px' }}>Cost for ${selectedScenario.amount}</span>
                        <span style={{ color: 'white', fontWeight: 'bold' }}>
                          ${(selectedScenario.amount * (processor.fee_percentage / 100)).toFixed(2)}
                        </span>
                      </div>
                      {comparisonData && (
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: '#a0a0a0', fontSize: '14px' }}>AI Priority Score</span>
                          <span style={{ color: '#00d4ff', fontWeight: 'bold' }}>
                            {comparisonData.priority_score?.toFixed(2) || 'N/A'}
                          </span>
                        </div>
                      )}
                    </div>

                    <div style={{ fontSize: '12px', color: '#666' }}>
                      🌍 {processor.supported_regions.join(', ')}
                    </div>

                    {processor.id === 'crossmint' && (
                      <div style={{
                        background: 'linear-gradient(45deg, #00d4ff10, #ff6b3510)',
                        border: '1px solid #00d4ff30',
                        borderRadius: '6px',
                        padding: '8px',
                        marginTop: '10px'
                      }}>
                        <div style={{ color: '#00d4ff', fontSize: '11px', fontWeight: 'bold' }}>
                          🚀 CRYPTO ADVANTAGE
                        </div>
                        <div style={{ color: '#e0e0e0', fontSize: '10px' }}>
                          USDC payments, instant settlement, lowest fees
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Real-time Market Analysis */}
          {realTimeAnalysis && (
            <div className={styles.card}>
              <h2>📊 Real-Time Market Analysis</h2>
              <div style={{ 
                background: 'rgba(0,212,255,0.1)',
                border: '1px solid rgba(0,212,255,0.3)',
                borderRadius: '8px',
                padding: '20px'
              }}>
                <div style={{ color: '#00d4ff', fontSize: '14px', marginBottom: '15px' }}>
                  🔴 LIVE: {realTimeAnalysis.data_source?.source === 'brave_search_api' ? 'Brave Search API Data' : 'High-Quality Synthetic Data'}
                </div>
                <div style={{ color: 'white', fontSize: '14px' }}>
                  Market conditions updated in real-time to optimize gateway selection for your business scenario.
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}