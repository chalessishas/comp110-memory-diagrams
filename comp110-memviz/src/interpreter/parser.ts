// Recursive-descent parser for the COMP110 v0 Python subset.
// Produces an AST matching types.ts. Throws ParseError with a line number.

import type {
  AssignStmt,
  BinaryOp,
  CallExpr,
  Expr,
  ExprStmt,
  FunctionDef,
  IndexExpr,
  NameRef,
  NumLit,
  Param,
  Program,
  ReturnStmt,
  Stmt,
  StrLit,
  TypeAnnotation,
  UnaryOp,
} from './types'
import { tokenize, type Token } from './tokenizer'

export class ParseError extends Error {
  line: number
  constructor(message: string, line: number) {
    super(`SyntaxError on line ${line}: ${message}`)
    this.line = line
  }
}

class Parser {
  private pos = 0
  private tokens: Token[]

  constructor(tokens: Token[]) {
    this.tokens = tokens
  }

  private peek(offset = 0): Token {
    return this.tokens[this.pos + offset]
  }

  private consume(): Token {
    return this.tokens[this.pos++]
  }

  private expect(kind: Token['kind'], value?: string): Token {
    const t = this.peek()
    if (t.kind !== kind || (value !== undefined && t.value !== value)) {
      throw new ParseError(
        `expected ${kind}${value ? ` '${value}'` : ''} but got ${t.kind} '${t.value}'`,
        t.line,
      )
    }
    return this.consume()
  }

  private match(kind: Token['kind'], value?: string): boolean {
    const t = this.peek()
    if (t.kind !== kind) return false
    if (value !== undefined && t.value !== value) return false
    return true
  }

  private skipNewlines() {
    while (this.match('NEWLINE')) this.consume()
  }

  // Program -----------------------------------------------------------

  parseProgram(): Program {
    const body: Stmt[] = []
    this.skipNewlines()
    while (!this.match('EOF')) {
      body.push(this.parseStmt())
      this.skipNewlines()
    }
    return { kind: 'program', body }
  }

  // Statements --------------------------------------------------------

  private parseStmt(): Stmt {
    const t = this.peek()
    if (t.kind === 'KEYWORD' && t.value === 'def') return this.parseFuncDef()
    if (t.kind === 'KEYWORD' && t.value === 'return') return this.parseReturn()
    // Assignment: NAME '=' expr  OR  NAME ':' TYPE '=' expr. We peek ahead to
    // distinguish from an expression statement starting with a name (like a
    // function call `foo(...)`), since those don't have an ASSIGN in that slot.
    if (t.kind === 'NAME') {
      const n1 = this.peek(1)
      if (n1?.kind === 'ASSIGN') return this.parseAssign(false)
      if (n1?.kind === 'COLON') return this.parseAssign(true)
    }
    return this.parseExprStmt()
  }

  private parseAssign(typed: boolean): AssignStmt {
    const nameTok = this.expect('NAME')
    let typeAnnotation: TypeAnnotation | null = null
    if (typed) {
      this.expect('COLON')
      typeAnnotation = this.parseTypeAnnotation()
    }
    this.expect('ASSIGN')
    const value = this.parseExpr()
    this.expect('NEWLINE')
    return {
      kind: 'assign',
      target: nameTok.value,
      typeAnnotation,
      value,
      line: nameTok.line,
    }
  }

  private parseFuncDef(): FunctionDef {
    const defTok = this.expect('KEYWORD', 'def')
    const lineStart = defTok.line
    const nameTok = this.expect('NAME')
    this.expect('LPAREN')
    const params: Param[] = []
    if (!this.match('RPAREN')) {
      params.push(this.parseParam())
      while (this.match('COMMA')) {
        this.consume()
        params.push(this.parseParam())
      }
    }
    this.expect('RPAREN')
    this.expect('ARROW')
    const returnType = this.parseTypeAnnotation()
    this.expect('COLON')
    this.expect('NEWLINE')
    this.expect('INDENT')
    this.skipNewlines()

    const body: Stmt[] = []
    // Optional docstring at the start of the body — the tokenizer emits it
    // as a STRING token that is immediately followed by a NEWLINE. Skip it.
    if (this.match('STRING')) {
      this.consume()
      if (this.match('NEWLINE')) this.consume()
      this.skipNewlines()
    }
    while (!this.match('DEDENT') && !this.match('EOF')) {
      body.push(this.parseStmt())
      this.skipNewlines()
    }
    // The DEDENT is produced by the tokenizer at the line where indent drops.
    // lineEnd is the line number that DEDENT fires on — minus 1 gives the
    // last indented line.
    const dedent = this.peek()
    if (this.match('DEDENT')) this.consume()
    const lineEnd = dedent ? Math.max(lineStart, dedent.line - 1) : lineStart
    return {
      kind: 'funcDef',
      name: nameTok.value,
      params,
      returnType,
      body,
      lineStart,
      lineEnd,
    }
  }

  private parseParam(): Param {
    const nameTok = this.expect('NAME')
    this.expect('COLON')
    const type = this.parseTypeAnnotation()
    return { name: nameTok.value, type }
  }

  private parseTypeAnnotation(): string {
    // v0 only uses simple type names (int, float, str, None, bool). Accept any NAME or KEYWORD 'None'.
    const t = this.peek()
    if (t.kind === 'NAME') { this.consume(); return t.value }
    if (t.kind === 'KEYWORD' && (t.value === 'None' || t.value === 'True' || t.value === 'False')) {
      this.consume()
      return t.value
    }
    throw new ParseError(`expected type annotation, got '${t.value}'`, t.line)
  }

  private parseReturn(): ReturnStmt {
    const retTok = this.expect('KEYWORD', 'return')
    // Bare `return` or `return <expr>`.
    if (this.match('NEWLINE')) {
      return { kind: 'return', expr: null, line: retTok.line }
    }
    const expr = this.parseExpr()
    this.expect('NEWLINE')
    return { kind: 'return', expr, line: retTok.line }
  }

  private parseExprStmt(): ExprStmt {
    const t = this.peek()
    const expr = this.parseExpr()
    this.expect('NEWLINE')
    return { kind: 'exprStmt', expr, line: t.line }
  }

  // Expressions (precedence climbing) --------------------------------

  private parseExpr(): Expr {
    return this.parseAdd()
  }

  private parseAdd(): Expr {
    let left = this.parseMul()
    while ((this.match('OP', '+') || this.match('OP', '-'))) {
      const op = this.consume().value as '+' | '-'
      const right = this.parseMul()
      left = { kind: 'binop', op, left, right, line: left.line } satisfies BinaryOp
    }
    return left
  }

  private parseMul(): Expr {
    let left = this.parsePow()
    while (
      this.match('OP', '*') ||
      this.match('OP', '/') ||
      this.match('OP', '//') ||
      this.match('OP', '%')
    ) {
      const op = this.consume().value as '*' | '/' | '//' | '%'
      const right = this.parsePow()
      left = { kind: 'binop', op, left, right, line: left.line } satisfies BinaryOp
    }
    return left
  }

  private parsePow(): Expr {
    const left = this.parseUnary()
    if (this.match('OP', '**')) {
      this.consume()
      const right = this.parsePow() // right-associative
      return { kind: 'binop', op: '**', left, right, line: left.line } satisfies BinaryOp
    }
    return left
  }

  private parseUnary(): Expr {
    if (this.match('OP', '-') || this.match('OP', '+')) {
      const t = this.consume()
      const operand = this.parseUnary()
      return { kind: 'unop', op: t.value as '+' | '-', operand, line: t.line } satisfies UnaryOp
    }
    return this.parsePostfix()
  }

  private parsePostfix(): Expr {
    let expr = this.parsePrimary()
    while (this.match('LPAREN') || this.match('LBRACKET')) {
      if (this.match('LPAREN')) {
        // Call — the callee must be a bare name in v0.
        if (expr.kind !== 'name') {
          throw new ParseError('only simple names may be called', expr.line)
        }
        this.consume()
        const args: CallExpr['args'] = []
        if (!this.match('RPAREN')) {
          args.push(this.parseArg())
          while (this.match('COMMA')) {
            this.consume()
            args.push(this.parseArg())
          }
        }
        this.expect('RPAREN')
        expr = { kind: 'call', callee: expr.name, args, line: expr.line } satisfies CallExpr
      } else {
        this.consume() // LBRACKET
        const index = this.parseExpr()
        this.expect('RBRACKET')
        expr = { kind: 'index', target: expr, index, line: expr.line } satisfies IndexExpr
      }
    }
    return expr
  }

  private parseArg(): { name: string | null; value: Expr } {
    // kwarg form: NAME '=' expr
    if (this.peek().kind === 'NAME' && this.peek(1).kind === 'ASSIGN') {
      const name = this.consume().value
      this.consume() // '='
      const value = this.parseExpr()
      return { name, value }
    }
    return { name: null, value: this.parseExpr() }
  }

  private parsePrimary(): Expr {
    const t = this.peek()
    if (t.kind === 'NUMBER') {
      this.consume()
      const isFloat = t.value.includes('.')
      return { kind: 'num', v: Number(t.value), isFloat, line: t.line } satisfies NumLit
    }
    if (t.kind === 'STRING') {
      this.consume()
      return { kind: 'str', v: t.value, line: t.line } satisfies StrLit
    }
    if (t.kind === 'NAME') {
      this.consume()
      return { kind: 'name', name: t.value, line: t.line } satisfies NameRef
    }
    // None / True / False are tokenized as KEYWORDs but behave as literal names.
    if (t.kind === 'KEYWORD' && (t.value === 'None' || t.value === 'True' || t.value === 'False')) {
      this.consume()
      return { kind: 'name', name: t.value, line: t.line } satisfies NameRef
    }
    if (t.kind === 'LPAREN') {
      this.consume()
      const inner = this.parseExpr()
      this.expect('RPAREN')
      return inner
    }
    throw new ParseError(`unexpected token '${t.value}'`, t.line)
  }
}

export function parse(src: string): Program {
  const tokens = tokenize(src)
  const p = new Parser(tokens)
  return p.parseProgram()
}
