/// <reference types="node" />

import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const CSS_PATH = join(process.cwd(), 'src/components/DiagramCanvas.css')

function blockFor(css: string, selector: string): string {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const match = css.match(new RegExp(`${escaped}\\s*\\{([^}]*)\\}`))
  return match?.[1] ?? ''
}

describe('DiagramCanvas retired chunk styling', () => {
  const css = readFileSync(CSS_PATH, 'utf8')

  it('strikes through the retired chunk (old value sits inline next to new)', () => {
    const retiredChunk = blockFor(css, '.chunk.retired')
    expect(retiredChunk).toContain('text-decoration: line-through')
  })

  it('active chunk has no strike', () => {
    const activeChunk = blockFor(css, '.chunk.active')
    expect(activeChunk).not.toContain('line-through')
  })
})
