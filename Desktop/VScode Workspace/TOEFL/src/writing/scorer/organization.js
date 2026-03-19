const DISCOURSE_MARKERS = [
  'however','moreover','furthermore','additionally','in addition','on the other hand',
  'nevertheless','for instance','for example','such as','in conclusion','therefore',
  'consequently','as a result','firstly','secondly','finally','meanwhile','similarly',
  'in contrast','despite','although','while','whereas','in summary','to summarize',
  'in particular','notably','specifically','that is','in other words','by contrast',
  'on the contrary','at the same time','in the meantime','above all','after all',
  'in fact','indeed','to begin with','first of all','last but not least','overall',
]

function countUniqueMarkers(text) {
  const lower = text.toLowerCase()
  const found = new Set()
  DISCOURSE_MARKERS.forEach(marker => {
    if (lower.includes(marker)) found.add(marker)
  })
  return found.size
}

export function score(text, taskType = 'general') {
  const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0)
  const sentenceCount = Math.max(sentences.length, 1)

  // Discourse marker density score
  const uniqueMarkers = countUniqueMarkers(text)
  const markerDensity = uniqueMarkers / sentenceCount
  // 0 markers → 0, 0.3+/sentence → 1.0
  const markerScore = Math.min(1, markerDensity / 0.3)

  // Paragraph count score
  const paragraphs = text.split(/\n+/).map(p => p.trim()).filter(p => p.length > 0)
  const paragraphCount = paragraphs.length
  let paragraphScore = 0.4
  if (paragraphCount >= 2) paragraphScore = 0.7
  if (paragraphCount >= 3) paragraphScore = 1.0

  // Task-specific bonuses
  let taskSpecific = 0
  const lower = text.toLowerCase()

  if (taskType === 'email') {
    const hasGreeting = /\b(dear|hello|hi|greetings)\b/i.test(text)
    const hasClosing = /\b(regards|sincerely|thank|best|yours|cheers|warm)\b/i.test(text)
    taskSpecific = (hasGreeting ? 0.5 : 0) + (hasClosing ? 0.5 : 0)
  } else if (taskType === 'discussion') {
    const hasEngagement =
      /\bi agree\b/i.test(text) ||
      /\bi disagree\b/i.test(text) ||
      /makes a good point/i.test(text) ||
      /\bwhile [A-Z]/i.test(text) ||
      /\bI think\b/i.test(text) ||
      /\bIn my opinion\b/i.test(text) ||
      /\bI believe\b/i.test(text)
    taskSpecific = hasEngagement ? 1.0 : 0.3
  } else {
    // General: reward having a clear opening and closing cue
    const hasOpener = /\b(first|to begin|in this|the purpose|this essay|one reason)\b/i.test(text)
    const hasCloser = /\b(in conclusion|to summarize|overall|in summary|therefore)\b/i.test(text)
    taskSpecific = (hasOpener ? 0.5 : 0) + (hasCloser ? 0.5 : 0)
  }

  const value = Math.min(
    1,
    markerScore * 0.5 + paragraphScore * 0.3 + taskSpecific * 0.2,
  )

  return {
    value,
    details: `${uniqueMarkers} unique discourse markers, ${paragraphCount} paragraph(s), taskScore=${taskSpecific.toFixed(2)}`,
  }
}

export function suggest(analysis) {
  if (analysis.value >= 0.8) return []
  const tips = []
  if (analysis.details.includes('0 unique discourse markers') || analysis.value < 0.5)
    tips.push('Use discourse markers (however, moreover, in conclusion) to connect your ideas.')
  if (analysis.details.includes('1 paragraph'))
    tips.push('Divide your response into multiple paragraphs for clarity.')
  if (analysis.details.includes('taskScore=0.00'))
    tips.push('Include task-specific conventions (greetings for emails, engagement phrases for discussions).')
  return tips.length > 0 ? tips : ['Improve cohesion by using transition phrases between ideas.']
}
