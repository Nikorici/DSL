from __future__ import annotations
from typing import List, Optional

from lexer import Lexer, Token, TokenType
from ast_nodes import (
    ASTNode, Program,
    LetStatement, PrintStatement, IfStatement, ExprStatement,
    BinaryOp, UnaryOp, FunctionCall,
    NumberLiteral, StringLiteral, Identifier,
)


class ParseError(Exception):
    def __init__(self, message: str, token: Token) -> None:
        super().__init__(f"{message} (got {token.type.name} {token.value!r} at line {token.line})")
        self.token = token


FUNC_KEYWORDS = {"sin", "cos", "tan"}
COMPARE_OPS   = {"==", "!=", "<", "<=", ">", ">="}
ADD_OPS       = {"+", "-"}
MUL_OPS       = {"*", "/"}


class Parser:
    """
    Recursive-descent parser for the LAB3 expression language.

    Grammar (simplified):
        program      := statement* EOF
        statement    := let_stmt | print_stmt | if_stmt | expr_stmt
        let_stmt     := 'let' IDENT '=' expr ';'
        print_stmt   := 'print' '(' expr ')' ';'
        if_stmt      := 'if' expr '{' statement* '}' ('else' '{' statement* '}')?
        expr_stmt    := expr ';'

        expr         := comparison
        comparison   := addition (CMP_OP addition)*
        addition     := mult (('+' | '-') mult)*
        mult         := unary (('*' | '/') unary)*
        unary        := '-' unary | power
        power        := primary ('^' unary)?
        primary      := NUMBER | STRING | func_call | IDENT | '(' expr ')'
        func_call    := ('sin'|'cos'|'tan') '(' expr ')'
    """

    def __init__(self, source: str) -> None:
        lexer = Lexer(source)
        self._tokens: List[Token] = lexer.tokenize()
        self._pos = 0

    # ------------------------------------------------------------------
    # Token navigation helpers
    # ------------------------------------------------------------------

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _check_type(self, tt: TokenType) -> bool:
        return self._peek().type is tt

    def _check_value(self, *values: str) -> bool:
        return self._peek().value in values

    def _expect_type(self, tt: TokenType) -> Token:
        if not self._check_type(tt):
            raise ParseError(f"Expected {tt.name}", self._peek())
        return self._advance()

    def _expect_value(self, *values: str) -> Token:
        if not self._check_value(*values):
            raise ParseError(f"Expected {values}", self._peek())
        return self._advance()

    def _match_value(self, *values: str) -> Optional[Token]:
        if self._check_value(*values):
            return self._advance()
        return None

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def parse(self) -> Program:
        stmts: List[ASTNode] = []
        while not self._check_type(TokenType.EOF):
            stmts.append(self._statement())
        return Program(stmts)

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def _statement(self) -> ASTNode:
        tok = self._peek()
        if tok.type is TokenType.KEYWORD:
            if tok.value == "let":
                return self._let_stmt()
            if tok.value == "print":
                return self._print_stmt()
            if tok.value == "if":
                return self._if_stmt()
        return self._expr_stmt()

    def _let_stmt(self) -> LetStatement:
        self._expect_value("let")
        name_tok = self._expect_type(TokenType.IDENT)
        self._expect_value("=")
        value = self._expr()
        self._expect_value(";")
        return LetStatement(name_tok.value, value)

    def _print_stmt(self) -> PrintStatement:
        self._expect_value("print")
        self._expect_value("(")
        value = self._expr()
        self._expect_value(")")
        self._expect_value(";")
        return PrintStatement(value)

    def _if_stmt(self) -> IfStatement:
        self._expect_value("if")
        condition = self._expr()
        self._expect_value("{")
        then_body = self._block()
        self._expect_value("}")

        else_body: Optional[List[ASTNode]] = None
        if self._check_value("else"):
            self._advance()
            self._expect_value("{")
            else_body = self._block()
            self._expect_value("}")

        return IfStatement(condition, then_body, else_body)

    def _block(self) -> List[ASTNode]:
        stmts: List[ASTNode] = []
        while not self._check_value("}") and not self._check_type(TokenType.EOF):
            stmts.append(self._statement())
        return stmts

    def _expr_stmt(self) -> ExprStatement:
        expr = self._expr()
        self._expect_value(";")
        return ExprStatement(expr)

    # ------------------------------------------------------------------
    # Expressions (precedence climbing via recursive descent)
    # ------------------------------------------------------------------

    def _expr(self) -> ASTNode:
        return self._comparison()

    def _comparison(self) -> ASTNode:
        left = self._addition()
        while self._check_type(TokenType.OP) and self._peek().value in COMPARE_OPS:
            op = self._advance().value
            right = self._addition()
            left = BinaryOp(op, left, right)
        return left

    def _addition(self) -> ASTNode:
        left = self._mult()
        while self._check_type(TokenType.OP) and self._peek().value in ADD_OPS:
            op = self._advance().value
            right = self._mult()
            left = BinaryOp(op, left, right)
        return left

    def _mult(self) -> ASTNode:
        left = self._unary()
        while self._check_type(TokenType.OP) and self._peek().value in MUL_OPS:
            op = self._advance().value
            right = self._unary()
            left = BinaryOp(op, left, right)
        return left

    def _unary(self) -> ASTNode:
        if self._check_type(TokenType.OP) and self._peek().value == "-":
            op = self._advance().value
            return UnaryOp(op, self._unary())
        return self._power()

    def _power(self) -> ASTNode:
        base = self._primary()
        if self._check_type(TokenType.OP) and self._peek().value == "^":
            op = self._advance().value
            exp = self._unary()
            return BinaryOp(op, base, exp)
        return base

    def _primary(self) -> ASTNode:
        tok = self._peek()

        if tok.type is TokenType.NUMBER:
            self._advance()
            return NumberLiteral(tok.value)

        if tok.type is TokenType.STRING:
            self._advance()
            return StringLiteral(tok.value)

        if tok.type is TokenType.KEYWORD and tok.value in FUNC_KEYWORDS:
            return self._func_call()

        if tok.type is TokenType.IDENT:
            self._advance()
            return Identifier(tok.value)

        if tok.type is TokenType.PUNCT and tok.value == "(":
            self._advance()
            expr = self._expr()
            self._expect_value(")")
            return expr

        raise ParseError("Unexpected token in expression", tok)

    def _func_call(self) -> FunctionCall:
        name_tok = self._advance()
        self._expect_value("(")
        arg = self._expr()
        self._expect_value(")")
        return FunctionCall(name_tok.value, arg)
