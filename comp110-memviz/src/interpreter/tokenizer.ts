// Tokenizer for the COMP110 v0 Python subset.
// Handles indentation via INDENT/DEDENT tokens. Docstrings and comments
// are recognized but surface as tokens the parser will then ignore.

export type TokenKind =
  | 'NEWLINE'
  | 'INDENT'
  | 'DEDENT'
  | 'NAME'
  | 'NUMBER'
  | 'STRING'
  | 'FSTRING' // value is a JSON-encoded list of parts: [{kind:'lit'|'interp', v|src}]
  | 'KEYWORD'
  | 'OP' // + - * / // % **
  | 'CMP' // == != < > <= >=
  | 'AUG' // += -= *= /=  (augmented assignment)
  | 'LPAREN'
  | 'RPAREN'
  | 'LBRACKET'
  | 'RBRACKET'
  | 'LBRACE'
  | 'RBRACE'
  | 'COLON'
  | 'COMMA'
  | 'DOT'
  | 'ARROW'
  | 'ASSIGN'
  | 'EOF'

export type Token = {
  kind: TokenKind
  value: string
  line: number
  col: number
}

const KEYWORDS = new Set([
  'def', 'return', 'None', 'True', 'False',
  'class', 'if', 'elif', 'else',
  'and', 'or', 'not', 'in', 'is',
  'while', 'for',
  'import', 'from', 'as',
])

export class TokenError extends Error {
  line: number
  col: number
  constructor(message: string, line: number, col: number) {
    super(`SyntaxError on line ${line}: ${message}`)
    this.line = line
    this.col = col
  }
}

export function tokenize(src: string): Token[] {
  const tokens: Token[] = []
  const indentStack: number[] = [0]
  const lines = src.replace(/\r\n?/g, '\n').split('\n')

  const emit = (kind: TokenKind, value: string, line: number, col: number) => {
    tokens.push({ kind, value, line, col })
  }

  for (let lineIdx = 0; lineIdx < lines.length; lineIdx++) {
    const lineNum = lineIdx + 1
    const line = lines[lineIdx]

    // Skip completely blank or comment-only lines without emitting NEWLINE so
    // they don't terminate multi-line constructs (there aren't any in v0, but
    // still — blank lines are invisible to the parser).
    const stripped = line.replace(/#.*$/, '').trimEnd()
    if (stripped.trim() === '') continue

    // Compute indent (spaces only — tabs not part of v0).
    let indent = 0
    while (indent < line.length && line[indent] === ' ') indent++

    const top = indentStack[indentStack.length - 1]
    if (indent > top) {
      indentStack.push(indent)
      emit('INDENT', '', lineNum, 0)
    } else {
      while (indent < indentStack[indentStack.length - 1]) {
        indentStack.pop()
        emit('DEDENT', '', lineNum, 0)
      }
      if (indent !== indentStack[indentStack.length - 1]) {
        throw new TokenError('inconsistent indentation', lineNum, indent)
      }
    }

    // Lex the line contents.
    let i = indent
    while (i < line.length) {
      const c = line[i]

      if (c === '#') break // rest-of-line comment
      if (c === ' ' || c === '\t') { i++; continue }

      // f-string: `f"..."` or `f'...'` with `{expr}` interpolation. We lex it
      // into a FSTRING token whose value is JSON-encoded parts.
      if (
        (c === 'f' || c === 'F') &&
        (line[i + 1] === '"' || line[i + 1] === "'")
      ) {
        const quote = line[i + 1]
        const parts: ({ kind: 'lit'; v: string } | { kind: 'interp'; src: string })[] = []
        let j = i + 2
        let buf = ''
        while (j < line.length && line[j] !== quote) {
          if (line[j] === '{' && line[j + 1] === '{') { buf += '{'; j += 2; continue }
          if (line[j] === '}' && line[j + 1] === '}') { buf += '}'; j += 2; continue }
          if (line[j] === '{') {
            if (buf.length) { parts.push({ kind: 'lit', v: buf }); buf = '' }
            j++
            const start = j
            let depth = 1
            while (j < line.length && depth > 0) {
              if (line[j] === '{') depth++
              else if (line[j] === '}') depth--
              if (depth > 0) j++
            }
            if (depth !== 0) throw new TokenError('unterminated { in f-string', lineNum, i)
            parts.push({ kind: 'interp', src: line.slice(start, j) })
            j++ // consume the '}'
            continue
          }
          if (line[j] === '\\' && j + 1 < line.length) {
            const esc = line[j + 1]
            buf += esc === 'n' ? '\n' : esc === 't' ? '\t' : esc
            j += 2
            continue
          }
          buf += line[j]
          j++
        }
        if (j >= line.length) throw new TokenError('unterminated f-string', lineNum, i)
        if (buf.length) parts.push({ kind: 'lit', v: buf })
        emit('FSTRING', JSON.stringify(parts), lineNum, i)
        i = j + 1
        continue
      }

      // Strings: '...' or "..." (no escapes in v0 beyond \n, \t, \\, \", \')
      if (c === '"' || c === "'") {
        // Triple-quoted docstrings
        if (line.slice(i, i + 3) === c + c + c) {
          const quote = c + c + c
          let content = ''
          let j = i + 3
          let curLine = lineIdx
          let curLineText = line
          while (true) {
            const endIdx = curLineText.indexOf(quote, j)
            if (endIdx >= 0) {
              content += curLineText.slice(j, endIdx)
              emit('STRING', content, lineNum, i)
              // Advance outer loop position to end of the triple quote on this
              // (possibly different) line.
              if (curLine === lineIdx) {
                i = endIdx + 3
              } else {
                // Skip to next iteration — adjust state so outer loop continues
                // at the next line by breaking and manually bumping lineIdx.
                lineIdx = curLine
                lineIdx -- // because for loop will ++
                i = line.length // terminate inner while
              }
              break
            }
            // Not closed on this line — consume whole line and continue.
            content += curLineText.slice(j) + '\n'
            curLine++
            if (curLine >= lines.length) {
              throw new TokenError('unterminated triple-quoted string', lineNum, i)
            }
            curLineText = lines[curLine]
            j = 0
          }
          continue
        }
        // Single-line quoted string
        const quote = c
        let j = i + 1
        let content = ''
        while (j < line.length && line[j] !== quote) {
          if (line[j] === '\\' && j + 1 < line.length) {
            const esc = line[j + 1]
            content += esc === 'n' ? '\n' : esc === 't' ? '\t' : esc
            j += 2
          } else {
            content += line[j]
            j++
          }
        }
        if (j >= line.length) throw new TokenError('unterminated string', lineNum, i)
        emit('STRING', content, lineNum, i)
        i = j + 1
        continue
      }

      // Numbers
      if (/[0-9]/.test(c)) {
        let j = i
        while (j < line.length && /[0-9]/.test(line[j])) j++
        if (line[j] === '.') {
          j++
          while (j < line.length && /[0-9]/.test(line[j])) j++
        }
        emit('NUMBER', line.slice(i, j), lineNum, i)
        i = j
        continue
      }

      // Identifiers / keywords
      if (/[A-Za-z_]/.test(c)) {
        let j = i
        while (j < line.length && /[A-Za-z0-9_]/.test(line[j])) j++
        const word = line.slice(i, j)
        emit(KEYWORDS.has(word) ? 'KEYWORD' : 'NAME', word, lineNum, i)
        i = j
        continue
      }

      // Two-character operators
      const two = line.slice(i, i + 2)
      if (two === '->') { emit('ARROW', two, lineNum, i); i += 2; continue }
      if (two === '**' || two === '//') { emit('OP', two, lineNum, i); i += 2; continue }
      if (two === '==' || two === '!=' || two === '<=' || two === '>=') {
        emit('CMP', two, lineNum, i); i += 2; continue
      }
      if (two === '+=' || two === '-=' || two === '*=' || two === '/=') {
        emit('AUG', two, lineNum, i); i += 2; continue
      }

      // Single-character operators / punctuation
      if (c === '(') { emit('LPAREN', c, lineNum, i); i++; continue }
      if (c === ')') { emit('RPAREN', c, lineNum, i); i++; continue }
      if (c === '[') { emit('LBRACKET', c, lineNum, i); i++; continue }
      if (c === ']') { emit('RBRACKET', c, lineNum, i); i++; continue }
      if (c === '{') { emit('LBRACE', c, lineNum, i); i++; continue }
      if (c === '}') { emit('RBRACE', c, lineNum, i); i++; continue }
      if (c === ':') { emit('COLON', c, lineNum, i); i++; continue }
      if (c === ',') { emit('COMMA', c, lineNum, i); i++; continue }
      if (c === '.') { emit('DOT', c, lineNum, i); i++; continue }
      if (c === '=') { emit('ASSIGN', c, lineNum, i); i++; continue }
      if (c === '<' || c === '>') { emit('CMP', c, lineNum, i); i++; continue }
      if ('+-*/%'.includes(c)) { emit('OP', c, lineNum, i); i++; continue }
      // Pipe is only used in union type annotations (v3 extension);
      // tokenize as OP and let parseTypeAnnotation interpret it.
      if (c === '|') { emit('OP', c, lineNum, i); i++; continue }

      throw new TokenError(`unexpected character ${JSON.stringify(c)}`, lineNum, i)
    }

    emit('NEWLINE', '', lineNum, line.length)
  }

  // Close any remaining indents.
  const lastLine = lines.length
  while (indentStack.length > 1) {
    indentStack.pop()
    emit('DEDENT', '', lastLine, 0)
  }
  emit('EOF', '', lastLine, 0)
  return tokens
}
