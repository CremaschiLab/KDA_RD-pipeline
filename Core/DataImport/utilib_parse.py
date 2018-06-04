#
# Flatten List function for parsing AMPL structures
#

def flatten_list(x):
    """Flatten nested lists"""
    if type(x) is not list:
        return x
    x_len = len(x)
    i = 0
    while i < x_len:
        if type(x[i]) is list:
            x_len += len(x[i]) - 1
            x[i:i+1] = x[i]
        else:
            i += 1
    return x

__all__ = ['ply_init', 't_newline', 't_ignore', 't_COMMENT', '_find_column', 'p_error']

#
# Utility functions that are used with PLY
#

def ply_init(data):
    global _parsedata
    _parsedata=data

def t_newline(t):
    r'[\n]+'
    t.lexer.lineno += len(t.value)

# Ignore space and tab
t_ignore  = " \t\r"

# Discard comments
def t_COMMENT(t):
    r'\#[^\n]*'
    pass
# Tokens in comments are discarded.

#
# Compute column.
#     input is the input text string
#     token is a token instance
#
def _find_column(input,token):
    i = token.lexpos
    while i > 0:
        if input[i] == '\n': break
        i -= 1
    column = (token.lexpos - i)+1
    return column

def p_error(p):
    if p is None:
        tmp = "Syntax error at end of file."
    else:
        tmp = "Syntax error at token "
        if p.type is "":
            tmp = tmp + "''"
        else:
            tmp = tmp + str(p.type)
        tmp = tmp + " with value '"+str(p.value)+"'"
        tmp = tmp + " in line " + str(p.lineno)
        tmp = tmp + " at column "+str(_find_column(_parsedata,p))
    raise IOError(tmp)
