// C tokenizer for the teaching subset.
// Whitespace is insignificant (unlike Python). #include lines and // /* */
// comments are stripped. We don't run a real preprocessor.

export type CTokenKind =
  | 'NAME'
  | 'INT'
  | 'CHAR' // single char literal: 'a' → 97
  | 'STRING'
  | 'KEYWORD'
  | 'OP' // + - * / %
  | 'CMP' // == != < > <= >=
  | 'LOGIC' // && ||
  | 'NOT' // !
  | 'AMP' // &  (address-of OR bitwise — we treat only as address-of)
  | 'STAR' // *  (deref OR multiplication — parser disambiguates by context)
  | 'ASSIGN' // =
  | 'INC' // ++
  | 'DEC' // --
  | 'LPAREN'
  | 'RPAREN'
  | 'LBRACE'
  | 'RBRACE'
  | 'LBRACKET'
  | 'RBRACKET'
  | 'SEMI'
  | 'COMMA'
  | 'EOF'

export type CToken = {
  kind: CTokenKind
  value: string
  line: number
  col: number
}

const C_KEYWORDS = new Set([
  'int', 'char', 'void',
  'if', 'else',
  'while', 'for',
  'return',
  'sizeof',
  // We allow these to appear but treat as identifiers/no-ops; the parser
  // can choose to ignore. NULL is treated as a keyword that evaluates to 0.
  'NULL',
])

export class CTokenError extends Error {
  line: number
  col: number
  constructor(message: string, line: number, col: number) {
    super(`SyntaxError on line ${line}: ${message}`)
    this.line = line
    this.col = col
  }
}

export function tokenizeC(src: string): CToken[] {
  const tokens: CToken[] = []
  // Strip block comments. We do this in a single pass so line numbers stay
  // intact (replace comment body with same-length whitespace).
  const cleaned = stripComments(src)

  const lines = cleaned.replace(/\r\n?/g, '\n').split('\n')

  for (let lineIdx = 0; lineIdx < lines.length; lineIdx++) {
    const lineNum = lineIdx + 1
    const line = lines[lineIdx]
    let i = 0

    // Strip preprocessor lines entirely (we don't model #include / #define).
    const trimmed = line.trimStart()
    if (trimmed.startsWith('#')) continue

    while (i < line.length) {
      const ch = line[i]

      // Skip whitespace.
      if (ch === ' ' || ch === '\t') {
        i++
        continue
      }

      // Strip line comments (// ...). Skip rest of line.
      if (ch === '/' && line[i + 1] === '/') break

      // Identifier or keyword.
      if (isIdentStart(ch)) {
        const start = i
        while (i < line.length && isIdentCont(line[i])) i++
        const name = line.slice(start, i)
        if (C_KEYWORDS.has(name)) {
          tokens.push({ kind: 'KEYWORD', value: name, line: lineNum, col: start + 1 })
        } else {
          tokens.push({ kind: 'NAME', value: name, line: lineNum, col: start + 1 })
        }
        continue
      }

      // Integer literal. Hex (0x...) and decimal only.
      if (isDigit(ch)) {
        const start = i
        if (ch === '0' && (line[i + 1] === 'x' || line[i + 1] === 'X')) {
          i += 2
          while (i < line.length && isHex(line[i])) i++
        } else {
          while (i < line.length && isDigit(line[i])) i++
        }
        tokens.push({ kind: 'INT', value: line.slice(start, i), line: lineNum, col: start + 1 })
        continue
      }

      // Character literal: 'a' or '\n'. Single byte only.
      if (ch === "'") {
        const start = i
        i++ // consume opening quote
        let charValue: number
        if (line[i] === '\\') {
          // Escape: \n \t \r \\ \' \0
          i++
          const esc = line[i++]
          switch (esc) {
            case 'n': charValue = 10; break
            case 't': charValue = 9; break
            case 'r': charValue = 13; break
            case '0': charValue = 0; break
            case '\\': charValue = 92; break
            case "'": charValue = 39; break
            case '"': charValue = 34; break
            default:
              throw new CTokenError(`unknown escape '\\${esc}' in char literal`, lineNum, start + 1)
          }
        } else {
          charValue = line.charCodeAt(i)
          i++
        }
        if (line[i] !== "'") {
          throw new CTokenError(`unterminated char literal`, lineNum, start + 1)
        }
        i++ // consume closing quote
        tokens.push({ kind: 'CHAR', value: String(charValue), line: lineNum, col: start + 1 })
        continue
      }

      // String literal: "hello\n". We resolve escapes here.
      if (ch === '"') {
        const start = i
        i++ // consume opening quote
        let s = ''
        while (i < line.length && line[i] !== '"') {
          if (line[i] === '\\') {
            i++
            const esc = line[i++]
            switch (esc) {
              case 'n': s += '\n'; break
              case 't': s += '\t'; break
              case 'r': s += '\r'; break
              case '0': s += '\0'; break
              case '\\': s += '\\'; break
              case "'": s += "'"; break
              case '"': s += '"'; break
              default:
                throw new CTokenError(`unknown escape '\\${esc}' in string literal`, lineNum, start + 1)
            }
          } else {
            s += line[i++]
          }
        }
        if (line[i] !== '"') {
          throw new CTokenError(`unterminated string literal`, lineNum, start + 1)
        }
        i++ // consume closing quote
        tokens.push({ kind: 'STRING', value: s, line: lineNum, col: start + 1 })
        continue
      }

      // Multi-char operators (check first — order matters!).
      const two = line.slice(i, i + 2)
      if (two === '==' || two === '!=' || two === '<=' || two === '>=') {
        tokens.push({ kind: 'CMP', value: two, line: lineNum, col: i + 1 })
        i += 2
        continue
      }
      if (two === '&&' || two === '||') {
        tokens.push({ kind: 'LOGIC', value: two, line: lineNum, col: i + 1 })
        i += 2
        continue
      }
      if (two === '++') {
        tokens.push({ kind: 'INC', value: two, line: lineNum, col: i + 1 })
        i += 2
        continue
      }
      if (two === '--') {
        tokens.push({ kind: 'DEC', value: two, line: lineNum, col: i + 1 })
        i += 2
        continue
      }

      // Single-char punctuation / operators.
      switch (ch) {
        case '+': case '-': case '/': case '%':
          tokens.push({ kind: 'OP', value: ch, line: lineNum, col: i + 1 })
          i++
          continue
        case '*':
          tokens.push({ kind: 'STAR', value: '*', line: lineNum, col: i + 1 })
          i++
          continue
        case '&':
          tokens.push({ kind: 'AMP', value: '&', line: lineNum, col: i + 1 })
          i++
          continue
        case '<': case '>':
          tokens.push({ kind: 'CMP', value: ch, line: lineNum, col: i + 1 })
          i++
          continue
        case '=':
          tokens.push({ kind: 'ASSIGN', value: '=', line: lineNum, col: i + 1 })
          i++
          continue
        case '!':
          tokens.push({ kind: 'NOT', value: '!', line: lineNum, col: i + 1 })
          i++
          continue
        case '(': tokens.push({ kind: 'LPAREN', value: '(', line: lineNum, col: i + 1 }); i++; continue
        case ')': tokens.push({ kind: 'RPAREN', value: ')', line: lineNum, col: i + 1 }); i++; continue
        case '{': tokens.push({ kind: 'LBRACE', value: '{', line: lineNum, col: i + 1 }); i++; continue
        case '}': tokens.push({ kind: 'RBRACE', value: '}', line: lineNum, col: i + 1 }); i++; continue
        case '[': tokens.push({ kind: 'LBRACKET', value: '[', line: lineNum, col: i + 1 }); i++; continue
        case ']': tokens.push({ kind: 'RBRACKET', value: ']', line: lineNum, col: i + 1 }); i++; continue
        case ';': tokens.push({ kind: 'SEMI', value: ';', line: lineNum, col: i + 1 }); i++; continue
        case ',': tokens.push({ kind: 'COMMA', value: ',', line: lineNum, col: i + 1 }); i++; continue
      }

      throw new CTokenError(`unexpected character '${ch}'`, lineNum, i + 1)
    }
  }

  tokens.push({ kind: 'EOF', value: '', line: lines.length + 1, col: 1 })
  return tokens
}

// Replace /* ... */ comment bodies with spaces of equal length so column
// numbers stay correct in error messages. Newlines inside comments preserve
// their newline so line numbers also stay correct.
function stripComments(src: string): string {
  let out = ''
  let i = 0
  while (i < src.length) {
    if (src[i] === '/' && src[i + 1] === '*') {
      out += '  ' // for the opening /*
      i += 2
      while (i < src.length && !(src[i] === '*' && src[i + 1] === '/')) {
        out += src[i] === '\n' ? '\n' : ' '
        i++
      }
      if (i < src.length) {
        out += '  ' // for the closing */
        i += 2
      }
      continue
    }
    out += src[i]
    i++
  }
  return out
}

function isIdentStart(ch: string): boolean {
  return (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || ch === '_'
}

function isIdentCont(ch: string): boolean {
  return isIdentStart(ch) || isDigit(ch)
}

function isDigit(ch: string): boolean {
  return ch >= '0' && ch <= '9'
}

function isHex(ch: string): boolean {
  return isDigit(ch) || (ch >= 'a' && ch <= 'f') || (ch >= 'A' && ch <= 'F')
}
