import { validWords } from './wordlist.js'
import { getEnglishWords } from './english-words.js'

export function score(text) {
  const tokens = text.match(/[a-zA-Z']+/g) || []
  const errors = []

  const skipWords = new Set([
    'dear', 'hello', 'sincerely', 'regards', 'hi', 'hey',
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam',
  ])

  // Spelling: check each token against dictionaries
  tokens.forEach(token => {
    if (token.length < 3) return
    if (token === token.toUpperCase()) return
    if (/\d/.test(token)) return
    if (token[0] === token[0].toUpperCase() && token.slice(1) === token.slice(1).toLowerCase()) return

    const lower = token.toLowerCase().replace(/^'+|'+$/g, '')
    if (lower.length < 3) return
    if (skipWords.has(lower)) return
    if (getEnglishWords().has(lower)) return
    if (validWords.has(lower)) return

    errors.push(`Possible misspelling: "${token}"`)
  })

  // Capitalization: first word of each sentence should be capitalized
  const sentences = text.split(/(?<=[.!?])\s+/)
  sentences.forEach((s, i) => {
    const trimmed = s.trim()
    if (!trimmed) return
    const firstChar = trimmed[0]
    if (firstChar && /[a-z]/.test(firstChar)) {
      errors.push(`Sentence ${i + 1} does not start with a capital letter`)
    }
  })

  // Standalone "i" → single error regardless of count (real e-rater doesn't stack these)
  const standaloneI = text.match(/\bi\b/g) || []
  if (standaloneI.length > 0) {
    errors.push(`Lowercase "i" should be capitalized (${standaloneI.length} occurrence${standaloneI.length > 1 ? 's' : ''})`)
  }

  // NOTE: Removed per-line punctuation check.
  // Real e-rater checks missing periods at sentence boundaries via NLP parsing,
  // NOT by splitting on newlines. The old check caused false positives on
  // naturally formatted emails and text with line breaks.

  const totalWords = Math.max(tokens.length, 1)
  const value = Math.max(0, Math.min(1, 1 - errors.length / totalWords))
  return {
    value,
    details: `${errors.length} mechanic issue(s) across ${tokens.length} word tokens`,
    errors,
  }
}

export function suggest(analysis) {
  if (analysis.value >= 0.85) return []
  const tips = []
  if (analysis.errors.some(e => e.includes('misspelling')))
    tips.push('Check spelling carefully — use a dictionary or spell-checker.')
  if (analysis.errors.some(e => e.includes('capital')))
    tips.push('Capitalize the first word of every sentence.')
  if (analysis.errors.some(e => e.includes('"i"')))
    tips.push('Always capitalize "I" when referring to yourself.')
  return tips.length > 0 ? tips : ['Proofread for spelling and punctuation errors.']
}
