export enum TokenType {
    NUMBER,
    VARIABLE,
    CONSTANT,
    PLUS,
    MINUS,
    MULTIPLY,
    DIVIDE,
    POWER,
    LPAREN,
    RPAREN,
    COMMA,
    LOG,
    LN,
    SIN,
    COS,
    TAN,
    CSC,
    SEC,
    COT,
    ARCSIN,
    ARCCOS,
    ARCTAN,
    ARCCSC,
    ARCSEC,
    ARCCOT,
    EOF
}

export interface Token {
    type: TokenType;
    value?: string;
    position: number;
}
