const DETAIL_MARKERS = [
  'for example','for instance','such as','specifically','in particular',
  'according to','namely','to illustrate','as evidence','as shown','as demonstrated',
  'in fact','as an example','including','like',
]

// Word count ranges per task type
const WORD_COUNT_TARGETS = {
  email:      { min: 50,  target: 120, max: 200 },
  discussion: { min: 80,  target: 160, max: 300 },
  general:    { min: 100, target: 200, max: 400 },
}

function wordCountScore(wordCount, taskType) {
  const range = WORD_COUNT_TARGETS[taskType] || WORD_COUNT_TARGETS.general
  if (wordCount < range.min) return wordCount / range.min * 0.5
  if (wordCount <= range.target) return 0.5 + ((wordCount - range.min) / (range.target - range.min)) * 0.5
  if (wordCount <= range.max) return 1.0
  // Penalize very long responses slightly
  return Math.max(0.7, 1.0 - (wordCount - range.max) / range.max * 0.3)
}

function detailMarkersScore(text) {
  const lower = text.toLowerCase()
  const found = DETAIL_MARKERS.filter(m => lower.includes(m))
  // 0→0, 1→0.4, 2→0.7, 3+→1.0
  if (found.length === 0) return 0
  if (found.length === 1) return 0.4
  if (found.length === 2) return 0.7
  return 1.0
}

function sentenceCountScore(count, taskType) {
  const targets = {
    email:      { min: 4,  good: 8  },
    discussion: { min: 5,  good: 10 },
    general:    { min: 6,  good: 12 },
  }
  const t = targets[taskType] || targets.general
  if (count < t.min) return count / t.min * 0.5
  if (count < t.good) return 0.5 + ((count - t.min) / (t.good - t.min)) * 0.5
  return 1.0
}

export function score(text, taskType = 'general') {
  const words = (text.match(/\b\w+\b/g) || [])
  const wordCount = words.length
  const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0)
  const sentenceCount = sentences.length

  const wcScore  = wordCountScore(wordCount, taskType)
  const dmScore  = detailMarkersScore(text)
  const scScore  = sentenceCountScore(sentenceCount, taskType)

  const value = Math.min(1, wcScore * 0.5 + dmScore * 0.3 + scScore * 0.2)

  return {
    value,
    details: `${wordCount} words, ${sentenceCount} sentences, ${
      DETAIL_MARKERS.filter(m => text.toLowerCase().includes(m)).length
    } detail marker(s)`,
  }
}

export function suggest(analysis) {
  if (analysis.value >= 0.8) return []
  const tips = []
  const wordMatch = analysis.details.match(/(\d+) words/)
  if (wordMatch && parseInt(wordMatch[1]) < 100)
    tips.push('Expand your response — develop your ideas with more detail and explanation.')
  if (analysis.details.includes('0 detail marker'))
    tips.push('Support your points with specific examples (for example, for instance, such as).')
  const sentMatch = analysis.details.match(/(\d+) sentences/)
  if (sentMatch && parseInt(sentMatch[1]) < 5)
    tips.push('Add more sentences to fully develop each idea.')
  return tips.length > 0 ? tips : ['Develop your ideas further with concrete examples and evidence.']
}
