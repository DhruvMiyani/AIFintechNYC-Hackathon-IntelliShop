import React, { useState, useEffect } from 'react';
import styles from '../styles/Dashboard.module.css';

interface CompetitiveData {
  [key: string]: {
    market_position: string;
    competitive_advantage: string;
    compared_processors: string[];
    pricing_comparison: { [key: string]: number };
    feature_comparison: { [key: string]: boolean };
  };
}

interface MarketIntelligence {
  fraud_trends: { [key: string]: { total_threats: number; high_risk_threats: number; risk_level: string } };
  service_health: { [key: string]: { operational_services: string; average_uptime: number; health_status: string } };
  market_sentiment: { [key: string]: { average_sentiment: number; sentiment_category: string; total_mentions: number } };
  news_impact: { [key: string]: { high_impact_news: number; average_market_impact: number; impact_trend: string } };
  performance_rankings: { [key: string]: { average_score: number; average_percentile: number; ranking: string } };
}

interface SyntheticTransactionSummary {
  total_count: number;
  business_type_used: string;
  risk_distribution: { [key: string]: number };
  average_amount: number;
}

export default function ComprehensiveInsightsDemo() {
  const [activeTab, setActiveTab] = useState('routing');
  const [competitiveData, setCompetitiveData] = useState<CompetitiveData | null>(null);
  const [marketIntelligence, setMarketIntelligence] = useState<MarketIntelligence | null>(null);
  const [syntheticData, setSyntheticData] = useState<SyntheticTransactionSummary | null>(null);
  const [scenarioResults, setScenarioResults] = useState<any>(null);
  const [processorInsights, setProcessorInsights] = useState<any>(null);
  const [selectedProcessor, setSelectedProcessor] = useState('stripe');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load initial data
    loadCompetitiveAnalysis();
    loadMarketIntelligence();
  }, []);

  const loadCompetitiveAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:8000/competitive-analysis');
      const data = await response.json();
      setCompetitiveData(data.competitive_analysis);
    } catch (error) {
      console.error('Failed to load competitive analysis:', error);
    }
  };

  const loadMarketIntelligence = async () => {
    try {
      const response = await fetch('http://localhost:8000/market-intelligence');
      const data = await response.json();
      setMarketIntelligence(data.market_intelligence);
    } catch (error) {
      console.error('Failed to load market intelligence:', error);
    }
  };

  const generateSyntheticData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/synthetic-data/transactions?count=50&business_type=startup_tech', {
        method: 'POST'
      });
      const data = await response.json();
      setSyntheticData(data.summary);
    } catch (error) {
      console.error('Failed to generate synthetic data:', error);
    }
    setLoading(false);
  };

  const runScenarioTests = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/scenario-testing', {
        method: 'POST'
      });
      const data = await response.json();
      setScenarioResults(data.scenario_results);
    } catch (error) {
      console.error('Failed to run scenario tests:', error);
    }
    setLoading(false);
  };

  const loadProcessorInsights = async (processorId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/comprehensive-insights/${processorId}`);
      const data = await response.json();
      setProcessorInsights(data);
    } catch (error) {
      console.error('Failed to load processor insights:', error);
    }
    setLoading(false);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'excellent': case 'operational': case 'positive': case 'leader': case 'top_tier':
        return '#28a745';
      case 'good': case 'strong': case 'neutral': case 'challenger':
        return '#ffc107';
      case 'concerning': case 'negative': case 'high': case 'follower': case 'average':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const getRiskBadgeColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return '#28a745';
      case 'medium': return '#ffc107';
      case 'high': return '#fd7e14';
      case 'critical': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🚀 Comprehensive Brave Search Integration Demo</h1>
        <p>Advanced payment orchestration with real-time market intelligence</p>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', marginBottom: '2rem', borderBottom: '1px solid #ddd' }}>
        {[
          { id: 'routing', label: '🎯 Smart Routing', icon: '🎯' },
          { id: 'competitive', label: '🏆 Competitive Analysis', icon: '🏆' },
          { id: 'intelligence', label: '📊 Market Intelligence', icon: '📊' },
          { id: 'synthetic', label: '🧪 Synthetic Data', icon: '🧪' },
          { id: 'scenarios', label: '🔬 Scenario Testing', icon: '🔬' },
          { id: 'insights', label: '🔍 Deep Insights', icon: '🔍' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '1rem 1.5rem',
              border: 'none',
              borderBottom: activeTab === tab.id ? '3px solid #0070f3' : '3px solid transparent',
              background: activeTab === tab.id ? '#f8f9fa' : 'transparent',
              cursor: 'pointer',
              fontWeight: activeTab === tab.id ? 'bold' : 'normal'
            }}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Smart Routing Tab */}
      {activeTab === 'routing' && (
        <div className={styles.card}>
          <h2>🎯 Intelligent Payment Routing</h2>
          <p>Test our enhanced routing system with real-time insights</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            {[
              {
                title: '🎯 Simple Routing',
                description: 'Fast routing for small transactions',
                endpoint: '/route-payment',
                payload: { amount: 25, complexity: 'simple', test_insights: false }
              },
              {
                title: '💎 Premium Analysis', 
                description: 'Comprehensive insights for high-value payments',
                endpoint: '/route-payment',
                payload: { amount: 5000, complexity: 'comprehensive', test_insights: true }
              },
              {
                title: '⚡ Urgent Processing',
                description: 'Time-sensitive payments with balanced insights',
                endpoint: '/route-payment',
                payload: { amount: 1500, urgency: 'high', complexity: 'balanced', test_insights: true }
              }
            ].map((scenario, index) => (
              <div key={index} style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '0.5rem' }}>
                <h3 style={{ margin: '0 0 0.5rem 0' }}>{scenario.title}</h3>
                <p style={{ fontSize: '0.9rem', color: '#666', margin: '0 0 1rem 0' }}>{scenario.description}</p>
                <button
                  onClick={async () => {
                    setLoading(true);
                    try {
                      const response = await fetch(`http://localhost:8000${scenario.endpoint}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ merchant_id: 'demo_merchant', ...scenario.payload })
                      });
                      const result = await response.json();
                      alert(`Selected: ${result.routing_decision?.selected_processor}\nReasoning: ${result.routing_decision?.reasoning?.substring(0, 100)}...`);
                    } catch (error) {
                      alert(`Error: ${error.message}`);
                    }
                    setLoading(false);
                  }}
                  disabled={loading}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#0070f3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.25rem',
                    cursor: 'pointer'
                  }}
                >
                  Test Routing
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Competitive Analysis Tab */}
      {activeTab === 'competitive' && (
        <div className={styles.card}>
          <h2>🏆 Competitive Analysis Dashboard</h2>
          <button onClick={loadCompetitiveAnalysis} style={{ marginBottom: '1rem', padding: '0.5rem 1rem', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '0.25rem' }}>
            🔄 Refresh Analysis
          </button>
          
          {competitiveData && (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                {Object.entries(competitiveData).map(([processor, data]) => (
                  <div key={processor} style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '0.5rem', backgroundColor: '#f8f9fa' }}>
                    <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {processor.toUpperCase()}
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.7rem',
                        backgroundColor: getStatusColor(data.market_position),
                        color: 'white'
                      }}>
                        {data.market_position}
                      </span>
                    </h3>
                    <p style={{ fontSize: '0.9rem', margin: '0 0 1rem 0' }}>{data.competitive_advantage}</p>
                    <div style={{ fontSize: '0.8rem' }}>
                      <p><strong>Compared with:</strong> {data.compared_processors.join(', ')}</p>
                      {Object.keys(data.feature_comparison).length > 0 && (
                        <div>
                          <strong>Features:</strong>
                          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem', flexWrap: 'wrap' }}>
                            {Object.entries(data.feature_comparison).map(([feature, supported]) => (
                              <span key={feature} style={{
                                padding: '0.125rem 0.375rem',
                                borderRadius: '0.125rem',
                                fontSize: '0.7rem',
                                backgroundColor: supported ? '#d4edda' : '#f8d7da',
                                color: supported ? '#155724' : '#721c24'
                              }}>
                                {feature}: {supported ? '✅' : '❌'}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Market Intelligence Tab */}
      {activeTab === 'intelligence' && (
        <div className={styles.card}>
          <h2>📊 Market Intelligence Dashboard</h2>
          <button onClick={loadMarketIntelligence} style={{ marginBottom: '1rem', padding: '0.5rem 1rem', backgroundColor: '#17a2b8', color: 'white', border: 'none', borderRadius: '0.25rem' }}>
            🔄 Refresh Intelligence
          </button>

          {marketIntelligence && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              
              {/* Fraud & Security */}
              <div>
                <h3>🚨 Fraud & Security Status</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {Object.entries(marketIntelligence.fraud_trends).map(([processor, data]) => (
                    <div key={processor} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '0.25rem' }}>
                      <span style={{ fontWeight: 'bold' }}>{processor.toUpperCase()}</span>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem' }}>{data.total_threats} threats</span>
                        <span style={{
                          padding: '0.125rem 0.375rem',
                          borderRadius: '0.125rem',
                          fontSize: '0.7rem',
                          backgroundColor: getRiskBadgeColor(data.risk_level),
                          color: 'white'
                        }}>
                          {data.risk_level}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Service Health */}
              <div>
                <h3>⚡ Service Health Status</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {Object.entries(marketIntelligence.service_health).map(([processor, data]) => (
                    <div key={processor} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '0.25rem' }}>
                      <span style={{ fontWeight: 'bold' }}>{processor.toUpperCase()}</span>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem' }}>{data.average_uptime}% uptime</span>
                        <span style={{
                          padding: '0.125rem 0.375rem',
                          borderRadius: '0.125rem',
                          fontSize: '0.7rem',
                          backgroundColor: getStatusColor(data.health_status),
                          color: 'white'
                        }}>
                          {data.health_status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Market Sentiment */}
              <div>
                <h3>📱 Social Sentiment</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {Object.entries(marketIntelligence.market_sentiment).map(([processor, data]) => (
                    <div key={processor} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '0.25rem' }}>
                      <span style={{ fontWeight: 'bold' }}>{processor.toUpperCase()}</span>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem' }}>{data.total_mentions} mentions</span>
                        <span style={{
                          padding: '0.125rem 0.375rem',
                          borderRadius: '0.125rem',
                          fontSize: '0.7rem',
                          backgroundColor: getStatusColor(data.sentiment_category),
                          color: 'white'
                        }}>
                          {data.sentiment_category} ({data.average_sentiment.toFixed(2)})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Performance Rankings */}
              <div>
                <h3>🏆 Performance Rankings</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {Object.entries(marketIntelligence.performance_rankings).map(([processor, data]) => (
                    <div key={processor} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '0.25rem' }}>
                      <span style={{ fontWeight: 'bold' }}>{processor.toUpperCase()}</span>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem' }}>{data.average_percentile}th percentile</span>
                        <span style={{
                          padding: '0.125rem 0.375rem',
                          borderRadius: '0.125rem',
                          fontSize: '0.7rem',
                          backgroundColor: getStatusColor(data.ranking),
                          color: 'white'
                        }}>
                          {data.ranking}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}
        </div>
      )}

      {/* Synthetic Data Tab */}
      {activeTab === 'synthetic' && (
        <div className={styles.card}>
          <h2>🧪 Synthetic Data Generation</h2>
          <p>Generate realistic transaction data and risk profiles for testing</p>
          
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
            <button
              onClick={generateSyntheticData}
              disabled={loading}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Generating...' : '🎲 Generate 50 Transactions'}
            </button>
          </div>

          {syntheticData && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <div>
                <h3>📊 Generation Summary</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '0.25rem' }}>
                    <span>Total Transactions:</span>
                    <strong>{syntheticData.total_count}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '0.25rem' }}>
                    <span>Business Type:</span>
                    <strong>{syntheticData.business_type_used}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '0.25rem' }}>
                    <span>Average Amount:</span>
                    <strong>${syntheticData.average_amount.toFixed(2)}</strong>
                  </div>
                </div>
              </div>

              <div>
                <h3>⚠️ Risk Distribution</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {Object.entries(syntheticData.risk_distribution).map(([risk, count]) => (
                    <div key={risk} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', backgroundColor: '#f8f9fa', borderRadius: '0.25rem' }}>
                      <span style={{
                        padding: '0.125rem 0.375rem',
                        borderRadius: '0.125rem',
                        fontSize: '0.8rem',
                        backgroundColor: getRiskBadgeColor(risk),
                        color: 'white'
                      }}>
                        {risk.toUpperCase()}
                      </span>
                      <strong>{count} transactions</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Scenario Testing Tab */}
      {activeTab === 'scenarios' && (
        <div className={styles.card}>
          <h2>🔬 Advanced Scenario Testing</h2>
          <p>Test routing behavior under different market conditions</p>
          
          <button
            onClick={runScenarioTests}
            disabled={loading}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#e83e8c',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginBottom: '2rem'
            }}
          >
            {loading ? 'Running Tests...' : '🚀 Run All Scenarios'}
          </button>

          {scenarioResults && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
              {Object.entries(scenarioResults).map(([scenario, result]: [string, any]) => (
                <div key={scenario} style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '0.5rem', backgroundColor: '#f8f9fa' }}>
                  <h3 style={{ margin: '0 0 1rem 0', textTransform: 'capitalize' }}>
                    {scenario.replace('_', ' ')}
                  </h3>
                  
                  {result.error ? (
                    <div style={{ color: '#dc3545' }}>
                      <p><strong>Error:</strong> {result.error}</p>
                    </div>
                  ) : (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <span>Selected:</span>
                        <strong style={{ color: '#28a745' }}>{result.selected_processor?.toUpperCase()}</strong>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <span>Confidence:</span>
                        <strong>{(result.confidence * 100).toFixed(1)}%</strong>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <span>Decision Time:</span>
                        <strong>{result.decision_time_ms?.toFixed(1)}ms</strong>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <span>Amount:</span>
                        <strong>${result.transaction_amount}</strong>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#666' }}>
                        <strong>Available:</strong> {result.scenario_processors?.join(', ')}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Deep Insights Tab */}
      {activeTab === 'insights' && (
        <div className={styles.card}>
          <h2>🔍 Deep Processor Insights</h2>
          
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', alignItems: 'center' }}>
            <label>Select Processor:</label>
            <select
              value={selectedProcessor}
              onChange={(e) => setSelectedProcessor(e.target.value)}
              style={{ padding: '0.5rem', borderRadius: '0.25rem', border: '1px solid #ddd' }}
            >
              <option value="stripe">Stripe</option>
              <option value="paypal">PayPal</option>
              <option value="visa">Visa Direct</option>
              <option value="adyen">Adyen</option>
              <option value="square">Square</option>
            </select>
            <button
              onClick={() => loadProcessorInsights(selectedProcessor)}
              disabled={loading}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#20c997',
                color: 'white',
                border: 'none',
                borderRadius: '0.25rem',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Loading...' : '🔍 Analyze'}
            </button>
          </div>

          {processorInsights && (
            <div>
              <h3>{selectedProcessor.toUpperCase()} - Comprehensive Analysis</h3>
              <p><strong>Insight Types:</strong> {processorInsights.total_insight_types}</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
                {Object.entries(processorInsights.insights_by_type).map(([insightType, data]: [string, any]) => (
                  <div key={insightType} style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '0.5rem' }}>
                    <h4 style={{ margin: '0 0 1rem 0', textTransform: 'capitalize' }}>
                      {insightType.replace('_', ' ')} ({data.count})
                    </h4>
                    
                    {data.insights.map((insight: any, index: number) => (
                      <div key={index} style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#f8f9fa', borderRadius: '0.25rem' }}>
                        <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>{insight.title}</h5>
                        <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem', color: '#666' }}>{insight.content}</p>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#999' }}>
                          <span>Confidence: {(insight.confidence_score * 100).toFixed(0)}%</span>
                          <span>Impact: {(insight.impact_score * 100).toFixed(0)}%</span>
                        </div>
                        
                        {/* Show type-specific data */}
                        {Object.keys(insight.type_specific_data).length > 0 && (
                          <div style={{ marginTop: '0.5rem', fontSize: '0.7rem' }}>
                            {Object.entries(insight.type_specific_data)
                              .filter(([key, value]) => value !== null && value !== undefined && value !== '' && !key.includes('timestamp'))
                              .slice(0, 3) // Show first 3 fields
                              .map(([key, value]: [string, any]) => (
                                <div key={key} style={{ display: 'flex', justifyContent: 'space-between' }}>
                                  <span style={{ textTransform: 'capitalize' }}>{key.replace('_', ' ')}:</span>
                                  <span>{Array.isArray(value) ? value.join(', ') : typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
                                </div>
                              ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  );
}