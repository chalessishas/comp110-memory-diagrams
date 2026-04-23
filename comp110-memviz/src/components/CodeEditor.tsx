import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { EditorView } from '@codemirror/view'

type Props = {
  value: string
  onChange: (v: string) => void
  highlightedLine?: number
  readOnly?: boolean
}

export function CodeEditor({ value, onChange, highlightedLine, readOnly }: Props) {
  return (
    <CodeMirror
      value={value}
      onChange={onChange}
      readOnly={readOnly}
      extensions={[
        python(),
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
          '.cm-activeLineGutter, .cm-activeLine': {
            backgroundColor: highlightedLine ? '#fffbea' : 'transparent',
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
