import { useState } from 'react'

interface ComparisonResult {
  complexity: 'simple' | 'balanced' | 'comprehensive'
  analysisTime: number
  riskFactors: string[]
  confidence: number
  recommendation: string
  processingSteps: string[]
  detailLevel: number
  accuracyScore: number
}

interface AnalysisComparisonOverlayProps {
  isOpen: boolean
  onClose: () => void
}

export default function AnalysisComparisonOverlay({ isOpen, onClose }: AnalysisComparisonOverlayProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [currentComplexity, setCurrentComplexity] = useState<'simple' | 'balanced' | 'comprehensive' | null>(null)
  const [results, setResults] = useState<ComparisonResult[]>([])
  const [testTransaction, setTestTransaction] = useState({
    amount: 2500,
    description: 'B2B Software License Payment',
    customerHistory: 'New customer, first transaction',
    riskIndicators: ['High amount', 'New customer', 'B2B transaction']
  })

  const runComparisonAnalysis = async () => {
    setIsAnalyzing(true)
    setResults([])
    
    const complexities: ('simple' | 'balanced' | 'comprehensive')[] = ['simple', 'balanced', 'comprehensive']
    
    for (const complexity of complexities) {
      setCurrentComplexity(complexity)
      
      // Simulate API call for each complexity level
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
      
      // Generate realistic results based on complexity
      const result: ComparisonResult = {
        complexity,
        analysisTime: complexity === 'simple' ? 150 + Math.random() * 100 : 
                     complexity === 'balanced' ? 800 + Math.random() * 400 : 
                     2200 + Math.random() * 800,
        riskFactors: complexity === 'simple' ? ['Amount check', 'Basic validation'] :
                    complexity === 'balanced' ? ['Amount analysis', 'Customer profile', 'Transaction pattern', 'Risk scoring'] :
                    ['Deep amount analysis', 'Comprehensive customer profiling', 'Historical pattern analysis', 'Cross-reference validation', 'Behavioral scoring', 'Fraud detection algorithms'],
        confidence: complexity === 'simple' ? 65 + Math.random() * 15 :
                   complexity === 'balanced' ? 80 + Math.random() * 10 :
                   92 + Math.random() * 7,
        recommendation: complexity === 'simple' ? 'Process with standard monitoring' :
                       complexity === 'balanced' ? 'Approve with enhanced monitoring and fraud checks' :
                       'Approve with comprehensive risk mitigation: enhanced customer verification, transaction monitoring, and staged processing',
        processingSteps: complexity === 'simple' ? ['Amount validation', 'Basic approval'] :
                        complexity === 'balanced' ? ['Risk assessment', 'Customer verification', 'Pattern analysis', 'Approval decision'] :
                        ['Multi-layer risk assessment', 'Advanced customer profiling', 'Historical pattern analysis', 'Cross-database verification', 'Behavioral analysis', 'Final risk-adjusted approval'],
        detailLevel: complexity === 'simple' ? 25 : complexity === 'balanced' ? 65 : 95,
        accuracyScore: complexity === 'simple' ? 70 + Math.random() * 15 :
                      complexity === 'balanced' ? 85 + Math.random() * 10 :
                      95 + Math.random() * 4
      }
      
      setResults(prev => [...prev, result])
    }
    
    setCurrentComplexity(null)
    setIsAnalyzing(false)
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'from-blue-500 to-cyan-500'
      case 'balanced': return 'from-purple-500 to-pink-500'
      case 'comprehensive': return 'from-orange-500 to-red-500'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const getComplexityBadge = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'bg-blue-500/20 text-blue-300 border-blue-500/50'
      case 'balanced': return 'bg-purple-500/20 text-purple-300 border-purple-500/50'
      case 'comprehensive': return 'bg-orange-500/20 text-orange-300 border-orange-500/50'
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/50'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      ></div>
      
      {/* Modal */}
      <div className="relative w-full h-full flex items-center justify-center p-4">
        <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 rounded-3xl border-2 border-white/20 shadow-2xl w-full max-w-7xl h-[90vh] overflow-hidden">
          
          {/* Header */}
          <div className="relative p-6 bg-gradient-to-r from-purple-600/30 via-pink-600/30 to-orange-600/30 border-b border-white/20">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-orange-500/10 animate-pulse"></div>
            
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 w-10 h-10 bg-red-500/20 hover:bg-red-500/40 rounded-full flex items-center justify-center text-red-300 hover:text-red-200 transition-all z-10"
            >
              ✕
            </button>
            
            <div className="relative z-10">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-purple-200 to-orange-200 bg-clip-text text-transparent mb-2">
                🤖 Claude Analysis Complexity Comparison
              </h1>
              <p className="text-lg text-purple-100 mb-4">
                Compare Simple vs Balanced vs Comprehensive Analysis Performance
              </p>
              
              {/* Test Transaction Info */}
              <div className="bg-white/10 rounded-lg p-4 mb-4">
                <h3 className="text-white font-bold mb-2">📊 Test Transaction</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-300">Amount: </span>
                    <span className="text-white font-bold">${testTransaction.amount.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-300">Type: </span>
                    <span className="text-white">{testTransaction.description}</span>
                  </div>
                  <div className="md:col-span-2">
                    <span className="text-gray-300">Context: </span>
                    <span className="text-white">{testTransaction.customerHistory}</span>
                  </div>
                </div>
              </div>
              
              {/* Analysis Status */}
              {isAnalyzing && currentComplexity && (
                <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-3 mb-4 animate-pulse">
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin w-5 h-5 border-2 border-yellow-400 border-t-transparent rounded-full"></div>
                    <span className="text-yellow-300 font-medium">
                      Analyzing with {currentComplexity.toUpperCase()} complexity...
                    </span>
                  </div>
                </div>
              )}
              
              {/* Control Button */}
              <button
                onClick={runComparisonAnalysis}
                disabled={isAnalyzing}
                className={`px-6 py-3 rounded-xl font-semibold transition-all transform hover:scale-105 ${
                  isAnalyzing 
                    ? 'bg-gray-600 text-gray-300 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white'
                }`}
              >
                {isAnalyzing ? '🔄 Analyzing...' : '🚀 Run Comparison Analysis'}
              </button>
            </div>
          </div>
          
          {/* Content */}
          <div className="h-full overflow-y-auto p-6">
            
            {results.length === 0 && !isAnalyzing ? (
              <div className="text-center py-12 text-gray-400">
                <div className="text-6xl mb-4">🤖</div>
                <p className="text-xl">Click "Run Comparison Analysis" to see Claude's different complexity levels in action</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {['simple', 'balanced', 'comprehensive'].map((complexity, index) => {
                  const result = results.find(r => r.complexity === complexity)
                  const isAnalyzingThis = isAnalyzing && currentComplexity === complexity
                  
                  return (
                    <div 
                      key={complexity}
                      className={`relative rounded-2xl p-6 border-2 transition-all ${
                        result ? 'bg-white/10 border-white/20' : 
                        isAnalyzingThis ? 'bg-yellow-500/10 border-yellow-500/30 animate-pulse' :
                        'bg-gray-500/5 border-gray-500/20'
                      }`}
                    >
                      {/* Complexity Header */}
                      <div className="mb-4">
                        <div className={`inline-block px-3 py-1 rounded-full text-xs font-bold border mb-2 ${getComplexityBadge(complexity)}`}>
                          {complexity.toUpperCase()}
                        </div>
                        <h3 className={`text-xl font-bold bg-gradient-to-r ${getComplexityColor(complexity)} bg-clip-text text-transparent`}>
                          {complexity === 'simple' && '⚡ Simple Analysis'}
                          {complexity === 'balanced' && '🎯 Balanced Analysis'}
                          {complexity === 'comprehensive' && '🔬 Comprehensive Analysis'}
                        </h3>
                      </div>
                      
                      {isAnalyzingThis && (
                        <div className="text-center py-8">
                          <div className="animate-spin w-12 h-12 border-4 border-yellow-400 border-t-transparent rounded-full mx-auto mb-4"></div>
                          <p className="text-yellow-300">Processing...</p>
                        </div>
                      )}
                      
                      {result && (
                        <div className="space-y-4">
                          {/* Metrics */}
                          <div className="grid grid-cols-2 gap-4">
                            <div className="bg-black/20 rounded-lg p-3">
                              <div className="text-2xl font-bold text-white">{Math.round(result.analysisTime)}ms</div>
                              <div className="text-xs text-gray-400">Analysis Time</div>
                            </div>
                            <div className="bg-black/20 rounded-lg p-3">
                              <div className="text-2xl font-bold text-green-400">{Math.round(result.confidence)}%</div>
                              <div className="text-xs text-gray-400">Confidence</div>
                            </div>
                          </div>
                          
                          {/* Accuracy Score */}
                          <div className="bg-black/20 rounded-lg p-3">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm text-gray-300">Accuracy Score</span>
                              <span className="text-sm font-bold text-white">{Math.round(result.accuracyScore)}%</span>
                            </div>
                            <div className="w-full bg-gray-600 rounded-full h-2">
                              <div 
                                className={`h-full rounded-full bg-gradient-to-r ${getComplexityColor(complexity)}`}
                                style={{ width: `${result.accuracyScore}%` }}
                              ></div>
                            </div>
                          </div>
                          
                          {/* Risk Factors */}
                          <div>
                            <h4 className="text-sm font-bold text-white mb-2">Risk Factors Analyzed:</h4>
                            <div className="space-y-1">
                              {result.riskFactors.map((factor, i) => (
                                <div key={i} className="text-xs text-gray-300 flex items-center">
                                  <span className="w-2 h-2 bg-current rounded-full mr-2 opacity-60"></span>
                                  {factor}
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          {/* Processing Steps */}
                          <div>
                            <h4 className="text-sm font-bold text-white mb-2">Processing Steps:</h4>
                            <div className="space-y-1">
                              {result.processingSteps.map((step, i) => (
                                <div key={i} className="text-xs text-gray-300 flex items-start">
                                  <span className="text-blue-400 mr-2 mt-0.5">{i + 1}.</span>
                                  <span>{step}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          {/* Recommendation */}
                          <div className="bg-black/20 rounded-lg p-3">
                            <h4 className="text-sm font-bold text-white mb-1">Recommendation:</h4>
                            <p className="text-xs text-gray-300 leading-relaxed">{result.recommendation}</p>
                          </div>
                          
                          {/* Detail Level */}
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-gray-400">Detail Level:</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-16 bg-gray-600 rounded-full h-1">
                                <div 
                                  className={`h-full rounded-full bg-gradient-to-r ${getComplexityColor(complexity)}`}
                                  style={{ width: `${result.detailLevel}%` }}
                                ></div>
                              </div>
                              <span className="text-white font-bold">{result.detailLevel}%</span>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {!result && !isAnalyzingThis && (
                        <div className="text-center py-8 text-gray-500">
                          <div className="text-4xl mb-2">⏳</div>
                          <p>Awaiting analysis...</p>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
            
            {/* Comparison Summary */}
            {results.length === 3 && (
              <div className="mt-8 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-2xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">📊 Analysis Comparison Summary</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">
                      {Math.round(results.find(r => r.complexity === 'simple')?.analysisTime || 0)}ms
                    </div>
                    <div className="text-sm text-blue-300">Fastest Processing</div>
                    <div className="text-xs text-gray-400">Simple Analysis</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">
                      {Math.round(results.find(r => r.complexity === 'balanced')?.confidence || 0)}%
                    </div>
                    <div className="text-sm text-purple-300">Best Balance</div>
                    <div className="text-xs text-gray-400">Speed vs Accuracy</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-400">
                      {Math.round(results.find(r => r.complexity === 'comprehensive')?.accuracyScore || 0)}%
                    </div>
                    <div className="text-sm text-orange-300">Highest Accuracy</div>
                    <div className="text-xs text-gray-400">Comprehensive Analysis</div>
                  </div>
                </div>
                
                <div className="mt-6 p-4 bg-white/10 rounded-lg">
                  <h4 className="font-bold text-white mb-2">🎯 Key Insights:</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Simple analysis offers 3x faster processing for basic validation needs</li>
                    <li>• Balanced analysis provides optimal speed-accuracy trade-off for most use cases</li>
                    <li>• Comprehensive analysis delivers maximum accuracy for high-risk scenarios</li>
                    <li>• Processing time increases exponentially with complexity but accuracy gains diminish</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}