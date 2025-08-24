import React, { useState, useEffect } from 'react';
import styles from '../styles/Dashboard.module.css';

interface PaymentRequest {
  amount: number;
  currency: string;
  merchant_id: string;
  customer_id?: string;
  urgency: string;
  complexity: string;
  test_insights: boolean;
}

interface RoutingDecision {
  selected_processor: string;
  processor_details: any;
  reasoning: string;
  confidence: number;
  decision_time_ms: number;
  fallback_chain: string[];
  claude_params: any;
}

interface ProcessorComparison {
  id: string;
  name: string;
  original_fee: number;
  effective_fee: number;
  success_rate: number;
  priority_score: number;
  insights_applied: string[];
}

export default function TestInsights() {
  const [request, setRequest] = useState<PaymentRequest>({
    amount: 1500,
    currency: 'USD',
    merchant_id: 'demo_merchant',
    urgency: 'normal',
    complexity: 'balanced',
    test_insights: true
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    // Load demo scenarios
    fetch('http://localhost:8000/demo-scenarios')
      .then(res => res.json())
      .then(data => setScenarios(data.scenarios))
      .catch(err => console.error('Failed to load scenarios:', err));

    // Load analytics
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/insights-analytics');
      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  };

  const routePayment = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/route-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      const data = await response.json();
      setResult(data);
      await loadAnalytics(); // Refresh analytics
    } catch (error) {
      console.error('Error routing payment:', error);
      setResult({ success: false, error: error.message });
    }
    setLoading(false);
  };

  const loadScenario = (scenario: any) => {
    setRequest(scenario.payload);
    setResult(null);
  };

  const forceRefreshInsights = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/force-insights-refresh', {
        method: 'POST'
      });
      const data = await response.json();
      alert(data.success ? 'Insights refreshed!' : `Error: ${data.error}`);
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🔍 Brave Search Insights Integration Test</h1>
        <p>Test the enhanced payment routing with real-time market intelligence</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        {/* Request Configuration */}
        <div className={styles.card}>
          <h2>Payment Request</h2>
          
          <div style={{ marginBottom: '1rem' }}>
            <label>Amount ($): </label>
            <input
              type="number"
              value={request.amount}
              onChange={(e) => setRequest({ ...request, amount: parseFloat(e.target.value) })}
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>Merchant ID: </label>
            <input
              type="text"
              value={request.merchant_id}
              onChange={(e) => setRequest({ ...request, merchant_id: e.target.value })}
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>Complexity: </label>
            <select
              value={request.complexity}
              onChange={(e) => setRequest({ ...request, complexity: e.target.value })}
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            >
              <option value="simple">Simple (No Insights)</option>
              <option value="balanced">Balanced (Basic Insights)</option>
              <option value="comprehensive">Comprehensive (Full Insights)</option>
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>Urgency: </label>
            <select
              value={request.urgency}
              onChange={(e) => setRequest({ ...request, urgency: e.target.value })}
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            >
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label>
              <input
                type="checkbox"
                checked={request.test_insights}
                onChange={(e) => setRequest({ ...request, test_insights: e.target.checked })}
              />
              <span style={{ marginLeft: '0.5rem' }}>Use Mock Insights (Demo)</span>
            </label>
          </div>

          <button
            onClick={routePayment}
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#0070f3',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '1rem',
              marginBottom: '1rem'
            }}
          >
            {loading ? 'Routing Payment...' : '🚀 Route Payment'}
          </button>

          <button
            onClick={forceRefreshInsights}
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.5rem',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '0.9rem'
            }}
          >
            🔄 Force Refresh Insights
          </button>
        </div>

        {/* Demo Scenarios */}
        <div className={styles.card}>
          <h2>Demo Scenarios</h2>
          {scenarios.map((scenario, index) => (
            <div key={index} style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '0.5rem' }}>
              <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem' }}>{scenario.name}</h3>
              <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#666' }}>
                {scenario.description}
              </p>
              <button
                onClick={() => loadScenario(scenario)}
                style={{
                  padding: '0.25rem 0.75rem',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.25rem',
                  cursor: 'pointer',
                  fontSize: '0.8rem'
                }}
              >
                Load Scenario
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className={styles.card} style={{ marginBottom: '2rem' }}>
          <h2>🎯 Routing Result</h2>
          
          {result.success ? (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                <div>
                  <h3>Selected Processor</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#28a745' }}>
                    {result.routing_decision.selected_processor.toUpperCase()}
                  </div>
                  <p><strong>Confidence:</strong> {(result.routing_decision.confidence * 100).toFixed(1)}%</p>
                  <p><strong>Decision Time:</strong> {result.routing_decision.decision_time_ms.toFixed(1)}ms</p>
                  <p><strong>Complexity:</strong> {result.request_details.complexity}</p>
                </div>

                <div>
                  <h3>Processor Details</h3>
                  <p><strong>Name:</strong> {result.routing_decision.processor_details.name}</p>
                  <p><strong>Original Fee:</strong> {result.routing_decision.processor_details.fee_percentage}%</p>
                  <p><strong>Effective Fee:</strong> {result.routing_decision.processor_details.effective_fee_percentage?.toFixed(2) || result.routing_decision.processor_details.fee_percentage}%</p>
                  <p><strong>Success Rate:</strong> {(result.routing_decision.processor_details.adjusted_success_rate || result.routing_decision.processor_details.metrics.success_rate * 100).toFixed(1)}%</p>
                </div>
              </div>

              <div style={{ marginTop: '1rem' }}>
                <h3>AI Reasoning</h3>
                <div style={{ backgroundColor: '#f8f9fa', padding: '1rem', borderRadius: '0.5rem', fontFamily: 'monospace', fontSize: '0.9rem' }}>
                  {result.routing_decision.reasoning}
                </div>
              </div>

              {result.processor_comparison && (
                <div style={{ marginTop: '1rem' }}>
                  <h3>Processor Comparison</h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#f8f9fa' }}>
                          <th style={{ padding: '0.5rem', textAlign: 'left', border: '1px solid #ddd' }}>Processor</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right', border: '1px solid #ddd' }}>Original Fee</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right', border: '1px solid #ddd' }}>Effective Fee</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right', border: '1px solid #ddd' }}>Success Rate</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right', border: '1px solid #ddd' }}>Priority</th>
                          <th style={{ padding: '0.5rem', textAlign: 'left', border: '1px solid #ddd' }}>Insights</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.processor_comparison.map((proc: ProcessorComparison) => (
                          <tr key={proc.id} style={{ backgroundColor: proc.id === result.routing_decision.selected_processor ? '#e8f5e8' : 'white' }}>
                            <td style={{ padding: '0.5rem', border: '1px solid #ddd', fontWeight: proc.id === result.routing_decision.selected_processor ? 'bold' : 'normal' }}>
                              {proc.name} {proc.id === result.routing_decision.selected_processor && '👑'}
                            </td>
                            <td style={{ padding: '0.5rem', textAlign: 'right', border: '1px solid #ddd' }}>{proc.original_fee.toFixed(2)}%</td>
                            <td style={{ padding: '0.5rem', textAlign: 'right', border: '1px solid #ddd' }}>
                              <span style={{ color: proc.effective_fee < proc.original_fee ? '#28a745' : 'inherit' }}>
                                {proc.effective_fee.toFixed(2)}%
                              </span>
                            </td>
                            <td style={{ padding: '0.5rem', textAlign: 'right', border: '1px solid #ddd' }}>{(proc.success_rate * 100).toFixed(1)}%</td>
                            <td style={{ padding: '0.5rem', textAlign: 'right', border: '1px solid #ddd' }}>{proc.priority_score.toFixed(2)}</td>
                            <td style={{ padding: '0.5rem', border: '1px solid #ddd', fontSize: '0.8rem' }}>
                              {proc.insights_applied.length > 0 ? proc.insights_applied.join('; ') : 'None'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ color: '#dc3545' }}>
              <h3>Error</h3>
              <p>{result.error || result.detail}</p>
            </div>
          )}
        </div>
      )}

      {/* Analytics */}
      {analytics && (
        <div className={styles.card}>
          <h2>📊 System Analytics</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '2rem' }}>
            <div>
              <h3>Routing Performance</h3>
              <p><strong>Total Decisions:</strong> {analytics.summary.total_decisions}</p>
              <p><strong>Insights Effectiveness:</strong> {analytics.summary.insights_effectiveness.toFixed(1)}%</p>
            </div>
            <div>
              <h3>Cache Performance</h3>
              <p><strong>Cache Entries:</strong> {analytics.summary.cache_performance.entries}</p>
              <p><strong>Last Fetch:</strong> {analytics.summary.cache_performance.last_fetch_ago ? `${Math.round(analytics.summary.cache_performance.last_fetch_ago)}s ago` : 'Never'}</p>
            </div>
            <div>
              <h3>Insights Status</h3>
              <p><strong>Enabled:</strong> {analytics.insights_analytics.insights_enabled ? '✅ Yes' : '❌ No'}</p>
              <p><strong>Orchestrator Cache:</strong> {analytics.insights_analytics.orchestrator_cache_size}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}