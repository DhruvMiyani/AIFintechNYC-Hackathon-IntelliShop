import React, { useState, useEffect } from 'react';

/**
 * Brave Search Payment Intelligence Widget
 * 
 * A drop-in React component that provides intelligent payment provider recommendations
 * using real-time market data from Brave Search API with synthetic fallback.
 * 
 * Props:
 * - amount: Transaction amount (number)
 * - businessType: 'startup_tech', 'enterprise', 'small_business' (string)
 * - urgency: 'normal', 'high' (string)
 * - apiUrl: Your deployed API URL (string)
 * - onRecommendation: Callback when recommendation is received (function)
 * - showDetails: Show detailed competitive analysis (boolean)
 */
const PaymentIntelligenceWidget = ({ 
  amount = 1000,
  businessType = 'startup_tech',
  urgency = 'normal',
  apiUrl = 'http://localhost:8000',
  onRecommendation,
  showDetails = true
}) => {
  const [recommendation, setRecommendation] = useState('');
  const [competitiveData, setCompetitiveData] = useState(null);
  const [dataSource, setDataSource] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRecommendation();
  }, [amount, businessType, urgency]);

  const fetchRecommendation = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get text recommendation
      const recommendationResponse = await fetch(
        `${apiUrl}/best-payment-provider?amount=${amount}&business_type=${businessType}&urgency=${urgency}`
      );
      
      if (!recommendationResponse.ok) {
        throw new Error(`API Error: ${recommendationResponse.status}`);
      }
      
      const text = await recommendationResponse.text();
      setRecommendation(text);

      // Get competitive analysis for additional details
      if (showDetails) {
        const competitiveResponse = await fetch(`${apiUrl}/competitive-analysis`);
        if (competitiveResponse.ok) {
          const competitiveJson = await competitiveResponse.json();
          setCompetitiveData(competitiveJson.competitive_analysis);
          setDataSource(competitiveJson.data_quality);
        }
      }

      // Call callback if provided
      onRecommendation && onRecommendation({ text, competitiveData });

    } catch (err) {
      setError(err.message);
      console.error('Payment Intelligence Widget Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDataSourceBadge = () => {
    if (!dataSource) return null;
    
    const isRealBrave = dataSource.source === 'brave_search_api';
    const isRateLimited = dataSource.rate_limited;
    
    const badgeStyle = {
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      fontWeight: 'bold',
      display: 'inline-block',
      marginBottom: '8px',
      backgroundColor: isRealBrave ? '#28a745' : isRateLimited ? '#ffc107' : '#17a2b8',
      color: isRealBrave ? 'white' : isRateLimited ? 'black' : 'white'
    };

    return (
      <div style={badgeStyle}>
        {isRealBrave ? '🔴 LIVE Brave Search Data' : 
         isRateLimited ? '⚠️ Rate Limited - Proves Real API Integration!' : 
         '🔄 High-Quality Synthetic Data'}
      </div>
    );
  };

  const getCompetitiveRankings = () => {
    if (!competitiveData || !showDetails) return null;

    const sortedProviders = Object.entries(competitiveData)
      .sort(([, a], [, b]) => (a.ranking || 999) - (b.ranking || 999))
      .slice(0, 3);

    return (
      <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
        <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 'bold' }}>
          🏆 Market Rankings
        </h4>
        {sortedProviders.map(([provider, data], index) => {
          const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉';
          return (
            <div key={provider} style={{ marginBottom: '8px', fontSize: '13px' }}>
              {medal} <strong>#{data.ranking} {provider.toUpperCase()}</strong>
              <div style={{ fontSize: '12px', color: '#666', marginLeft: '20px' }}>
                {data.competitive_advantage}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const widgetStyle = {
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '16px',
    backgroundColor: 'white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    maxWidth: '600px',
    margin: '16px 0'
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px'
  };

  const buttonStyle = {
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '6px 12px',
    fontSize: '12px',
    cursor: 'pointer',
    marginLeft: '8px'
  };

  const recommendationStyle = {
    backgroundColor: '#f8f9fa',
    border: '1px solid #e9ecef',
    borderRadius: '4px',
    padding: '12px',
    fontFamily: 'Monaco, monospace',
    fontSize: '12px',
    whiteSpace: 'pre-wrap',
    overflow: 'auto',
    maxHeight: '400px'
  };

  if (error) {
    return (
      <div style={{...widgetStyle, borderColor: '#dc3545'}}>
        <h3 style={{ color: '#dc3545', margin: '0 0 8px 0' }}>❌ Payment Intelligence Error</h3>
        <p style={{ margin: 0, fontSize: '14px' }}>{error}</p>
        <button onClick={fetchRecommendation} style={{...buttonStyle, backgroundColor: '#dc3545', marginTop: '8px'}}>
          🔄 Retry
        </button>
      </div>
    );
  }

  return (
    <div style={widgetStyle}>
      <div style={headerStyle}>
        <h3 style={{ margin: 0, fontSize: '16px' }}>💡 AI Payment Recommendation</h3>
        <div>
          {getDataSourceBadge()}
          <button 
            onClick={fetchRecommendation} 
            disabled={loading}
            style={{...buttonStyle, opacity: loading ? 0.6 : 1}}
          >
            {loading ? '⏳ Loading...' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      <div style={{ fontSize: '13px', color: '#666', marginBottom: '12px' }}>
        Amount: ${amount.toLocaleString()} | Business: {businessType.replace('_', ' ')} | Urgency: {urgency}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <div>🔄 Getting intelligent recommendation...</div>
          <div style={{ fontSize: '12px', marginTop: '8px' }}>
            Analyzing market conditions with Brave Search API
          </div>
        </div>
      ) : (
        <>
          <div style={recommendationStyle}>
            {recommendation || 'No recommendation available'}
          </div>
          {getCompetitiveRankings()}
        </>
      )}
    </div>
  );
};

export default PaymentIntelligenceWidget;

// Example usage:
/*
<PaymentIntelligenceWidget
  amount={5000}
  businessType="startup_tech"
  urgency="high"
  apiUrl="https://your-deployed-api.herokuapp.com"
  onRecommendation={(data) => {
    console.log('Got recommendation:', data);
    // Use the recommendation in your payment flow
  }}
  showDetails={true}
/>
*/