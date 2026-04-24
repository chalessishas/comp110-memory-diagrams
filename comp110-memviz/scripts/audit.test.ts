import { describe, it, expect } from 'vitest'
import { run } from '../src/interpreter/evaluator'
import problems from './problems.json'

describe('COMP110 24s memory-diagram audit', () => {
  const rows: { id: string; status: string; detail: string }[] = []

  for (const p of problems as { id: string; source: string | null }[]) {
    if (!p.source) continue
    it(`handles ${p.id}`, () => {
      let status = 'PASS'
      let detail = ''
      try {
        const snapshots = run(p.source)
        const last = snapshots[snapshots.length - 1]
        if (last.error) {
          status = 'RUNTIME'
          detail = last.error
        } else {
          detail = JSON.stringify(last.output)
        }
      } catch (e) {
        status = 'PARSE'
        detail = (e as Error).message
      }
      rows.push({ id: p.id, status, detail })
      // Don't fail the test — we want to collect data.
    })
  }

  it('prints audit summary', () => {
    console.log('\n=== AUDIT SUMMARY ===')
    for (const r of rows) {
      console.log(`${r.status.padEnd(7)} ${r.id.padEnd(38)} ${r.detail.slice(0, 80)}`)
    }
    const pass = rows.filter((r) => r.status === 'PASS').length
    console.log(`\nTotal: ${pass}/${rows.length} passing\n`)
    expect(rows.length).toBeGreaterThan(0)
  })
})
