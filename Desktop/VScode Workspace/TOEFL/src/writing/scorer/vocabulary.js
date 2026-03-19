import { commonWords } from './wordlist.js'

// Function words to exclude from content-word analysis
const FUNCTION_POS = new Set([
  'the','a','an','is','are','was','were','be','been','being','have','has','had',
  'do','does','did','will','would','could','should','may','might','can','shall',
  'must','and','or','but','if','when','while','because','since','although',
  'though','for','from','to','in','on','at','by','with','about','into','through',
  'during','before','after','between','under','over','above','below','out','up',
  'down','off','as','of','this','that','these','those','it','its','he','she',
  'they','we','you','i','me','my','your','his','her','our','their','who',
  'which','what','where','how','why','here','there','then','than','very','much',
  'more','most','some','any','all','each','every','both','few','many','such',
  'own','other','another','same','different','first','last','next','new','old',
  'good','great','little','long','big','small','right','only','also','just',
  'still','even','now','already','never','always','often','sometimes','too',
  'so','well','back','away','again','once','yet','almost','enough','quite',
  'rather','not','no',
])

function isContentWord(word) {
  return word.length >= 4 && !FUNCTION_POS.has(word)
}

// Linear interpolation clamped to [0, 1]
function linearMap(value, x0, x1, y0, y1) {
  if (value <= x0) return y0
  if (value >= x1) return y1
  return y0 + ((value - x0) / (x1 - x0)) * (y1 - y0)
}

export function score(text) {
  const tokens = (text.match(/[a-zA-Z']+/g) || []).map(w => w.toLowerCase())
  if (tokens.length === 0) return { value: 0, details: 'No words found' }

  // Average word length score
  const avgLen = tokens.reduce((sum, w) => sum + w.length, 0) / tokens.length
  // 3.5→0.2, 4.0→0.4, 4.5→0.6, 5.0→0.8, 5.5→1.0
  const avgLenScore = linearMap(avgLen, 3.5, 5.5, 0.2, 1.0)

  // Rare word ratio (content words NOT in commonWords)
  const contentTokens = tokens.filter(isContentWord)
  const totalContent = contentTokens.length || 1
  const rareCount = contentTokens.filter(w => !commonWords.has(w)).length
  const rareRatio = rareCount / totalContent
  // 0%→0.2, 5%→0.4, 10%→0.6, 15%→0.8, 20%→1.0
  const rareScore = linearMap(rareRatio, 0, 0.2, 0.2, 1.0)

  const value = Math.min(1, (avgLenScore + rareScore) / 2)
  return {
    value,
    details: `Avg word length: ${avgLen.toFixed(2)}, rare word ratio: ${(rareRatio * 100).toFixed(1)}%`,
  }
}

export function suggest(analysis) {
  if (analysis.value >= 0.75) return []
  const tips = []
  if (analysis.details.includes('Avg word length')) {
    const match = analysis.details.match(/Avg word length: ([\d.]+)/)
    if (match && parseFloat(match[1]) < 4.5)
      tips.push('Expand your vocabulary — use more precise, academic words instead of simple ones.')
  }
  if (analysis.details.includes('rare word ratio')) {
    const match = analysis.details.match(/rare word ratio: ([\d.]+)%/)
    if (match && parseFloat(match[1]) < 10)
      tips.push('Incorporate more varied and sophisticated vocabulary from the Academic Word List.')
  }
  return tips.length > 0 ? tips : ['Use a wider range of vocabulary to demonstrate lexical diversity.']
}
