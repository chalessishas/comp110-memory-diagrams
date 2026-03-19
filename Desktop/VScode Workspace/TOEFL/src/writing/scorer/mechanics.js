import { validWords } from './wordlist.js'

export function score(text) {
  const tokens = text.match(/[a-zA-Z']+/g) || []
  const errors = []

  // Words to skip in spell check (email format words, titles, common proper nouns)
  const skipWords = new Set([
    'dear', 'hello', 'sincerely', 'regards', 'hi', 'hey',
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam',
  ])

  // Spelling: check each token against validWords
  tokens.forEach(token => {
    // Skip: < 3 chars, all caps (acronyms), contains numbers
    if (token.length < 3) return
    if (token === token.toUpperCase()) return
    if (/\d/.test(token)) return

    // Skip capitalized words (likely proper nouns: names, places)
    if (token[0] === token[0].toUpperCase() && token.slice(1) === token.slice(1).toLowerCase()) return

    const lower = token.toLowerCase().replace(/^'+|'+$/g, '') // strip leading/trailing apostrophes
    if (lower.length < 3) return
    if (skipWords.has(lower)) return
    if (validWords.has(lower)) return

    // Before flagging as misspelled, check if a base form exists in validWords
    // This handles common suffixes: -ed, -ing, -s, -es, -er, -est, -ly, -tion, -ment, -ness
    const baseChecks = [
      lower.replace(/ed$/, ''), lower.replace(/ed$/, 'e'),
      lower.replace(/ing$/, ''), lower.replace(/ing$/, 'e'), lower.replace(/ting$/, 't'),
      lower.replace(/s$/, ''), lower.replace(/es$/, ''), lower.replace(/ies$/, 'y'),
      lower.replace(/er$/, ''), lower.replace(/er$/, 'e'),
      lower.replace(/est$/, ''), lower.replace(/est$/, 'e'),
      lower.replace(/ly$/, ''), lower.replace(/ly$/, 'le'),
      lower.replace(/tion$/, 't'), lower.replace(/tion$/, 'te'),
      lower.replace(/ment$/, ''), lower.replace(/ness$/, ''),
      lower.replace(/able$/, ''), lower.replace(/able$/, 'e'),
      lower.replace(/ful$/, ''), lower.replace(/less$/, ''),
      lower.replace(/ous$/, ''), lower.replace(/ive$/, ''), lower.replace(/ive$/, 'e'),
      lower.replace(/al$/, ''), lower.replace(/ally$/, ''),
    ]
    const hasBase = baseChecks.some(base => base.length >= 3 && validWords.has(base))
    if (!hasBase) {
      errors.push(`Possible misspelling: "${token}"`)
    }
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

  // Standalone "i" should be "I"
  const standaloneI = text.match(/\bi\b/g) || []
  standaloneI.forEach(() => errors.push('Lowercase "i" should be capitalized'))

  // Check sentences end with punctuation
  const sentenceBlocks = text.split('\n').map(s => s.trim()).filter(s => s.length > 0)
  sentenceBlocks.forEach((block, i) => {
    if (!/[.!?]$/.test(block)) {
      errors.push(`Paragraph/line ${i + 1} does not end with punctuation`)
    }
  })

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
  if (analysis.errors.some(e => e.includes('punctuation')))
    tips.push('End every sentence with a period, question mark, or exclamation point.')
  return tips.length > 0 ? tips : ['Proofread for spelling and punctuation errors.']
}
