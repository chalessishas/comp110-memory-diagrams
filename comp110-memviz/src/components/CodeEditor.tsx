import CodeMirror, { type ReactCodeMirrorRef } from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { EditorView, Decoration, type DecorationSet } from '@codemirror/view'
import { StateEffect, StateField } from '@codemirror/state'
import { useEffect, useRef } from 'react'

const setHighlightEffect = StateEffect.define<number | null>()

const highlightField = StateField.define<DecorationSet>({
  create() {
    return Decoration.none
  },
  update(decorations, tr) {
    decorations = decorations.map(tr.changes)
    for (const effect of tr.effects) {
      if (effect.is(setHighlightEffect)) {
        const line = effect.value
        if (line !== null && line > 0 && line <= tr.state.doc.lines) {
          const from = tr.state.doc.line(line).from
          decorations = Decoration.set([
            Decoration.line({ attributes: { class: 'cm-current-step-line' } }).range(from),
          ])
        } else {
          decorations = Decoration.none
        }
      }
    }
    return decorations
  },
  provide: (f) => EditorView.decorations.from(f),
})

type Props = {
  value: string
  onChange: (v: string) => void
  highlightedLine?: number
  readOnly?: boolean
}

export function CodeEditor({ value, onChange, highlightedLine, readOnly }: Props) {
  const ref = useRef<ReactCodeMirrorRef>(null)

  useEffect(() => {
    const view = ref.current?.view
    if (!view) return
    view.dispatch({ effects: setHighlightEffect.of(highlightedLine ?? null) })
  }, [highlightedLine])

  return (
    <CodeMirror
      ref={ref}
      value={value}
      onChange={onChange}
      readOnly={readOnly}
      extensions={[
        python(),
        highlightField,
        EditorView.theme({
          '&': {
            fontSize: '13px',
            fontFamily: 'SFMono-Regular, Menlo, Monaco, Consolas, monospace',
            height: '100%',
            minHeight: '300px',
          },
          '.cm-gutters': {
            backgroundColor: '#f7fafc',
            borderRight: '1px solid #e2e8f0',
            color: '#a0aec0',
          },
          '.cm-current-step-line': {
            backgroundColor: '#fffbea',
            boxShadow: 'inset 3px 0 0 #f6b93b',
          },
        }),
        EditorView.lineWrapping,
      ]}
      basicSetup={{
        lineNumbers: true,
        highlightActiveLine: false,
        foldGutter: false,
      }}
    />
  )
}
