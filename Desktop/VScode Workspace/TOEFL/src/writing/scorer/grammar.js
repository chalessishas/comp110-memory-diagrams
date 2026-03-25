const CONJUNCTIONS = new Set([
  'and','but','or','so','because','since','although','though','when','while',
  'if','after','before','unless','until','whereas','as','once','whenever',
  'wherever','whether','that','which','who','whom','where','why','how',
])

export function score(text) {
  const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0)
  if (sentences.length === 0) return { value: 0, details: 'No sentences found', errors: [] }

  const errors = []

  // Fragment detection: flag only if < 3 words AND missing a verb-like word
  // Real e-rater uses NLP parsing; we approximate by checking for common verb patterns
  const verbPattern = /\b(is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|could|should|may|might|can|shall|must|go|get|make|take|give|come|see|know|think|say|use|find|want|tell|ask|work|seem|feel|try|leave|call|need|become|keep|let|begin|show|hear|play|run|move|live|believe|hold|bring|happen|write|provide|sit|stand|lose|pay|meet|include|continue|set|learn|change|lead|understand|watch|follow|stop|create|speak|read|allow|add|spend|grow|open|walk|win|offer|remember|love|consider|appear|buy|wait|serve|die|send|expect|build|stay|fall|cut|reach|kill|remain|suggest|raise|pass|sell|require|report|decide|pull|develop|mean)\b/i
  sentences.forEach((s, i) => {
    const words = s.split(/\s+/)
    if (words.length < 3 && !verbPattern.test(s)) {
      errors.push(`Possible fragment (sentence ${i + 1}): "${s.substring(0, 40)}"`)
    }
  })

  // Run-on detection: > 50 words AND no semicolons AND no subordinating/coordinating conjunctions
  // Real e-rater rarely triggers this (73% of students get zero penalty)
  sentences.forEach((s, i) => {
    const words = s.split(/\s+/)
    if (words.length > 50 && !s.includes(';')) {
      const hasConjunction = words.some(w => CONJUNCTIONS.has(w.toLowerCase()))
      if (!hasConjunction) {
        errors.push(`Possible run-on sentence (sentence ${i + 1}): ${words.length} words`)
      }
    }
  })

  // Comma splice detection
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
    'forward', 'overall', 'finally', 'personally', 'frankly',
  ])
  const safePhrases = [
    'moving forward', 'looking ahead', 'in addition', 'on the other hand',
    'in contrast', 'as a result', 'in conclusion', 'to summarize',
    'in summary', 'for example', 'in particular', 'in fact',
    'of course', 'after all', 'at the same time', 'on the whole',
    'in general', 'to be honest', 'to be fair', 'in my opinion',
    'in other words', 'that said', 'having said that',
  ]
  const lines = text.split('\n')
  lines.forEach(line => {
    const commaSpliceRegex = /,\s+(I|he|she|they|we|it)\s+\w+/gi
    let csMatch
    while ((csMatch = commaSpliceRegex.exec(line)) !== null) {
      const pos = csMatch.index
      const before = line.substring(Math.max(0, pos - 50), pos).toLowerCase()
      const lastWordMatch = before.match(/(\w+)\s*$/)
      const lastWord = lastWordMatch ? lastWordMatch[1] : ''
      const hasPhrase = safePhrases.some(p => before.includes(p))
      if (!safeWords.has(lastWord) && !hasPhrase) {
        errors.push(`Possible comma splice: "${csMatch[0].trim()}"`)
      }
    }
  })

  // Double negatives — match within each sentence, not across the whole text
  // Real e-rater: 99.6% of students get zero penalty (extremely rare trigger)
  const doubleNegPatterns = [
    /\bnot\b.*\bno\b/i,
    /\bnever\b.*\bno\b/i,
    /\bdon't\b.*\bnothing\b/i,
    /\bcan't\b.*\bnone\b/i,
  ]
  sentences.forEach((s, i) => {
    for (const p of doubleNegPatterns) {
      if (p.test(s)) {
        errors.push(`Possible double negative in sentence ${i + 1}`)
        break
      }
    }
  })

  // Penalty: errors / total words (matching real e-rater formula)
  const totalWords = text.split(/\s+/).filter(w => w.length > 0).length || 1
  const value = Math.max(0, Math.min(1, 1 - errors.length / totalWords))
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
