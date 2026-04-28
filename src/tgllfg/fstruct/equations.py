# tgllfg/equations.py

"""
LFG annotation language: AST, parser, and unparser.

Equations are the functional annotations attached to c-structure rule
expansions and lexical entries. They are written using the LFG
metavariables ↑ (mother), ↓ (current node or i-th child) and → (the
f-structure reached by an off-path step), and they describe how
f-structures are composed during equation solving.

The grammar implemented here covers the §4.1 deliverable of the
tgllfg evolution plan. The unifier in §4.2 walks the AST produced by
this module; nothing downstream should string-match equation text.

Grammar (EBNF)
--------------

::

    equation        ::= defining
                      | constraining
                      | existential
                      | neg_existential
                      | neg_equation
                      | set_member

    defining        ::= designator "=" value
    constraining    ::= designator "=c" value
    neg_equation    ::= designator "≠" value
    set_member      ::= designator "∈" designator
    neg_existential ::= "¬" designator
    existential     ::= designator                 (* fallthrough *)

    designator      ::= "(" base path? ")"         (* parenthesized *)
                      | base path?                 (* bare *)

    base            ::= "↑" | "↓" | "↓" digit+ | "→"

    path            ::= path_element (path_element)*
    path_element    ::= simple_step off_path?
    simple_step     ::= ident                      (* F     *)
                      | ident "*"                  (* F*    *)
                      | ident "+"                  (* F+    *)
                      | "{" ident ("|" ident)+ "}" (* {F|G} *)

    off_path        ::= "<" equation ("," equation)* ">"

    value           ::= atom | designator
    atom            ::= "'" atom_char* "'"

    ident           ::= [A-Za-z_] [A-Za-z0-9_-]*
    digit           ::= [0-9]

Documented restrictions
-----------------------

* Star and plus may only be applied to a single feature, not to a
  sub-path. ``F*`` and ``F+`` are accepted; ``(F G)*`` is not.
* Alternation ``{F|G}`` is over single features only and may not be
  starred or plussed.
* Atoms are single-quoted; embedded single quotes are not currently
  supported (no use case in the existing grammar).
* ``↓i`` indices are 1-based and must satisfy ``i ≥ 1``. A bare
  ``↓`` (no index) refers to the current node's f-structure.
* Off-path constraints are *represented* in the AST but the §4.1
  unifier does not evaluate them; encountering a non-empty
  ``off_path`` raises ``NotImplementedError``.

Examples
--------

::

    (↑ PRED) = 'EAT <SUBJ, OBJ>'   →  DefiningEquation
    (↑ VOICE) = ↓1 VOICE           →  DefiningEquation, rhs is a Designator path
    (↑ SUBJ) = ↓3                  →  DefiningEquation, rhs path is empty
    (↑) = ↓1                       →  DefiningEquation, lhs path is empty
    (↑ CASE) =c 'NOM'              →  ConstrainingEquation
    (↑ TOPIC)                      →  ExistentialConstraint
    ¬ (↑ NEG)                      →  NegExistentialConstraint
    (↑ FOCUS) ≠ 'WH'               →  NegEquation
    ↓ ∈ (↑ ADJ)                    →  SetMembership
    (↑ TOPIC) = (↑ COMP* GF)       →  DefiningEquation, rhs has StarFeature
"""

from __future__ import annotations

from dataclasses import dataclass


# === AST: bases ============================================================

@dataclass(frozen=True)
class Up:
    """The ↑ metavariable: the mother node's f-structure."""


@dataclass(frozen=True)
class Down:
    """The ↓ or ↓i metavariable.

    ``idx`` is None for bare ``↓`` (the current node's f-structure) and
    a 1-based integer for ``↓i`` (the i-th child's f-structure).
    """
    idx: int | None


@dataclass(frozen=True)
class Right:
    """The → metavariable, used inside off-path constraints to refer to
    the f-structure reached by the current path step."""


type Base = Up | Down | Right


# === AST: path elements ====================================================
#
# Every path element carries an optional tuple of off-path constraints
# attached at that step. The §4.1 unifier rejects non-empty off_path; the
# representation is preserved so downstream phases can evaluate them.

@dataclass(frozen=True)
class Feature:
    """A literal feature step: ``F``."""
    name: str
    off_path: tuple["Equation", ...] = ()


@dataclass(frozen=True)
class StarFeature:
    """Kleene-star feature step: ``F*``."""
    name: str
    off_path: tuple["Equation", ...] = ()


@dataclass(frozen=True)
class PlusFeature:
    """Kleene-plus feature step: ``F+``."""
    name: str
    off_path: tuple["Equation", ...] = ()


@dataclass(frozen=True)
class AltFeature:
    """Disjunctive feature step: ``{F1 | F2 | ...}``."""
    names: tuple[str, ...]
    off_path: tuple["Equation", ...] = ()


type PathElement = Feature | StarFeature | PlusFeature | AltFeature


# === AST: designators and values ===========================================

@dataclass(frozen=True)
class Designator:
    """A designator: a metavariable base followed by a (possibly empty)
    sequence of path elements. The parens around it in the surface
    syntax are not represented here; the parser strips them."""
    base: Base
    path: tuple[PathElement, ...] = ()


@dataclass(frozen=True)
class Atom:
    """A single-quoted atomic value such as ``'NOM'`` or
    ``'EAT <SUBJ, OBJ>'``. The contents are opaque to this module."""
    value: str


type Value = Atom | Designator


# === AST: equations ========================================================

@dataclass(frozen=True)
class DefiningEquation:
    """``lhs = rhs``: lhs and rhs must unify."""
    lhs: Designator
    rhs: Value


@dataclass(frozen=True)
class ConstrainingEquation:
    """``lhs =c rhs``: must already hold in the solved f-structure."""
    lhs: Designator
    rhs: Value


@dataclass(frozen=True)
class ExistentialConstraint:
    """``(designator)`` standing alone: the path must be defined."""
    designator: Designator


@dataclass(frozen=True)
class NegExistentialConstraint:
    """``¬ (designator)``: the path must not be defined."""
    designator: Designator


@dataclass(frozen=True)
class NegEquation:
    """``lhs ≠ rhs``: lhs and rhs must not unify to the same value."""
    lhs: Designator
    rhs: Value


@dataclass(frozen=True)
class SetMembership:
    """``element ∈ container``: typical use ``↓ ∈ (↑ ADJ)``."""
    element: Designator
    container: Designator


type Equation = (
    DefiningEquation
    | ConstrainingEquation
    | ExistentialConstraint
    | NegExistentialConstraint
    | NegEquation
    | SetMembership
)


# === Parse errors ==========================================================

class ParseError(ValueError):
    """Raised on lex or parse failure with offset information."""

    def __init__(self, message: str, source: str, offset: int) -> None:
        self.message = message
        self.source = source
        self.offset = offset
        # Render a small caret pointing at the offending position.
        line = source.replace("\n", " ")
        caret = " " * offset + "^"
        super().__init__(f"{message} at offset {offset}\n  {line}\n  {caret}")


# === Tokenizer =============================================================

@dataclass(frozen=True)
class _Token:
    kind: str
    text: str
    offset: int


_SINGLE_CHAR_TOKENS: dict[str, str] = {
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "<": "LANGLE",
    ">": "RANGLE",
    "↑": "UP",
    "↓": "DOWN",
    "→": "RIGHT",
    "¬": "NEG",
    "∈": "IN",
    "≠": "NEQ",
    "*": "STAR",
    "+": "PLUS",
    "|": "PIPE",
    ",": "COMMA",
}


def _is_ident_start(c: str) -> bool:
    return c.isalpha() or c == "_"


def _is_ident_cont(c: str) -> bool:
    return c.isalnum() or c in "_-"


def _tokenize(s: str) -> list[_Token]:
    tokens: list[_Token] = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c in _SINGLE_CHAR_TOKENS:
            tokens.append(_Token(_SINGLE_CHAR_TOKENS[c], c, i))
            i += 1
            continue
        if c == "=":
            if i + 1 < n and s[i + 1] == "c":
                tokens.append(_Token("EQC", "=c", i))
                i += 2
            else:
                tokens.append(_Token("EQ", "=", i))
                i += 1
            continue
        if c == "'":
            end = s.find("'", i + 1)
            if end < 0:
                raise ParseError("unterminated atom literal", s, i)
            tokens.append(_Token("ATOM", s[i + 1:end], i))
            i = end + 1
            continue
        if c.isdigit():
            start = i
            while i < n and s[i].isdigit():
                i += 1
            tokens.append(_Token("INT", s[start:i], start))
            continue
        if _is_ident_start(c):
            start = i
            i += 1
            while i < n and _is_ident_cont(s[i]):
                i += 1
            tokens.append(_Token("IDENT", s[start:i], start))
            continue
        raise ParseError(f"unexpected character {c!r}", s, i)
    tokens.append(_Token("EOF", "", n))
    return tokens


# === Parser ================================================================

class _Parser:
    def __init__(self, tokens: list[_Token], source: str) -> None:
        self._tokens = tokens
        self._source = source
        self._pos = 0

    def _peek(self, offset: int = 0) -> _Token:
        return self._tokens[self._pos + offset]

    def _consume(self, kind: str | None = None) -> _Token:
        tok = self._tokens[self._pos]
        if kind is not None and tok.kind != kind:
            raise self._error(f"expected {kind}, got {tok.kind} ({tok.text!r})", tok)
        self._pos += 1
        return tok

    def _error(self, msg: str, tok: _Token) -> ParseError:
        return ParseError(msg, self._source, tok.offset)

    # Top-level entry.
    def parse(self) -> Equation:
        eq = self._parse_equation()
        tail = self._peek()
        if tail.kind != "EOF":
            raise self._error(f"trailing tokens after equation: {tail.text!r}", tail)
        return eq

    def _parse_equation(self) -> Equation:
        t = self._peek()
        if t.kind == "NEG":
            self._consume("NEG")
            d = self._parse_designator()
            return NegExistentialConstraint(d)

        lhs = self._parse_designator()
        nxt = self._peek()
        if nxt.kind == "EQ":
            self._consume("EQ")
            return DefiningEquation(lhs, self._parse_value())
        if nxt.kind == "EQC":
            self._consume("EQC")
            return ConstrainingEquation(lhs, self._parse_value())
        if nxt.kind == "NEQ":
            self._consume("NEQ")
            return NegEquation(lhs, self._parse_value())
        if nxt.kind == "IN":
            self._consume("IN")
            return SetMembership(lhs, self._parse_designator())
        # Fallthrough: a bare designator is an existential constraint.
        return ExistentialConstraint(lhs)

    def _parse_designator(self) -> Designator:
        t = self._peek()
        if t.kind == "LPAREN":
            self._consume("LPAREN")
            base = self._parse_base()
            path = self._parse_path()
            self._consume("RPAREN")
            return Designator(base, tuple(path))
        # Bare designator: ↑, ↓, ↓i, →, optionally followed by path elements
        # up to the next non-path token.
        base = self._parse_base()
        path = self._parse_path()
        return Designator(base, tuple(path))

    def _parse_base(self) -> Base:
        t = self._peek()
        if t.kind == "UP":
            self._consume("UP")
            return Up()
        if t.kind == "RIGHT":
            self._consume("RIGHT")
            return Right()
        if t.kind == "DOWN":
            self._consume("DOWN")
            nxt = self._peek()
            if nxt.kind == "INT":
                self._consume("INT")
                idx = int(nxt.text)
                if idx < 1:
                    raise self._error(f"↓ index must be ≥ 1, got {idx}", nxt)
                return Down(idx=idx)
            return Down(idx=None)
        raise self._error(f"expected ↑, ↓, or →; got {t.kind} ({t.text!r})", t)

    def _parse_path(self) -> list[PathElement]:
        elements: list[PathElement] = []
        while self._peek().kind in ("IDENT", "LBRACE"):
            elements.append(self._parse_path_element())
        return elements

    def _parse_path_element(self) -> PathElement:
        t = self._peek()
        elem: PathElement
        if t.kind == "LBRACE":
            self._consume("LBRACE")
            names = [self._consume("IDENT").text]
            if self._peek().kind != "PIPE":
                raise self._error(
                    "alternation requires at least two alternatives",
                    self._peek(),
                )
            while self._peek().kind == "PIPE":
                self._consume("PIPE")
                names.append(self._consume("IDENT").text)
            self._consume("RBRACE")
            elem = AltFeature(names=tuple(names))
        else:
            name = self._consume("IDENT").text
            nxt = self._peek()
            if nxt.kind == "STAR":
                self._consume("STAR")
                elem = StarFeature(name=name)
            elif nxt.kind == "PLUS":
                self._consume("PLUS")
                elem = PlusFeature(name=name)
            else:
                elem = Feature(name=name)

        if self._peek().kind == "LANGLE":
            self._consume("LANGLE")
            constraints: list[Equation] = [self._parse_equation()]
            while self._peek().kind == "COMMA":
                self._consume("COMMA")
                constraints.append(self._parse_equation())
            self._consume("RANGLE")
            elem = _attach_off_path(elem, tuple(constraints))
        return elem

    def _parse_value(self) -> Value:
        t = self._peek()
        if t.kind == "ATOM":
            self._consume("ATOM")
            return Atom(value=t.text)
        return self._parse_designator()


def _attach_off_path(
    elem: PathElement, constraints: tuple[Equation, ...]
) -> PathElement:
    if isinstance(elem, Feature):
        return Feature(name=elem.name, off_path=constraints)
    if isinstance(elem, StarFeature):
        return StarFeature(name=elem.name, off_path=constraints)
    if isinstance(elem, PlusFeature):
        return PlusFeature(name=elem.name, off_path=constraints)
    if isinstance(elem, AltFeature):
        return AltFeature(names=elem.names, off_path=constraints)
    raise TypeError(f"unknown path element type: {type(elem).__name__}")


def parse_equation(s: str) -> Equation:
    """Parse an LFG annotation string into a typed equation AST.

    Raises ``ParseError`` on lexical or syntactic failure.
    """
    tokens = _tokenize(s)
    return _Parser(tokens, s).parse()


# === Unparser ==============================================================
#
# Canonical form: every designator is parenthesized, every path step is
# separated by a single space, every binary operator has a single space
# on each side. Round-tripping (parse → unparse → parse) yields an AST
# equal to the original.

def _unparse_base(b: Base) -> str:
    if isinstance(b, Up):
        return "↑"
    if isinstance(b, Right):
        return "→"
    return "↓" if b.idx is None else f"↓{b.idx}"


def _unparse_path_element(e: PathElement) -> str:
    if isinstance(e, Feature):
        core = e.name
    elif isinstance(e, StarFeature):
        core = f"{e.name}*"
    elif isinstance(e, PlusFeature):
        core = f"{e.name}+"
    else:
        core = "{" + " | ".join(e.names) + "}"
    if e.off_path:
        body = ", ".join(unparse(c) for c in e.off_path)
        return f"{core}<{body}>"
    return core


def _unparse_designator(d: Designator) -> str:
    base = _unparse_base(d.base)
    if not d.path:
        return f"({base})"
    return "(" + base + " " + " ".join(_unparse_path_element(e) for e in d.path) + ")"


def _unparse_value(v: Value) -> str:
    if isinstance(v, Atom):
        return f"'{v.value}'"
    return _unparse_designator(v)


def unparse(eq: Equation) -> str:
    """Render an equation AST back to canonical surface syntax."""
    if isinstance(eq, DefiningEquation):
        return f"{_unparse_designator(eq.lhs)} = {_unparse_value(eq.rhs)}"
    if isinstance(eq, ConstrainingEquation):
        return f"{_unparse_designator(eq.lhs)} =c {_unparse_value(eq.rhs)}"
    if isinstance(eq, NegEquation):
        return f"{_unparse_designator(eq.lhs)} ≠ {_unparse_value(eq.rhs)}"
    if isinstance(eq, SetMembership):
        return (
            f"{_unparse_designator(eq.element)} ∈ "
            f"{_unparse_designator(eq.container)}"
        )
    if isinstance(eq, NegExistentialConstraint):
        return f"¬ {_unparse_designator(eq.designator)}"
    if isinstance(eq, ExistentialConstraint):
        return _unparse_designator(eq.designator)
    raise TypeError(f"unknown equation type: {type(eq).__name__}")


__all__ = [
    # Bases
    "Up", "Down", "Right", "Base",
    # Path elements
    "Feature", "StarFeature", "PlusFeature", "AltFeature", "PathElement",
    # Designators and values
    "Designator", "Atom", "Value",
    # Equations
    "DefiningEquation", "ConstrainingEquation", "ExistentialConstraint",
    "NegExistentialConstraint", "NegEquation", "SetMembership", "Equation",
    # Errors
    "ParseError",
    # Functions
    "parse_equation", "unparse",
]
