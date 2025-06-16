lexer grammar CLexer;

// Keywords
AUTO: 'auto';
BREAK: 'break';
CASE: 'case';
CHAR: 'char';
CONST: 'const';
CONTINUE: 'continue';
DEFAULT: 'default';
DO: 'do';
DOUBLE: 'double';
ELSE: 'else';
ENUM: 'enum';
EXTERN: 'extern';
FLOAT: 'float';
FOR: 'for';
GOTO: 'goto';
IF: 'if';
INLINE: 'inline';
INT: 'int';
LONG: 'long';
REGISTER: 'register';
RESTRICT: 'restrict';
RETURN: 'return';
SHORT: 'short';
SIGNED: 'signed';
SIZEOF: 'sizeof';
STATIC: 'static';
STRUCT: 'struct';
SWITCH: 'switch';
TYPEDEF: 'typedef';
UNION: 'union';
UNSIGNED: 'unsigned';
VOID: 'void';
VOLATILE: 'volatile';
WHILE: 'while';

// Literals
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
INTEGER_CONSTANT: [0-9]+;
FLOATING_CONSTANT: [0-9]*'.'[0-9]+([eE][+-]?[0-9]+)?;
CHARACTER_CONSTANT: '\'' (~['\\\r\n] | '\\' .) '\'';
STRING_LITERAL: '"' (~["\\\r\n] | '\\' .)* '"';

// Operators
PLUS: '+';
MINUS: '-';
STAR: '*';
DIV: '/';
MOD: '%';
ASSIGN: '=';
PLUS_ASSIGN: '+=';
MINUS_ASSIGN: '-=';
STAR_ASSIGN: '*=';
DIV_ASSIGN: '/=';
MOD_ASSIGN: '%=';
AND_ASSIGN: '&=';
OR_ASSIGN: '|=';
XOR_ASSIGN: '^=';
LEFT_SHIFT_ASSIGN: '<<=';
RIGHT_SHIFT_ASSIGN: '>>=';
AND: '&';
OR: '|';
XOR: '^';
NOT: '!';
TILDE: '~';
PLUS_PLUS: '++';
MINUS_MINUS: '--';
LEFT_SHIFT: '<<';
RIGHT_SHIFT: '>>';
LESS_THAN: '<';
GREATER_THAN: '>';
LESS_EQUAL: '<=';
GREATER_EQUAL: '>=';
EQUAL: '==';
NOT_EQUAL: '!=';
AND_AND: '&&';
OR_OR: '||';

// Separators
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
SEMI: ';';
COMMA: ',';
DOT: '.';
ARROW: '->';
QUESTION: '?';
COLON: ':';

// Skip whitespace and comments
WS: [ \t\r\n]+ -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;
LINE_COMMENT: '//' ~[\r\n]* -> skip; 