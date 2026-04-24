// Recursive-descent parser for the COMP110 v0 Python subset.
// Produces an AST matching types.ts. Throws ParseError with a line number.

import type {
  AssignStmt,
  AttrAssignStmt,
  AttrExpr,
  BinaryOp,
  BoolLit,
  BoolOp,
  CallExpr,
  ClassDef,
  CompareOp,
  DictLit,
  Expr,
  ExprStmt,
  SliceExpr,
  TernaryExpr,
  FStringLit,
  ForStmt,
  FunctionDef,
  IfStmt,
  IndexAssignStmt,
  IndexExpr,
  ListLit,
  NameRef,
  NotOp,
  NumLit,
  Param,
  Program,
  ReturnStmt,
  Stmt,
  StrLit,
  TypeAnnotation,
  UnaryOp,
  WhileStmt,
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
    if (t.kind === 'KEYWORD' && t.value === 'class') return this.parseClassDef()
    if (t.kind === 'KEYWORD' && t.value === 'if') return this.parseIf()
    if (t.kind === 'KEYWORD' && t.value === 'while') return this.parseWhile()
    if (t.kind === 'KEYWORD' && t.value === 'for') return this.parseFor()
    if (t.kind === 'KEYWORD' && t.value === 'return') return this.parseReturn()
    // Import statements are parsed and silently ignored — they don't affect
    // the memory diagram since all supported names are built in.
    if (
      (t.kind === 'KEYWORD' && t.value === 'import') ||
      (t.kind === 'KEYWORD' && t.value === 'from')
    ) {
      return this.parseImportSkip()
    }
    // Bare typed declaration with no value: `a: list[int]`. We handle that
    // via parseAssign(true) when the next-next token is ASSIGN. Otherwise
    // fall through.
    if (t.kind === 'NAME') {
      const n1 = this.peek(1)
      if (n1?.kind === 'COLON') return this.parseTypedDecl()
    }
    // For everything else we parse a postfix expression (covers NameRef,
    // AttrExpr, IndexExpr, CallExpr) and then classify based on what follows.
    const startPos = this.pos
    const lhs = this.parsePostfix()
    // simple-name '=' expr  → AssignStmt (declaration done earlier)
    if (lhs.kind === 'name' && this.match('ASSIGN')) {
      this.consume()
      const value = this.parseExpr()
      this.expect('NEWLINE')
      return {
        kind: 'assign',
        target: lhs.name,
        typeAnnotation: null,
        value,
        line: lhs.line,
      } satisfies AssignStmt
    }
    // simple-name AUG expr  →  desugar to AssignStmt with NameRef + BinaryOp
    if (lhs.kind === 'name' && this.match('AUG')) {
      const augTok = this.consume()
      const rhs = this.parseExpr()
      this.expect('NEWLINE')
      const op = augTok.value.slice(0, -1) as '+' | '-' | '*' | '/'
      return {
        kind: 'assign',
        target: lhs.name,
        typeAnnotation: null,
        value: { kind: 'binop', op, left: lhs, right: rhs, line: augTok.line } satisfies BinaryOp,
        line: lhs.line,
      } satisfies AssignStmt
    }
    // attr ASSIGN expr  →  AttrAssign
    if (lhs.kind === 'attr' && this.match('ASSIGN')) {
      this.consume()
      const value = this.parseExpr()
      this.expect('NEWLINE')
      return {
        kind: 'attrAssign',
        target: lhs.target,
        attr: lhs.name,
        value,
        line: lhs.line,
      } satisfies AttrAssignStmt
    }
    // attr AUG expr  →  desugar to AttrAssign with BinaryOp(attr_read, op, expr)
    if (lhs.kind === 'attr' && this.match('AUG')) {
      const augTok = this.consume()
      const rhs = this.parseExpr()
      this.expect('NEWLINE')
      const op = augTok.value.slice(0, -1) as '+' | '-' | '*' | '/'
      return {
        kind: 'attrAssign',
        target: lhs.target,
        attr: lhs.name,
        value: { kind: 'binop', op, left: lhs, right: rhs, line: augTok.line } satisfies BinaryOp,
        line: lhs.line,
      } satisfies AttrAssignStmt
    }
    // index ASSIGN expr  →  IndexAssign
    if (lhs.kind === 'index' && this.match('ASSIGN')) {
      this.consume()
      const value = this.parseExpr()
      this.expect('NEWLINE')
      return {
        kind: 'indexAssign',
        target: lhs.target,
        index: lhs.index,
        value,
        line: lhs.line,
      } satisfies IndexAssignStmt
    }
    // index AUG expr  →  desugar to IndexAssign with BinaryOp(index_read, op, expr)
    if (lhs.kind === 'index' && this.match('AUG')) {
      const augTok = this.consume()
      const rhs = this.parseExpr()
      this.expect('NEWLINE')
      const op = augTok.value.slice(0, -1) as '+' | '-' | '*' | '/'
      return {
        kind: 'indexAssign',
        target: lhs.target,
        index: lhs.index,
        value: { kind: 'binop', op, left: lhs, right: rhs, line: augTok.line } satisfies BinaryOp,
        line: lhs.line,
      } satisfies IndexAssignStmt
    }
    // Fall through: expression statement. Back up so parseExprStmt sees the
    // full expression from the first token (it needs the low-precedence layers
    // too, not just postfix).
    this.pos = startPos
    return this.parseExprStmt()
  }

  // Consume an import/from-import line and return a no-op expression stmt.
  // We don't model imports — every name the memory diagram cares about is
  // already a builtin or defined in the program.
  private parseImportSkip(): Stmt {
    const firstTok = this.consume() // 'import' or 'from'
    while (!this.match('NEWLINE') && !this.match('EOF')) this.consume()
    if (this.match('NEWLINE')) this.consume()
    // Return a dummy expression statement that does nothing at runtime.
    return {
      kind: 'exprStmt',
      expr: { kind: 'name', name: 'None', line: firstTok.line },
      line: firstTok.line,
    }
  }

  private parseWhile(): WhileStmt {
    const wTok = this.expect('KEYWORD', 'while')
    const condition = this.parseExpr()
    this.expect('COLON')
    this.expect('NEWLINE')
    this.expect('INDENT')
    this.skipNewlines()
    const body: Stmt[] = []
    while (!this.match('DEDENT') && !this.match('EOF')) {
      body.push(this.parseStmt())
      this.skipNewlines()
    }
    if (this.match('DEDENT')) this.consume()
    return { kind: 'while', condition, body, line: wTok.line }
  }

  private parseFor(): ForStmt {
    const fTok = this.expect('KEYWORD', 'for')
    const tNameTok = this.expect('NAME')
    this.expect('KEYWORD', 'in')
    const iter = this.parseExpr()
    this.expect('COLON')
    this.expect('NEWLINE')
    this.expect('INDENT')
    this.skipNewlines()
    const body: Stmt[] = []
    while (!this.match('DEDENT') && !this.match('EOF')) {
      body.push(this.parseStmt())
      this.skipNewlines()
    }
    if (this.match('DEDENT')) this.consume()
    return { kind: 'for', target: tNameTok.value, iter, body, line: fTok.line }
  }

  private parseClassDef(): ClassDef {
    const classTok = this.expect('KEYWORD', 'class')
    const lineStart = classTok.line
    const nameTok = this.expect('NAME')
    this.expect('COLON')
    this.expect('NEWLINE')
    this.expect('INDENT')
    this.skipNewlines()

    // Optional docstring
    if (this.match('STRING')) {
      this.consume()
      if (this.match('NEWLINE')) this.consume()
      this.skipNewlines()
    }

    const fieldDecls: { name: string; type: TypeAnnotation }[] = []
    const methods: FunctionDef[] = []
    while (!this.match('DEDENT') && !this.match('EOF')) {
      if (this.match('KEYWORD', 'def')) {
        methods.push(this.parseFuncDef())
      } else if (this.peek().kind === 'NAME' && this.peek(1)?.kind === 'COLON') {
        // Bare field declaration: `name: str` — no default value allowed in v1.
        const fnameTok = this.expect('NAME')
        this.expect('COLON')
        const type = this.parseTypeAnnotation()
        this.expect('NEWLINE')
        fieldDecls.push({ name: fnameTok.value, type })
      } else {
        throw new ParseError(
          `unexpected '${this.peek().value}' in class body (expected field decl or 'def')`,
          this.peek().line,
        )
      }
      this.skipNewlines()
    }
    const dedent = this.peek()
    if (this.match('DEDENT')) this.consume()
    const lineEnd = dedent ? Math.max(lineStart, dedent.line - 1) : lineStart
    return { kind: 'classDef', name: nameTok.value, fieldDecls, methods, lineStart, lineEnd }
  }

  private parseIf(): IfStmt {
    const ifTok = this.expect('KEYWORD', 'if')
    const branches: IfStmt['branches'] = []
    const firstCond = this.parseExpr()
    this.expect('COLON')
    this.expect('NEWLINE')
    this.expect('INDENT')
    this.skipNewlines()
    const firstBody: Stmt[] = []
    while (!this.match('DEDENT') && !this.match('EOF')) {
      firstBody.push(this.parseStmt())
      this.skipNewlines()
    }
    if (this.match('DEDENT')) this.consume()
    branches.push({ condition: firstCond, body: firstBody })

    while (this.match('KEYWORD', 'elif')) {
      this.consume()
      const cond = this.parseExpr()
      this.expect('COLON')
      this.expect('NEWLINE')
      this.expect('INDENT')
      this.skipNewlines()
      const body: Stmt[] = []
      while (!this.match('DEDENT') && !this.match('EOF')) {
        body.push(this.parseStmt())
        this.skipNewlines()
      }
      if (this.match('DEDENT')) this.consume()
      branches.push({ condition: cond, body })
    }

    let elseBody: Stmt[] | null = null
    if (this.match('KEYWORD', 'else')) {
      this.consume()
      this.expect('COLON')
      this.expect('NEWLINE')
      this.expect('INDENT')
      this.skipNewlines()
      elseBody = []
      while (!this.match('DEDENT') && !this.match('EOF')) {
        elseBody.push(this.parseStmt())
        this.skipNewlines()
      }
      if (this.match('DEDENT')) this.consume()
    }

    return { kind: 'if', branches, elseBody, line: ifTok.line }
  }

  // Parses a typed declaration — the caller has verified that the next
  // tokens are `NAME COLON ...`. Handles three shapes:
  //   1) NAME : TYPE = expr         → regular AssignStmt with typeAnnotation
  //   2) NAME : TYPE                → bare type hint (Python forward decl);
  //                                    returned as a no-op exprStmt
  // (Untyped NAME = expr is handled in parseStmt via parsePostfix + ASSIGN.)
  private parseTypedDecl(): Stmt {
    const nameTok = this.expect('NAME')
    this.expect('COLON')
    const typeAnnotation = this.parseTypeAnnotation()
    if (this.match('NEWLINE')) {
      this.consume()
      return {
        kind: 'exprStmt',
        expr: { kind: 'name', name: 'None', line: nameTok.line },
        line: nameTok.line,
      }
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
    } satisfies AssignStmt
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
    // Return type annotation `-> Type` is optional (e.g. __init__ omits it).
    let returnType: TypeAnnotation = 'None'
    if (this.match('ARROW')) {
      this.consume()
      returnType = this.parseTypeAnnotation()
    }
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
    // In v1 method definitions, `self` omits the type annotation. Other params
    // should normally have `: type` but we accept untyped ones for forgiveness.
    if (!this.match('COLON')) {
      return { name: nameTok.value, type: nameTok.value === 'self' ? 'Self' : 'Any' }
    }
    this.consume() // COLON
    const type = this.parseTypeAnnotation()
    return { name: nameTok.value, type }
  }

  private parseTypeAnnotation(): string {
    // Accept simple types, parametric ones (list[int], dict[str, int]),
    // and Python 3.10+ union types (Node | None). Retained as a flat string.
    let result = this.parseSimpleType()
    while (this.match('OP', '|')) {
      this.consume()
      result += ' | ' + this.parseSimpleType()
    }
    return result
  }

  private parseSimpleType(): string {
    const t = this.peek()
    if (t.kind === 'NAME') {
      this.consume()
      let result = t.value
      if (this.match('LBRACKET')) {
        this.consume()
        result += '['
        result += this.parseTypeAnnotation()
        while (this.match('COMMA')) {
          this.consume()
          result += ', ' + this.parseTypeAnnotation()
        }
        this.expect('RBRACKET')
        result += ']'
      }
      return result
    }
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
  // Python precedence (low → high): or → and → not → comparisons → + - → * / // % → unary → ** → postfix → primary

  private parseExpr(): Expr {
    const value = this.parseOr()
    // Ternary: `value if condition else alternative`. Python's conditional
    // expression. `if` at expression position means ternary, not statement.
    if (this.match('KEYWORD', 'if')) {
      const tok = this.consume()
      const condition = this.parseOr()
      this.expect('KEYWORD', 'else')
      const alternative = this.parseExpr() // right-associative
      return {
        kind: 'ternary',
        consequent: value,
        condition,
        alternative,
        line: tok.line,
      } satisfies TernaryExpr
    }
    return value
  }

  private parseOr(): Expr {
    let left = this.parseAnd()
    while (this.match('KEYWORD', 'or')) {
      const tok = this.consume()
      const right = this.parseAnd()
      left = { kind: 'boolOp', op: 'or', left, right, line: tok.line } satisfies BoolOp
    }
    return left
  }

  private parseAnd(): Expr {
    let left = this.parseNot()
    while (this.match('KEYWORD', 'and')) {
      const tok = this.consume()
      const right = this.parseNot()
      left = { kind: 'boolOp', op: 'and', left, right, line: tok.line } satisfies BoolOp
    }
    return left
  }

  private parseNot(): Expr {
    if (this.match('KEYWORD', 'not')) {
      const tok = this.consume()
      const operand = this.parseNot()
      return { kind: 'not', operand, line: tok.line } satisfies NotOp
    }
    return this.parseCompare()
  }

  private parseCompare(): Expr {
    // Python supports chained comparisons: `a < b < c` means
    // `(a < b) and (b < c)`. We collect every (op, right) pair then fold
    // into an `and` chain. Mixed ops work: `0 <= i < len(xs)` is valid.
    let left = this.parseAdd()
    const chain: { op: CompareOp['op']; right: Expr; line: number }[] = []
    while (true) {
      if (this.match('CMP')) {
        const tok = this.consume()
        chain.push({
          op: tok.value as CompareOp['op'],
          right: this.parseAdd(),
          line: tok.line,
        })
      } else if (this.match('KEYWORD', 'in')) {
        const tok = this.consume()
        chain.push({ op: 'in', right: this.parseAdd(), line: tok.line })
      } else if (
        this.match('KEYWORD', 'not') &&
        this.peek(1)?.kind === 'KEYWORD' &&
        this.peek(1)?.value === 'in'
      ) {
        this.consume()
        const tok = this.consume()
        chain.push({ op: 'not in', right: this.parseAdd(), line: tok.line })
      } else if (this.match('KEYWORD', 'is')) {
        const tok = this.consume()
        const negated = this.match('KEYWORD', 'not')
        if (negated) this.consume()
        chain.push({
          op: negated ? '!=' : '==',
          right: this.parseAdd(),
          line: tok.line,
        })
      } else {
        break
      }
    }
    if (chain.length === 0) return left
    // Build chain: left OP1 r1 AND r1 OP2 r2 AND ...
    let prev = left
    let acc: Expr | null = null
    for (const c of chain) {
      const cmp: CompareOp = {
        kind: 'cmp',
        op: c.op,
        left: prev,
        right: c.right,
        line: c.line,
      }
      acc = acc === null ? cmp : {
        kind: 'boolOp',
        op: 'and',
        left: acc,
        right: cmp,
        line: c.line,
      }
      prev = c.right
    }
    return acc!
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
    while (this.match('LPAREN') || this.match('LBRACKET') || this.match('DOT')) {
      if (this.match('DOT')) {
        this.consume()
        const nameTok = this.expect('NAME')
        expr = {
          kind: 'attr',
          target: expr,
          name: nameTok.value,
          line: expr.line,
        } satisfies AttrExpr
      } else if (this.match('LPAREN')) {
        // A call. Two forms:
        //   (a) bare name: `foo(...)`                 → callee = name
        //   (b) attribute: `obj.meth(...)`            → callee is an attr expr
        // We keep CallExpr.callee as a string for the common case but stash
        // the full attr target in `methodOf` for the method case.
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
        if (expr.kind === 'name') {
          expr = { kind: 'call', callee: expr.name, args, line: expr.line } satisfies CallExpr
        } else if (expr.kind === 'attr') {
          expr = {
            kind: 'call',
            callee: expr.name, // method name
            methodOf: expr.target,
            args,
            line: expr.line,
          } satisfies CallExpr
        } else {
          throw new ParseError('only names or attributes may be called', expr.line)
        }
      } else {
        this.consume() // LBRACKET
        // Slice if we see `:` before or after the first expression.
        // Forms: `[a:b]`, `[:b]`, `[a:]`, `[:]`.
        if (this.match('COLON')) {
          // Form `[:b]` or `[:]`
          this.consume()
          let stop: Expr | null = null
          if (!this.match('RBRACKET')) stop = this.parseExpr()
          this.expect('RBRACKET')
          expr = { kind: 'slice', target: expr, start: null, stop, line: expr.line } satisfies SliceExpr
        } else {
          const first = this.parseExpr()
          if (this.match('COLON')) {
            this.consume()
            let stop: Expr | null = null
            if (!this.match('RBRACKET')) stop = this.parseExpr()
            this.expect('RBRACKET')
            expr = { kind: 'slice', target: expr, start: first, stop, line: expr.line } satisfies SliceExpr
          } else {
            this.expect('RBRACKET')
            expr = { kind: 'index', target: expr, index: first, line: expr.line } satisfies IndexExpr
          }
        }
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
    if (t.kind === 'FSTRING') {
      this.consume()
      const raw = JSON.parse(t.value) as ({ kind: 'lit'; v: string } | { kind: 'interp'; src: string })[]
      // Parse each interpolated expression by running the tokenizer + parser
      // recursively on the embedded source. The outer expression's line number
      // is preserved so error messages still point at the right line.
      const parts: FStringLit['parts'] = raw.map((p) => {
        if (p.kind === 'lit') return { kind: 'lit', v: p.v }
        const subTokens = tokenize(p.src + '\n')
        const subParser = new Parser(subTokens)
        const expr = subParser.parseExpr()
        return { kind: 'interp', expr }
      })
      return { kind: 'fstr', parts, line: t.line } satisfies FStringLit
    }
    if (t.kind === 'NAME') {
      this.consume()
      return { kind: 'name', name: t.value, line: t.line } satisfies NameRef
    }
    if (t.kind === 'KEYWORD' && t.value === 'None') {
      this.consume()
      return { kind: 'name', name: 'None', line: t.line } satisfies NameRef
    }
    if (t.kind === 'KEYWORD' && (t.value === 'True' || t.value === 'False')) {
      this.consume()
      return { kind: 'bool', v: t.value === 'True', line: t.line } satisfies BoolLit
    }
    if (t.kind === 'LPAREN') {
      this.consume()
      const inner = this.parseExpr()
      this.expect('RPAREN')
      return inner
    }
    if (t.kind === 'LBRACKET') {
      this.consume()
      const elements: Expr[] = []
      if (!this.match('RBRACKET')) {
        elements.push(this.parseExpr())
        while (this.match('COMMA')) {
          this.consume()
          // Allow trailing comma: `[1, 2,]`
          if (this.match('RBRACKET')) break
          elements.push(this.parseExpr())
        }
      }
      this.expect('RBRACKET')
      return { kind: 'listLit', elements, line: t.line } satisfies ListLit
    }
    if (t.kind === 'LBRACE') {
      this.consume()
      const entries: DictLit['entries'] = []
      if (!this.match('RBRACE')) {
        const k = this.parseExpr()
        this.expect('COLON')
        const v = this.parseExpr()
        entries.push({ key: k, value: v })
        while (this.match('COMMA')) {
          this.consume()
          if (this.match('RBRACE')) break
          const k2 = this.parseExpr()
          this.expect('COLON')
          const v2 = this.parseExpr()
          entries.push({ key: k2, value: v2 })
        }
      }
      this.expect('RBRACE')
      return { kind: 'dictLit', entries, line: t.line } satisfies DictLit
    }
    throw new ParseError(`unexpected token '${t.value}'`, t.line)
  }
}

export function parse(src: string): Program {
  const tokens = tokenize(src)
  const p = new Parser(tokens)
  return p.parseProgram()
}
