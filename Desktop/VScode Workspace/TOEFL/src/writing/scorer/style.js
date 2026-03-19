// Function words excluded from repetition analysis
const FUNCTION_WORDS = new Set([
  'the','a','an','is','are','was','were','be','been','being','have','has','had',
  'do','does','did','will','would','could','should','may','might','can','shall',
  'must','and','or','but','if','when','while','because','since','although',
  'though','for','from','to','in','on','at','by','with','about','into','through',
  'during','before','after','between','under','over','above','below','out','up',
  'down','off','as','of','this','that','these','those','it','its','he','she',
  'they','we','you','i','me','my','your','his','her','our','their','who',
  'which','what','where','how','why','here','there','then','than','very','much',
  'more','most','some','any','all','each','every','both','few','many','such',
  'own','other','another','same','also','just','still','even','now','already',
  'never','always','often','so','well','back','again','once','yet','not','no',
])

export function score(text) {
  const tokens = (text.match(/[a-zA-Z']+/g) || []).map(w => w.toLowerCase())
  if (tokens.length === 0) return { value: 0, details: 'No words found' }

  // Type-token ratio — for short essays (100-200 words), TTR is naturally higher
  // Map: ≤0.4→0.2, 0.5→0.5, 0.6→0.7, 0.7→0.85, ≥0.8→1.0
  const unique = new Set(tokens)
  const rawTtr = unique.size / tokens.length
  const ttrScore = Math.min(1, Math.max(0.2, (rawTtr - 0.3) * 1.6))

  // Sentence length variance
  const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0)
  let varianceScore = 0
  if (sentences.length >= 2) {
    const lengths = sentences.map(s => s.split(/\s+/).length)
    const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length
    const variance = lengths.reduce((sum, l) => sum + (l - mean) ** 2, 0) / lengths.length
    const stddev = Math.sqrt(variance)
    // stddev 0→0.2, 3→0.5, 6→0.8, 8+→1.0 (more lenient for short essays)
    varianceScore = Math.min(1, 0.2 + stddev / 10)
  }

  // Repetition penalty: content words >4 chars used ≥3 times
  const freq = {}
  tokens.forEach(w => {
    if (w.length > 4 && !FUNCTION_WORDS.has(w)) {
      freq[w] = (freq[w] || 0) + 1
    }
  })
  const repeatedWords = Object.values(freq).filter(count => count >= 3).length
  const repetitionPenalty = Math.min(0.3, repeatedWords * 0.05)

  const ttr = rawTtr // keep raw for display
  const value = Math.max(0, Math.min(1, ttrScore * 0.4 + varianceScore * 0.4 + 0.2 - repetitionPenalty))

  return {
    value,
    details: `TTR: ${ttr.toFixed(2)}, sentence length variance: ${varianceScore.toFixed(2)}, ${repeatedWords} repeated word(s)`,
  }
}

export function suggest(analysis) {
  if (analysis.value >= 0.75) return []
  const tips = []
  const ttrMatch = analysis.details.match(/TTR: ([\d.]+)/)
  if (ttrMatch && parseFloat(ttrMatch[1]) < 0.6)
    tips.push('Avoid repeating the same words — use synonyms to add variety.')
  const varMatch = analysis.details.match(/sentence length variance: ([\d.]+)/)
  if (varMatch && parseFloat(varMatch[1]) < 0.3)
    tips.push('Vary your sentence lengths — mix short punchy sentences with longer detailed ones.')
  const repMatch = analysis.details.match(/(\d+) repeated word/)
  if (repMatch && parseInt(repMatch[1]) > 2)
    tips.push('You are overusing certain words — find synonyms or restructure your sentences.')
  return tips.length > 0 ? tips : ['Improve your writing style by using varied vocabulary and sentence structures.']
}
