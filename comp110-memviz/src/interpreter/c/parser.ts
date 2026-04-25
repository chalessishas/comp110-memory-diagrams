// C parser for the teaching subset. Recursive descent with one-function-
// per-precedence-level for expressions. Designed to be readable rather
// than fast — the inputs are <50-line student programs.

import type {
  CExpr, CFunctionDef, CProgram, CStmt, CTopLevel, CType, CVarDecl,
} from './types'
import type { CToken, CTokenKind } from './tokenizer'

export class CParseError extends Error {
  line: number
  constructor(message: string, line: number) {
    super(`SyntaxError on line ${line}: ${message}`)
    this.line = line
  }
}

class Parser {
  tokens: CToken[]
  pos = 0

  constructor(tokens: CToken[]) {
    this.tokens = tokens
  }

  peek(offset = 0): CToken {
    return this.tokens[this.pos + offset]
  }

  consume(): CToken {
    return this.tokens[this.pos++]
  }

  match(kind: CTokenKind, value?: string): boolean {
    const t = this.peek()
    if (t.kind !== kind) return false
    if (value !== undefined && t.value !== value) return false
    return true
  }

  expect(kind: CTokenKind, value?: string): CToken {
    const t = this.peek()
    if (t.kind !== kind || (value !== undefined && t.value !== value)) {
      const want = value !== undefined ? `${kind} '${value}'` : kind
      throw new CParseError(`expected ${want}, got ${t.kind} '${t.value}'`, t.line)
    }
    return this.consume()
  }

  // program := topLevel*
  parseProgram(): CProgram {
    const body: CTopLevel[] = []
    while (!this.match('EOF')) {
      body.push(this.parseTopLevel())
    }
    return { kind: 'program', body }
  }

  // A top-level form is either a global variable declaration or a function
  // definition. Both start with a type, an identifier, and then either '('
  // (function) or anything else (declaration).
  parseTopLevel(): CTopLevel {
    const type = this.parseType()
    const nameTok = this.expect('NAME')

    if (this.match('LPAREN')) {
      return this.parseFunctionDef(type, nameTok.value, nameTok.line)
    }
    // Global variable declaration: int x = 5;  or  int arr[10];
    return this.finishVarDecl(type, nameTok.value, nameTok.line)
  }

  // Parse a base type with optional `*` suffix(es) for pointers.
  // `int`, `int*`, `int**`, `char*`, `void`. Array dimensions are NOT
  // parsed here — they belong to the declarator, parsed after the name.
  parseType(): CType {
    const t = this.peek()
    let base: CType
    if (t.kind !== 'KEYWORD' || (t.value !== 'int' && t.value !== 'char' && t.value !== 'void')) {
      throw new CParseError(`expected type (int / char / void), got '${t.value}'`, t.line)
    }
    this.consume()
    if (t.value === 'int') base = { kind: 'int' }
    else if (t.value === 'char') base = { kind: 'char' }
    else base = { kind: 'void' }

    while (this.match('STAR')) {
      this.consume()
      base = { kind: 'ptr', to: base }
    }
    return base
  }

  parseFunctionDef(returnType: CType, name: string, lineStart: number): CFunctionDef {
    this.expect('LPAREN')
    const params: { name: string; type: CType }[] = []
    if (!this.match('RPAREN')) {
      // void → no params, accept `(void)` form too.
      if (this.match('KEYWORD', 'void') && this.peek(1).kind === 'RPAREN') {
        this.consume()
      } else {
        do {
          const ptype = this.parseType()
          const pname = this.expect('NAME').value
          // Reject array params for now (they're really pointers in C; we
          // just accept the bare name without the `[]`).
          params.push({ name: pname, type: ptype })
        } while (this.match('COMMA') && (this.consume(), true))
      }
    }
    this.expect('RPAREN')
    this.expect('LBRACE')
    const body: CStmt[] = []
    while (!this.match('RBRACE')) {
      body.push(this.parseStmt())
    }
    const lineEnd = this.peek().line
    this.expect('RBRACE')
    return { kind: 'funcDef', name, returnType, params, body, lineStart, lineEnd }
  }

  // Statement entry. Dispatches based on lookahead.
  parseStmt(): CStmt {
    const t = this.peek()

    // Block
    if (t.kind === 'LBRACE') {
      this.consume()
      const body: CStmt[] = []
      while (!this.match('RBRACE')) body.push(this.parseStmt())
      this.expect('RBRACE')
      return { kind: 'block', body, line: t.line }
    }

    // Declaration starts with a type keyword.
    if (t.kind === 'KEYWORD' && (t.value === 'int' || t.value === 'char' || t.value === 'void')) {
      const type = this.parseType()
      const nameTok = this.expect('NAME')
      return this.finishVarDecl(type, nameTok.value, nameTok.line)
    }

    if (t.kind === 'KEYWORD') {
      switch (t.value) {
        case 'if': return this.parseIf()
        case 'while': return this.parseWhile()
        case 'for': return this.parseFor()
        case 'return': return this.parseReturn()
      }
    }

    // Otherwise it's an expression statement OR an assignment / index-assign /
    // deref-assign. We parse as an expression and then look for `=` or `;`.
    const expr = this.parseExpr()

    if (this.match('ASSIGN')) {
      this.consume()
      const value = this.parseExpr()
      this.expect('SEMI')
      // Determine which assignment statement kind based on LHS shape.
      if (expr.kind === 'name') {
        return { kind: 'assign', target: expr.name, value, line: t.line }
      }
      if (expr.kind === 'index') {
        return { kind: 'indexAssign', target: expr.target, index: expr.index, value, line: t.line }
      }
      if (expr.kind === 'deref') {
        return { kind: 'derefAssign', target: expr.operand, value, line: t.line }
      }
      throw new CParseError(`invalid assignment target`, t.line)
    }

    this.expect('SEMI')
    return { kind: 'exprStmt', expr, line: t.line }
  }

  // After consuming `type name`, finish the rest of a variable declaration:
  // `;`, `= expr;`, or `[ dim ];` for an array.
  finishVarDecl(type: CType, name: string, line: number): CVarDecl {
    if (this.match('LBRACKET')) {
      this.consume()
      const dimTok = this.expect('INT')
      this.expect('RBRACKET')
      const arrType: CType = { kind: 'arr', of: type, length: parseInt(dimTok.value, 10) }
      // No initializer support for arrays in this MVP — students declare then
      // assign via a loop or indexing. Reject `int arr[3] = {1,2,3};` etc.
      this.expect('SEMI')
      return { kind: 'varDecl', type: arrType, name, init: null, line }
    }

    let init: CExpr | null = null
    if (this.match('ASSIGN')) {
      this.consume()
      init = this.parseExpr()
    }
    this.expect('SEMI')
    return { kind: 'varDecl', type, name, init, line }
  }

  parseIf(): CStmt {
    const t = this.expect('KEYWORD', 'if')
    this.expect('LPAREN')
    const cond = this.parseExpr()
    this.expect('RPAREN')
    const body = this.parseStmtBlock()
    const branches = [{ condition: cond, body }]
    let elseBody: CStmt[] | null = null
    while (this.match('KEYWORD', 'else')) {
      this.consume()
      if (this.match('KEYWORD', 'if')) {
        this.consume()
        this.expect('LPAREN')
        const c = this.parseExpr()
        this.expect('RPAREN')
        const b = this.parseStmtBlock()
        branches.push({ condition: c, body: b })
      } else {
        elseBody = this.parseStmtBlock()
        break
      }
    }
    return { kind: 'if', branches, elseBody, line: t.line }
  }

  parseWhile(): CStmt {
    const t = this.expect('KEYWORD', 'while')
    this.expect('LPAREN')
    const cond = this.parseExpr()
    this.expect('RPAREN')
    const body = this.parseStmtBlock()
    return { kind: 'while', condition: cond, body, line: t.line }
  }

  parseFor(): CStmt {
    const t = this.expect('KEYWORD', 'for')
    this.expect('LPAREN')

    // init: declaration | expression | empty
    let init: CVarDecl | CExpr | null = null
    if (!this.match('SEMI')) {
      const peek0 = this.peek()
      if (peek0.kind === 'KEYWORD' && (peek0.value === 'int' || peek0.value === 'char')) {
        const type = this.parseType()
        const nameTok = this.expect('NAME')
        // Reuse finishVarDecl, which will consume the trailing `;`.
        init = this.finishVarDecl(type, nameTok.value, nameTok.line)
      } else {
        init = this.parseExprOrAssign()
        this.expect('SEMI')
      }
    } else {
      this.consume() // empty init: `;`
    }

    let cond: CExpr | null = null
    if (!this.match('SEMI')) cond = this.parseExpr()
    this.expect('SEMI')

    let update: CExpr | null = null
    if (!this.match('RPAREN')) update = this.parseExprOrAssign()
    this.expect('RPAREN')

    const body = this.parseStmtBlock()
    return { kind: 'for', init, condition: cond, update, body, line: t.line }
  }

  parseReturn(): CStmt {
    const t = this.expect('KEYWORD', 'return')
    if (this.match('SEMI')) {
      this.consume()
      return { kind: 'return', expr: null, line: t.line }
    }
    const e = this.parseExpr()
    this.expect('SEMI')
    return { kind: 'return', expr: e, line: t.line }
  }

  // Body of if/else/while/for: either `{ ... }` or a single statement.
  parseStmtBlock(): CStmt[] {
    if (this.match('LBRACE')) {
      this.consume()
      const body: CStmt[] = []
      while (!this.match('RBRACE')) body.push(this.parseStmt())
      this.expect('RBRACE')
      return body
    }
    return [this.parseStmt()]
  }

  // For for-loop init/update — accept assignment-as-expression `x = 5` AND
  // bare expressions like `i++` (we don't really model i++ but we accept
  // common `i = i + 1` form).
  parseExprOrAssign(): CExpr {
    const start = this.pos
    const e = this.parseExpr()
    if (this.match('ASSIGN') && e.kind === 'name') {
      this.consume()
      const v = this.parseExpr()
      return { kind: 'assignExpr', target: e.name, value: v, line: this.tokens[start].line }
    }
    return e
  }

  // Expression precedence (low → high): || → && → == != → < > <= >= →
  // + - → * / % → unary → postfix → primary.
  parseExpr(): CExpr {
    return this.parseLogicalOr()
  }

  parseLogicalOr(): CExpr {
    let left = this.parseLogicalAnd()
    while (this.match('LOGIC', '||')) {
      const t = this.consume()
      const right = this.parseLogicalAnd()
      left = { kind: 'logical', op: '||', left, right, line: t.line }
    }
    return left
  }

  parseLogicalAnd(): CExpr {
    let left = this.parseEquality()
    while (this.match('LOGIC', '&&')) {
      const t = this.consume()
      const right = this.parseEquality()
      left = { kind: 'logical', op: '&&', left, right, line: t.line }
    }
    return left
  }

  parseEquality(): CExpr {
    let left = this.parseRelational()
    while (this.match('CMP', '==') || this.match('CMP', '!=')) {
      const t = this.consume()
      const right = this.parseRelational()
      left = { kind: 'cmp', op: t.value as '==' | '!=', left, right, line: t.line }
    }
    return left
  }

  parseRelational(): CExpr {
    let left = this.parseAdditive()
    while (
      this.match('CMP', '<') || this.match('CMP', '>') ||
      this.match('CMP', '<=') || this.match('CMP', '>=')
    ) {
      const t = this.consume()
      const right = this.parseAdditive()
      left = { kind: 'cmp', op: t.value as '<' | '>' | '<=' | '>=', left, right, line: t.line }
    }
    return left
  }

  parseAdditive(): CExpr {
    let left = this.parseMultiplicative()
    while (this.match('OP', '+') || this.match('OP', '-')) {
      const t = this.consume()
      const right = this.parseMultiplicative()
      left = { kind: 'binop', op: t.value as '+' | '-', left, right, line: t.line }
    }
    return left
  }

  parseMultiplicative(): CExpr {
    let left = this.parseUnary()
    while (this.match('STAR') || this.match('OP', '/') || this.match('OP', '%')) {
      const t = this.consume()
      const right = this.parseUnary()
      const op = t.kind === 'STAR' ? '*' : (t.value as '/' | '%')
      left = { kind: 'binop', op: op as '*' | '/' | '%', left, right, line: t.line }
    }
    return left
  }

  parseUnary(): CExpr {
    const t = this.peek()
    if (t.kind === 'OP' && (t.value === '-' || t.value === '+')) {
      this.consume()
      const operand = this.parseUnary()
      return { kind: 'unop', op: t.value as '-' | '+', operand, line: t.line }
    }
    if (t.kind === 'NOT') {
      this.consume()
      const operand = this.parseUnary()
      return { kind: 'not', operand, line: t.line }
    }
    if (t.kind === 'AMP') {
      this.consume()
      const operand = this.parseUnary()
      return { kind: 'addrOf', operand, line: t.line }
    }
    if (t.kind === 'STAR') {
      this.consume()
      const operand = this.parseUnary()
      return { kind: 'deref', operand, line: t.line }
    }
    if (t.kind === 'KEYWORD' && t.value === 'sizeof') {
      this.consume()
      this.expect('LPAREN')
      const ty = this.parseType()
      this.expect('RPAREN')
      return { kind: 'sizeof', type: ty, line: t.line }
    }
    // Cast: `(type) expr`. Distinguish from grouped paren by lookahead.
    if (t.kind === 'LPAREN' && this.isTypeKeyword(this.peek(1))) {
      this.consume() // (
      const ty = this.parseType()
      this.expect('RPAREN')
      const e = this.parseUnary()
      return { kind: 'cast', type: ty, expr: e, line: t.line }
    }
    return this.parsePostfix()
  }

  isTypeKeyword(tok: CToken): boolean {
    return tok.kind === 'KEYWORD' && (tok.value === 'int' || tok.value === 'char' || tok.value === 'void')
  }

  parsePostfix(): CExpr {
    let e = this.parsePrimary()
    while (true) {
      if (this.match('LBRACKET')) {
        const t = this.consume()
        const idx = this.parseExpr()
        this.expect('RBRACKET')
        e = { kind: 'index', target: e, index: idx, line: t.line }
        continue
      }
      if (this.match('LPAREN')) {
        // Function call. Only valid if the current expression is a NameRef
        // (we don't support function pointers).
        if (e.kind !== 'name') {
          throw new CParseError(`cannot call expression`, this.peek().line)
        }
        const t = this.consume()
        const args: CExpr[] = []
        if (!this.match('RPAREN')) {
          args.push(this.parseExpr())
          while (this.match('COMMA')) {
            this.consume()
            args.push(this.parseExpr())
          }
        }
        this.expect('RPAREN')
        e = { kind: 'call', callee: e.name, args, line: t.line }
        continue
      }
      break
    }
    return e
  }

  parsePrimary(): CExpr {
    const t = this.peek()
    if (t.kind === 'INT') {
      this.consume()
      const v = t.value.startsWith('0x') || t.value.startsWith('0X')
        ? parseInt(t.value.slice(2), 16)
        : parseInt(t.value, 10)
      return { kind: 'intLit', v, line: t.line }
    }
    if (t.kind === 'CHAR') {
      this.consume()
      return { kind: 'charLit', v: parseInt(t.value, 10), line: t.line }
    }
    if (t.kind === 'STRING') {
      this.consume()
      return { kind: 'strLit', v: t.value, line: t.line }
    }
    if (t.kind === 'KEYWORD' && t.value === 'NULL') {
      this.consume()
      return { kind: 'intLit', v: 0, line: t.line }
    }
    if (t.kind === 'NAME') {
      this.consume()
      return { kind: 'name', name: t.value, line: t.line }
    }
    if (t.kind === 'LPAREN') {
      this.consume()
      const e = this.parseExpr()
      this.expect('RPAREN')
      return e
    }
    throw new CParseError(`unexpected token '${t.value}'`, t.line)
  }
}

export function parseC(tokens: CToken[]): CProgram {
  const p = new Parser(tokens)
  return p.parseProgram()
}
