from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class ASTNode:
    """Base class for every AST node."""

    def pretty(self, indent: int = 0) -> str:
        raise NotImplementedError


def _ind(n: int) -> str:
    return "  " * n


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

@dataclass
class NumberLiteral(ASTNode):
    value: str

    def pretty(self, indent: int = 0) -> str:
        return f"{_ind(indent)}Number({self.value})"


@dataclass
class StringLiteral(ASTNode):
    value: str

    def pretty(self, indent: int = 0) -> str:
        return f"{_ind(indent)}String({self.value!r})"


@dataclass
class Identifier(ASTNode):
    name: str

    def pretty(self, indent: int = 0) -> str:
        return f"{_ind(indent)}Ident({self.name})"


@dataclass
class BinaryOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

    def pretty(self, indent: int = 0) -> str:
        lines = [f"{_ind(indent)}BinaryOp({self.op})"]
        lines.append(self.left.pretty(indent + 1))
        lines.append(self.right.pretty(indent + 1))
        return "\n".join(lines)


@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

    def pretty(self, indent: int = 0) -> str:
        lines = [f"{_ind(indent)}UnaryOp({self.op})"]
        lines.append(self.operand.pretty(indent + 1))
        return "\n".join(lines)


@dataclass
class FunctionCall(ASTNode):
    name: str
    argument: ASTNode

    def pretty(self, indent: int = 0) -> str:
        lines = [f"{_ind(indent)}Call({self.name})"]
        lines.append(self.argument.pretty(indent + 1))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

@dataclass
class LetStatement(ASTNode):
    name: str
    value: ASTNode

    def pretty(self, indent: int = 0) -> str:
        lines = [f"{_ind(indent)}Let({self.name})"]
        lines.append(self.value.pretty(indent + 1))
        return "\n".join(lines)


@dataclass
class PrintStatement(ASTNode):
    value: ASTNode

    def pretty(self, indent: int = 0) -> str:
        lines = [f"{_ind(indent)}Print"]
        lines.append(self.value.pretty(indent + 1))
        return "\n".join(lines)


@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_body: List[ASTNode]
    else_body: Optional[List[ASTNode]]

    def pretty(self, indent: int = 0) -> str:
        lines = [f"{_ind(indent)}If"]
        lines.append(f"{_ind(indent + 1)}condition:")
        lines.append(self.condition.pretty(indent + 2))
        lines.append(f"{_ind(indent + 1)}then:")
        for stmt in self.then_body:
            lines.append(stmt.pretty(indent + 2))
        if self.else_body is not None:
            lines.append(f"{_ind(indent + 1)}else:")
            for stmt in self.else_body:
                lines.append(stmt.pretty(indent + 2))
        return "\n".join(lines)


@dataclass
class ExprStatement(ASTNode):
    expr: ASTNode

    def pretty(self, indent: int = 0) -> str:
        return self.expr.pretty(indent)


@dataclass
class Program(ASTNode):
    statements: List[ASTNode] = field(default_factory=list)

    def pretty(self, indent: int = 0) -> str:
        lines = [f"{_ind(indent)}Program"]
        for stmt in self.statements:
            lines.append(stmt.pretty(indent + 1))
        return "\n".join(lines)
