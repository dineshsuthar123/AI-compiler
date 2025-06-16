parser grammar CParser;

options {
    tokenVocab=CLexer;
}

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

declarationList
    : declaration+
    ;

declaration
    : declarationSpecifiers initDeclaratorList? SEMI
    ;

declarationSpecifiers
    : (storageClassSpecifier
    | typeSpecifier
    | typeQualifier
    | functionSpecifier)+
    ;

initDeclaratorList
    : initDeclarator (COMMA initDeclarator)*
    ;

initDeclarator
    : declarator (ASSIGN initializer)?
    ;

storageClassSpecifier
    : TYPEDEF
    | EXTERN
    | STATIC
    | AUTO
    | REGISTER
    ;

typeSpecifier
    : VOID
    | CHAR
    | SHORT
    | INT
    | LONG
    | FLOAT
    | DOUBLE
    | SIGNED
    | UNSIGNED
    | structOrUnionSpecifier
    | enumSpecifier
    | typedefName
    ;

structOrUnionSpecifier
    : structOrUnion IDENTIFIER? LBRACE structDeclarationList RBRACE
    | structOrUnion IDENTIFIER
    ;

structOrUnion
    : STRUCT
    | UNION
    ;

structDeclarationList
    : structDeclaration+
    ;

structDeclaration
    : specifierQualifierList structDeclaratorList SEMI
    ;

specifierQualifierList
    : (typeSpecifier | typeQualifier)+
    ;

structDeclaratorList
    : structDeclarator (COMMA structDeclarator)*
    ;

structDeclarator
    : declarator
    | declarator? COLON constantExpression
    ;

enumSpecifier
    : ENUM IDENTIFIER? LBRACE enumeratorList RBRACE
    | ENUM IDENTIFIER
    ;

enumeratorList
    : enumerator (COMMA enumerator)*
    ;

enumerator
    : IDENTIFIER (ASSIGN constantExpression)?
    ;

typeQualifier
    : CONST
    | RESTRICT
    | VOLATILE
    ;

functionSpecifier
    : INLINE
    ;

declarator
    : pointer? directDeclarator
    ;

directDeclarator
    : IDENTIFIER
    | LPAREN declarator RPAREN
    | directDeclarator LBRACK typeQualifierList? assignmentExpression? RBRACK
    | directDeclarator LPAREN parameterTypeList RPAREN
    | directDeclarator LPAREN identifierList? RPAREN
    ;

pointer
    : (STAR typeQualifierList?)+
    ;

typeQualifierList
    : typeQualifier+
    ;

parameterTypeList
    : parameterList (COMMA ELLIPSIS)?
    ;

parameterList
    : parameterDeclaration (COMMA parameterDeclaration)*
    ;

parameterDeclaration
    : declarationSpecifiers declarator
    | declarationSpecifiers abstractDeclarator?
    ;

identifierList
    : IDENTIFIER (COMMA IDENTIFIER)*
    ;

typeName
    : specifierQualifierList abstractDeclarator?
    ;

abstractDeclarator
    : pointer
    | pointer? directAbstractDeclarator
    ;

directAbstractDeclarator
    : LPAREN abstractDeclarator RPAREN
    | LBRACK typeQualifierList? assignmentExpression? RBRACK
    | LPAREN parameterTypeList? RPAREN
    ;

typedefName
    : IDENTIFIER
    ;

initializer
    : assignmentExpression
    | LBRACE initializerList COMMA? RBRACE
    ;

initializerList
    : designation? initializer (COMMA designation? initializer)*
    ;

designation
    : designatorList ASSIGN
    ;

designatorList
    : designator+
    ;

designator
    : LBRACK constantExpression RBRACK
    | DOT IDENTIFIER
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
    : IDENTIFIER COLON statement
    | CASE constantExpression COLON statement
    | DEFAULT COLON statement
    ;

compoundStatement
    : LBRACE blockItemList? RBRACE
    ;

blockItemList
    : blockItem+
    ;

blockItem
    : declaration
    | statement
    ;

expressionStatement
    : expression? SEMI
    ;

selectionStatement
    : IF LPAREN expression RPAREN statement (ELSE statement)?
    | SWITCH LPAREN expression RPAREN statement
    ;

iterationStatement
    : WHILE LPAREN expression RPAREN statement
    | DO statement WHILE LPAREN expression RPAREN SEMI
    | FOR LPAREN forCondition RPAREN statement
    ;

forCondition
    : forDeclaration? SEMI expression? SEMI expression?
    | expression? SEMI expression? SEMI expression?
    ;

forDeclaration
    : declarationSpecifiers initDeclaratorList?
    ;

jumpStatement
    : GOTO IDENTIFIER SEMI
    | CONTINUE SEMI
    | BREAK SEMI
    | RETURN expression? SEMI
    ;

expression
    : assignmentExpression (COMMA assignmentExpression)*
    ;

constantExpression
    : conditionalExpression
    ;

assignmentExpression
    : conditionalExpression
    | unaryExpression assignmentOperator assignmentExpression
    ;

assignmentOperator
    : ASSIGN
    | STAR_ASSIGN
    | DIV_ASSIGN
    | MOD_ASSIGN
    | PLUS_ASSIGN
    | MINUS_ASSIGN
    | LEFT_SHIFT_ASSIGN
    | RIGHT_SHIFT_ASSIGN
    | AND_ASSIGN
    | XOR_ASSIGN
    | OR_ASSIGN
    ;

conditionalExpression
    : logicalOrExpression (QUESTION expression COLON conditionalExpression)?
    ;

logicalOrExpression
    : logicalAndExpression (OR_OR logicalAndExpression)*
    ;

logicalAndExpression
    : inclusiveOrExpression (AND_AND inclusiveOrExpression)*
    ;

inclusiveOrExpression
    : exclusiveOrExpression (OR exclusiveOrExpression)*
    ;

exclusiveOrExpression
    : andExpression (XOR andExpression)*
    ;

andExpression
    : equalityExpression (AND equalityExpression)*
    ;

equalityExpression
    : relationalExpression ((EQUAL | NOT_EQUAL) relationalExpression)*
    ;

relationalExpression
    : shiftExpression ((LESS_THAN | GREATER_THAN | LESS_EQUAL | GREATER_EQUAL) shiftExpression)*
    ;

shiftExpression
    : additiveExpression ((LEFT_SHIFT | RIGHT_SHIFT) additiveExpression)*
    ;

additiveExpression
    : multiplicativeExpression ((PLUS | MINUS) multiplicativeExpression)*
    ;

multiplicativeExpression
    : castExpression ((STAR | DIV | MOD) castExpression)*
    ;

castExpression
    : unaryExpression
    | LPAREN typeName RPAREN castExpression
    ;

unaryExpression
    : postfixExpression
    | PLUS_PLUS unaryExpression
    | MINUS_MINUS unaryExpression
    | unaryOperator castExpression
    | SIZEOF unaryExpression
    | SIZEOF LPAREN typeName RPAREN
    ;

unaryOperator
    : AND
    | STAR
    | PLUS
    | MINUS
    | TILDE
    | NOT
    ;

postfixExpression
    : primaryExpression
        (LBRACK expression RBRACK
        | LPAREN argumentExpressionList? RPAREN
        | DOT IDENTIFIER
        | ARROW IDENTIFIER
        | PLUS_PLUS
        | MINUS_MINUS)*
    ;

primaryExpression
    : IDENTIFIER
    | constant
    | STRING_LITERAL
    | LPAREN expression RPAREN
    ;

constant
    : INTEGER_CONSTANT
    | FLOATING_CONSTANT
    | CHARACTER_CONSTANT
    ;

argumentExpressionList
    : assignmentExpression (COMMA assignmentExpression)*
    ; 