######################
# Tyler Harwood     ##
# COS 301           ##
# Dr. Chawathe      ##
# 23 February 2023  ##
######################

##################################################
# Based on the Calc.py program from the PLY docs.
# ©2001-2020, David Beazley.                    #
#################################################

import sys
sys.path.insert(0, "../..")
if sys.version_info[0] >= 3:
    raw_input = input

# List of valid non-literals
tokens = [
    'NAME',
    'NUMBER',
]

# List of valid literals
literals = ['=','+', '-','*','/','%','(',')', ',']

# Non-literal token definition
# A range of char values I think
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

# Ignore these chars
t_ignore  = ' \t'

# dictionary of names
names = {}

# Integer value assigned to token
def t_NUMBER(t):
    r'\d+'
    t.value = [int(t.value)]    
    return t


# Keeps track of line number by counting newline.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value[0].count("\n")



# For error handling: 
def t_error(t):
    print("Illegal character '%s'" % t.value[0][0])
    t.lexer.skip(1)



# Build the lexer
import ply.lex as lex
lex.lex()  


# Parsing Rules

precedence = [
    ('left', ','),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'UMINUS'),
]



# Assignment statement:
#   Rule for defining a name with an expression
def p_statement_assign(p):
    'statement : NAME "=" expression'
    names[p[1]] = p[3]

# Somewhat Synonymous with the above, just without a key.
def p_expression_expr(p):
    'statement : expression'

    if len(p[1]) > 1:

        if p[1][-1] is None:
            p[1] = p[1][0:-1]
            print(p[1])
        else:
            print(p[1])

    elif len(p[1]) == 1:
        print(p[1][0])
    
    else:
        print(tuple(p[1]))


# Evaluation of expressions.
# Its easy enough to just add mod here.
def p_binop(p):
    '''expression   : expression '+' expression
                    | expression '-' expression
                    | expression '*' expression
                    | expression '/' expression
                    | expression '%' expression'''

    p[0] = []
    if len(p[1]) >= len(p[3]):
        p[0] = list(p[1]).copy()
        domain = len(p[3])
    else:
        p[0] = list(p[3]).copy()
        domain = len(p[1])

    for i in range(domain):

        # Need this for singleton lists because of silly implementation
        # of numbers actually just being singleton lists.
        if p[1][i] == None or p[3][i] == None:
            break

        if p[2] == '+':

            p[0][i] = p[1][i] + p[3][i] 

        elif p[2] == '-':

            p[0][i] = p[1][i] - p[3][i] 

        elif p[2] == '*':

            p[0][i] = p[1][i] * p[3][i] 

        elif p[2] == '/':

            p[0][i] = p[1][i] / p[3][i] 
            
        elif p[2] == '%':

            p[0][i] = p[1][i] % p[3][i] 

    if len(p[0]) > 1: p[0] = tuple(p[0])
            


# Unary minus operator, changes sign of an expr
def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"

    p[0] = list(p[2]).copy()
    for i in range( len(p[2]) ):
        
        if p[0][i] != None:
            p[0][i] =  -p[2][i]

    p[0] = tuple(p[0])

# Defines parenthesization
def p_expression_group(p):
    '''expression   : '(' expression ')' 
                    | '(' ')' '''
    if p[2] == ')':
        p[0] = ()
    else:
        p[0] = p[2]



# Defines bottom of expression as either a number or name
def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]

def p_expression_name(p):
    "expression : NAME"

    # Catches undefined names and assigns the token as 0
    # allows for coninued parsing
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0

# Error detection
def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


#list

#Rebuild lexer?
#lex.lex()

# 1. Integer division implementation
def p_expression_Div(p):
    "expression : expression '/' '/' expression"

    p[0] = []
    if len(p[1]) >= len(p[4]):
        p[0] = list(p[1]).copy()
        domain = len(p[4])
    else:
        p[0] = list(p[4]).copy()
        domain = len(p[1])

    
    for i in range(domain):

        # Need this for singleton lists because of silly implementation
        # of numbers actually just being singleton lists.
        if p[1][i] == None or p[4][i] == None:
            break

        if p[2] == '/' and p[3] == '/':

            p[0][i] = p[1][i] // p[4][i]


        #Assign to tuple on the way out
    p[0] = tuple(p[0])    

# 2. Lists implementation

def p_expression_list(p):
    '''expression   : '(' list ')' 
                    | '(' list expression ')' '''
    p[0] = p[2].copy()
    
    if p[3] != ')':
        if len(p[3]) > 1:
            p[0].append(p[3])
        else:
            p[0].append(p[3][0])
    else:
        p[0].append(None)
    
    p[0] = tuple(p[0])
    

def p_list_append(p):
    '''list     : expression ','
                | list expression ',' '''
    p[0] = list(p[1]).copy()

    # Bugfix so merging sublists to parent does
    # not include trailing None

    if len(p) > 3:

        if len(p[2]) > 1:

            #Append the list object to the list?
            #p[0].append(p[2])

            #Append each element instead
            for i in range(len(p[2])):
                p[0].append(p[2][i])

        else:
            p[0].append(p[2][0])




# And then the parsing can begin
import ply.yacc as yacc
yacc.yacc()

if not sys.stdin.isatty():
    for line in sys.stdin:
        if '\n' == line.rstrip() or 'END' == line.rstrip():
            break

        try:
            s = line
        except EOFError:
            print()
            break
        if not s:
            continue
        yacc.parse(s)

if sys.stdin.isatty():
    while 1:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        if not s:
            continue
        yacc.parse(s)
