export function score(text) {
  const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0)
  if (sentences.length === 0) return { value: 0, details: 'No sentences found', errors: [] }

  const errors = []

  // Fragment detection: sentences with < 3 words
  sentences.forEach((s, i) => {
    const words = s.split(/\s+/)
    if (words.length < 3) errors.push(`Possible fragment (sentence ${i + 1}): "${s.substring(0, 40)}"`)
  })

  // Run-on detection: sentences > 40 words without semicolons or conjunctions
  sentences.forEach((s, i) => {
    const words = s.split(/\s+/)
    if (words.length > 40 && !s.includes(';')) {
      errors.push(`Possible run-on sentence (sentence ${i + 1}): ${words.length} words`)
    }
  })

  // Comma splice detection: ", I/he/she/they/we/it [verb]" patterns
  // Exclude: after conjunctions, discourse markers, and subordinating conjunctions
  const safeWords = new Set([
    'however', 'moreover', 'furthermore', 'additionally', 'nevertheless',
    'therefore', 'consequently', 'meanwhile', 'otherwise', 'instead',
    'unfortunately', 'fortunately', 'similarly', 'alternatively',
    'specifically', 'honestly', 'personally', 'apparently', 'obviously',
    'clearly', 'indeed', 'certainly', 'naturally', 'surprisingly',
    'interestingly', 'importantly', 'ideally', 'typically', 'generally',
    'and', 'but', 'so', 'or', 'nor', 'yet', 'for',
    'if', 'when', 'while', 'because', 'since', 'although', 'though',
    'unless', 'until', 'after', 'before', 'where', 'whereas',
  ])
  const commaSpliceRegex = /,\s+(I|he|she|they|we|it)\s+\w+/gi
  let csMatch
  while ((csMatch = commaSpliceRegex.exec(text)) !== null) {
    const pos = csMatch.index
    const before = text.substring(Math.max(0, pos - 40), pos).toLowerCase()
    const lastWordMatch = before.match(/(\w+)\s*$/)
    const lastWord = lastWordMatch ? lastWordMatch[1] : ''
    if (!safeWords.has(lastWord)) {
      errors.push(`Possible comma splice: "${csMatch[0].trim()}"`)
    }
  }

  // Double negatives
  const doubleNegPatterns = [
    /\bnot\b.*\bno\b/i,
    /\bnever\b.*\bno\b/i,
    /\bdon't\b.*\bnothing\b/i,
    /\bcan't\b.*\bnone\b/i,
  ]
  doubleNegPatterns.forEach(p => {
    if (p.test(text)) errors.push('Possible double negative detected')
  })

  const value = Math.max(0, Math.min(1, 1 - errors.length / sentences.length))
  return { value, details: `${errors.length} issue(s) in ${sentences.length} sentences`, errors }
}

export function suggest(analysis) {
  if (analysis.value >= 0.9) return []
  const tips = []
  if (analysis.errors.some(e => e.includes('fragment')))
    tips.push('Ensure each sentence has a subject and verb.')
  if (analysis.errors.some(e => e.includes('run-on')))
    tips.push('Break long sentences into shorter ones using periods or semicolons.')
  if (analysis.errors.some(e => e.includes('comma splice')))
    tips.push('Use a conjunction (and, but, so) or period instead of a comma between independent clauses.')
  if (analysis.errors.some(e => e.includes('double negative')))
    tips.push('Avoid using two negatives in the same clause.')
  return tips.length > 0 ? tips : ['Review your sentence structure for grammatical accuracy.']
}
