grammar C;

// Parser rules
compilationUnit
    : translationUnit? EOF
    ;

translationUnit
    : externalDeclaration+
    ;

externalDeclaration
    : functionDefinition
    | declaration
    ;

functionDefinition
    : declarationSpecifiers? declarator declarationList? compoundStatement
    ;

declaration
    : declarationSpecifiers initDeclaratorList? ';'
    ;

declarationList
    : declaration+
    ;

declarationSpecifiers
    : (storageClassSpecifier | typeSpecifier | typeQualifier)+
    ;

storageClassSpecifier
    : 'typedef'
    | 'extern'
    | 'static'
    | 'auto'
    | 'register'
    ;

typeQualifier
    : 'const'
    | 'volatile'
    ;

initDeclaratorList
    : initDeclarator (',' initDeclarator)*
    ;

initDeclarator
    : declarator ('=' initializer)?
    ;

initializer
    : assignmentExpression
    | '{' initializerList '}'
    | '{' initializerList ',' '}'
    ;

initializerList
    : initializer (',' initializer)*
    ;

declarator
    : pointer? directDeclarator
    ;

directDeclarator
    : Identifier
    | '(' declarator ')'
    | directDeclarator '[' constantExpression? ']'
    | directDeclarator '(' parameterTypeList ')'
    | directDeclarator '(' identifierList? ')'
    ;

abstractDeclarator
    : pointer
    | pointer? directAbstractDeclarator
    ;

directAbstractDeclarator
    : '(' abstractDeclarator ')'
    | '[' constantExpression? ']'
    | '(' parameterTypeList? ')'
    ;

pointer
    : '*' typeQualifier* pointer?
    ;

parameterTypeList
    : parameterList (',' '...')?
    ;

parameterList
    : parameterDeclaration (',' parameterDeclaration)*
    ;

parameterDeclaration
    : declarationSpecifiers declarator
    | declarationSpecifiers abstractDeclarator?
    ;

identifierList
    : Identifier (',' Identifier)*
    ;

typeSpecifier
    : 'void'
    | 'char'
    | 'short'
    | 'int'
    | 'long'
    | 'float'
    | 'double'
    | 'signed'
    | 'unsigned'
    | structOrUnionSpecifier
    | enumSpecifier
    | typedefName
    ;

structOrUnionSpecifier
    : structOrUnion Identifier? '{' structDeclarationList '}'
    | structOrUnion Identifier
    ;

structOrUnion
    : 'struct'
    | 'union'
    ;

structDeclarationList
    : structDeclaration+
    ;

structDeclaration
    : specifierQualifierList structDeclaratorList ';'
    ;

specifierQualifierList
    : (typeSpecifier | typeQualifier)+
    ;

structDeclaratorList
    : structDeclarator (',' structDeclarator)*
    ;

structDeclarator
    : declarator
    | declarator? ':' constantExpression
    ;

enumSpecifier
    : 'enum' Identifier? '{' enumeratorList '}'
    | 'enum' Identifier
    ;

enumeratorList
    : enumerator (',' enumerator)*
    ;

enumerator
    : Identifier ('=' constantExpression)?
    ;

typedefName
    : Identifier
    ;

statement
    : labeledStatement
    | compoundStatement
    | expressionStatement
    | selectionStatement
    | iterationStatement
    | jumpStatement
    ;

labeledStatement
    : Identifier ':' statement
    | 'case' constantExpression ':' statement
    | 'default' ':' statement
    ;

compoundStatement
    : '{' blockItemList? '}'
    ;

blockItemList
    : blockItem+
    ;

blockItem
    : declaration
    | statement
    ;

expressionStatement
    : expression? ';'
    ;

selectionStatement
    : 'if' '(' expression ')' statement ('else' statement)?
    | 'switch' '(' expression ')' statement
    ;

iterationStatement
    : 'while' '(' expression ')' statement
    | 'do' statement 'while' '(' expression ')' ';'
    | 'for' '(' expression? ';' expression? ';' expression? ')' statement
    ;

jumpStatement
    : 'continue' ';'
    | 'break' ';'
    | 'return' expression? ';'
    ;

expression
    : assignmentExpression (',' assignmentExpression)*
    ;

assignmentExpression
    : conditionalExpression
    | unaryExpression assignmentOperator assignmentExpression
    ;

assignmentOperator
    : '=' | '*=' | '/=' | '%=' | '+=' | '-=' | '<<=' | '>>=' | '&=' | '^=' | '|='
    ;

conditionalExpression
    : logicalOrExpression ('?' expression ':' conditionalExpression)?
    ;

constantExpression
    : conditionalExpression
    ;

logicalOrExpression
    : logicalAndExpression ('||' logicalAndExpression)*
    ;

logicalAndExpression
    : inclusiveOrExpression ('&&' inclusiveOrExpression)*
    ;

inclusiveOrExpression
    : exclusiveOrExpression ('|' exclusiveOrExpression)*
    ;

exclusiveOrExpression
    : andExpression ('^' andExpression)*
    ;

andExpression
    : equalityExpression ('&' equalityExpression)*
    ;

equalityExpression
    : relationalExpression (('=='|'!=') relationalExpression)*
    ;

relationalExpression
    : shiftExpression (('<'|'>'|'<='|'>=') shiftExpression)*
    ;

shiftExpression
    : additiveExpression (('<<'|'>>') additiveExpression)*
    ;

additiveExpression
    : multiplicativeExpression (('+'|'-') multiplicativeExpression)*
    ;

multiplicativeExpression
    : unaryExpression (('*'|'/'|'%') unaryExpression)*
    ;

unaryExpression
    : postfixExpression
    | '++' unaryExpression
    | '--' unaryExpression
    | unaryOperator unaryExpression
    | 'sizeof' unaryExpression
    | 'sizeof' '(' typeName ')'
    ;

unaryOperator
    : '&' | '*' | '+' | '-' | '~' | '!'
    ;

postfixExpression
    : primaryExpression
    | postfixExpression '[' expression ']'
    | postfixExpression '(' argumentExpressionList? ')'
    | postfixExpression '.' Identifier
    | postfixExpression '->' Identifier
    | postfixExpression '++'
    | postfixExpression '--'
    ;

primaryExpression
    : Identifier
    | Constant
    | StringLiteral
    | '(' expression ')'
    ;

argumentExpressionList
    : assignmentExpression (',' assignmentExpression)*
    ;

typeName
    : specifierQualifierList abstractDeclarator?
    ;

// Lexer rules
Identifier
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

Constant
    : IntegerConstant
    | FloatingConstant
    | CharacterConstant
    ;

StringLiteral
    : '"' SCharSequence? '"'
    ;

IntegerConstant
    : DecimalConstant IntegerSuffix?
    | OctalConstant IntegerSuffix?
    | HexadecimalConstant IntegerSuffix?
    ;

FloatingConstant
    : DecimalFloatingConstant
    | HexadecimalFloatingConstant
    ;

CharacterConstant
    : '\'' CCharSequence '\''
    ;

fragment
DecimalFloatingConstant
    : FractionalConstant ExponentPart? FloatingSuffix?
    | DigitSequence ExponentPart FloatingSuffix?
    ;

fragment
HexadecimalFloatingConstant
    : HexadecimalPrefix HexadecimalFractionalConstant BinaryExponentPart FloatingSuffix?
    | HexadecimalPrefix HexadecimalDigitSequence BinaryExponentPart FloatingSuffix?
    ;

fragment
FractionalConstant
    : DigitSequence? '.' DigitSequence
    | DigitSequence '.'
    ;

fragment
ExponentPart
    : [eE] [+-]? DigitSequence
    ;

fragment
BinaryExponentPart
    : [pP] [+-]? DigitSequence
    ;

fragment
HexadecimalFractionalConstant
    : HexadecimalDigitSequence? '.' HexadecimalDigitSequence
    | HexadecimalDigitSequence '.'
    ;

fragment
FloatingSuffix
    : [flFL]
    ;

fragment
DigitSequence
    : Digit+
    ;

fragment
HexadecimalDigitSequence
    : HexadecimalDigit+
    ;

fragment
DecimalConstant
    : NonzeroDigit Digit*
    ;

fragment
OctalConstant
    : '0' OctalDigit*
    ;

fragment
HexadecimalConstant
    : HexadecimalPrefix HexadecimalDigit+
    ;

fragment
HexadecimalPrefix
    : '0' [xX]
    ;

fragment
NonzeroDigit
    : [1-9]
    ;

fragment
Digit
    : [0-9]
    ;

fragment
OctalDigit
    : [0-7]
    ;

fragment
HexadecimalDigit
    : [0-9a-fA-F]
    ;

fragment
IntegerSuffix
    : [uU] [lL]?
    | [lL] [uU]?
    ;

fragment
CCharSequence
    : CChar+
    ;

fragment
CChar
    : ~['\\\r\n]
    | EscapeSequence
    ;

fragment
SCharSequence
    : SChar+
    ;

fragment
SChar
    : ~["\\\r\n]
    | EscapeSequence
    ;

fragment
EscapeSequence
    : SimpleEscapeSequence
    | OctalEscapeSequence
    | HexadecimalEscapeSequence
    ;

fragment
SimpleEscapeSequence
    : '\\' ['"?abfnrtv\\]
    ;

fragment
OctalEscapeSequence
    : '\\' OctalDigit OctalDigit? OctalDigit?
    ;

fragment
HexadecimalEscapeSequence
    : '\\x' HexadecimalDigit+
    ;

Whitespace
    : [ \t\r\n]+ -> skip
    ;

BlockComment
    : '/*' .*? '*/' -> skip
    ;

LineComment
    : '//' ~[\r\n]* -> skip
    ; 