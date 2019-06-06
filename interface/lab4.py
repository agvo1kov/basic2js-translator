import sys
import json
import subprocess

def get_token_name(token):
    global service_words, operations, separators, constants, identifiers
    codes = ['W', 'O', 'R', 'C', 'I']
    tables = [service_words, operations, separators, constants, identifiers]
    if token[0] in ['C', 'I']:
        return tables[codes.index(token[0])][token[1]]['value']
    return tables[codes.index(token[0])][token[1]]

def scan():
    global token_index, nxtsymb, cursymb
    token_index += 1
    if token_index < len(tokens_chain):
        cursymb = tokens_chain[token_index-1]
        nxtsymb = tokens_chain[token_index]

def antiscan():
    global token_index, nxtsymb, cursymb
    token_index -= 1
    if token_index >= 1:
        cursymb = tokens_chain[token_index-1]
        nxtsymb = tokens_chain[token_index]

def error(text):
    global mistakes
    if text[-8:] == 'expected':
        if text == '";" expected' and (cursymb[2] != nxtsymb[2]):
            mistakes.append(str(text) + ' in the end of line ' + str(cursymb[2]))
            return
        text += ' instead of "' + get_token_name(nxtsymb) + '"'
    mistakes.append(str(text) + ' at line ' + str(nxtsymb[2]))

def check(response):
    if response:
        error(response)
        return False
    else:
        return True

def wrapper():
    scan()
    mistake = False
    while not mistake:
        print('PERED', get_token_name(nxtsymb), nxtsymb)
        mistake = operator()
        if mistake:
            return mistake
        if cursymb[0] == 'I' and get_token_name(nxtsymb) == ':':
            scan()
        else:
            print('POSLE:', get_token_name(nxtsymb), nxtsymb)
            scan()
            print('POSLE2:', get_token_name(nxtsymb), nxtsymb)
            if get_token_name(nxtsymb) == ';':
                scan()
                if get_token_name(nxtsymb) == 'stop':
                    break

def program():
#     print(Fore.GREEN + 'program' + Style.RESET_ALL)
    scan()
    if nxtsymb[0] != 'I':
        return 'identifier expected'
    scan()
    if get_token_name(nxtsymb) != ';':
        return '";" expected'
    return ''

def var():
#     print(Fore.GREEN + 'var' + Style.RESET_ALL)
    if nxtsymb[0] != 'I':
        return 'identifier expexted'
    scan()
    while get_token_name(nxtsymb) == ',':
        scan()
        if nxtsymb[0] != 'I':
            return 'identifier expected'
        scan()
    if get_token_name(nxtsymb) != ':':
        return '":" expected'
    scan()
    if not check(var_type()):
        return 'invalid variable type declaration'
    return ''

def var_type():
#     print(Fore.GREEN + 'var_type' + Style.RESET_ALL)
    if get_token_name(nxtsymb) in ['integer', 'real', 'string']:
        return ''
    elif get_token_name(nxtsymb) == 'array':
        scan()
        if nxtsymb[2] != '[':
            return '"[" expected'
        scan()
        if not check(interval()):
            return 'invalid interval syntax'
        scan()
        while nxtsymb[2] == ',':
            scan()
            if not check(interval()):
                return 'invalid interval syntax'
            scan()
        if nxtsymb[2] != ']':
            return '"]" expected'
        scan()
        if nxtsymb[2] != 'of':
            return '"of" expected'
        scan()
        if nxtsymb[2] not in ['integer', 'real', 'string']:
            return 'variable type expected'
        return ''
    else:
        return 'array type expected'
        
def interval():
#     print(Fore.GREEN + 'interval' + Style.RESET_ALL)
    if nxtsymb[0] != 'C':
        return 'constant expected'
    scan()
    if nxtsymb[2] != '..':
        return '".." expected'
    scan()
    if nxtsymb[0] != 'C':
        return 'constant expected'
    return ''

def function_or_procedure():
#     print(Fore.GREEN + 'function_or_procedure' + Style.RESET_ALL)
    if nxtsymb[2] == 'procedure':
        scan()
        if not check(procedure()):
            return 'invalid procedure declaration'
        return ''
    if nxtsymb[2] == 'function':
        scan()
        if not check(function()):
            return 'invalid function declaration'
        return ''
    return ''        

def procedure():
#     print(Fore.GREEN + 'procedure' + Style.RESET_ALL)
    if nxtsymb[0] != 'I':
        return 'identifier expended'
    scan()
    if nxtsymb[2] == '(':
        scan()
        if not check(var()):
            return 'invalid var declaration'
        scan()
        while nxtsymb[2] == ';':
            scan()
            if not check(var()):
                return 'invalid var declaration'
            scan()
        if nxtsymb[2] != ')':
            return '")" expected'
        scan()
    if nxtsymb[2] != ';':
        return '";" expected'
    
    scan()
    if nxtsymb[2] == 'var':
        scan()
        if not check(var()):
            return 'invalid var declaration'
        scan()
        if nxtsymb[2] != ';':
            return '";" expected'
        scan()
        while nxtsymb[0] == 'I':
            if not check(var()):
                return 'invalid var declaration'
            scan()
            if nxtsymb[2] != ';':
                return '";" expected'
            scan()
    
    while nxtsymb[2] in ['function', 'procedure']:
        if not check(function_or_procedure()):
            return 'invalid function or procedure declaration'
    
    if nxtsymb[2] != 'begin':
        return '"begin" expected'
    scan()
    mistake = ''
    while not mistake:
        if nxtsymb[2] == 'end':
            break
        mistake = operator()
        if mistake:
            return mistake
        if cursymb[0] == 'I' and nxtsymb[2] == ':':
            scan()
        else:
            scan()
            if nxtsymb[2] == ';':
                scan()
            else:
                return '";" expected'
            
    if nxtsymb[2] != 'end':
        if cursymb[2] == ';' and nxtsymb[2] == 'else':
            return 'extra ";" before else'
        return 'unexpected "'+nxtsymb[2]+'"'
    scan()
    if nxtsymb[2] != ';':
        return '";" expected'
    scan()
    return ''

def function():
#     print(Fore.GREEN + 'function' + Style.RESET_ALL)
    if nxtsymb[0] != 'I':
        return 'identifier expended'
    scan()
    if nxtsymb[2] == '(':
        scan()
        if not check(var()):
            return 'invalid var declaration'
        scan()
        while nxtsymb[2] == ';':
            scan()
            if not check(var()):
                return 'invalid var declaration'
            scan()
        if nxtsymb[2] != ')':
            return '")" expected'
        scan()
    if nxtsymb[2] != ':':
        return 'expected ":"'
    scan()
    if nxtsymb[2] not in ['integer', 'real', 'string']:
        return 'type of function expected'
    scan()
    if nxtsymb[2] != ';':
        return '";" expected'
    
    scan()
    if nxtsymb[2] == 'var':
        scan()
        if not check(var()):
            return 'invalid var declaration'
        scan()
        if nxtsymb[2] != ';':
            return '";" expected'
        scan()
        while nxtsymb[0] == 'I':
            if not check(var()):
                return 'invalid var declaration'
            scan()
            if nxtsymb[2] != ';':
                return '";" expected'
            scan()
    
    while nxtsymb[2] in ['function', 'procedure']:
        if not check(function_or_procedure()):
            return 'invalid function or procedure declaration'
    
#     scan()
    if nxtsymb[2] != 'begin':
        return '"begin" expected'
    
    scan()
    return_presence = False
    mistake = ''
    while not mistake:
        if nxtsymb[2] == 'return':
            return_presence = True
        if nxtsymb[2] == 'end':
            break
        mistake = operator(True)
        if mistake:
            return mistake
        if cursymb[0] == 'I' and nxtsymb[2] == ':':
            scan()
        else:
            scan()
            if nxtsymb[2] == ';':
                scan()
            else:
                return '";" expected'

    if not return_presence:
        return 'return expected in the end of function'
            
    if nxtsymb[2] != 'end':
        if cursymb[2] == ';' and nxtsymb[2] == 'else':
            return 'extra ";" before else'
        return 'unexpected "'+nxtsymb[2]+'"'
    scan()
    if nxtsymb[2] != ';':
        return '";" expected'
    scan()
    return ''

def operator():
#     print(Fore.GREEN + 'operator' + Style.RESET_ALL)
    print(get_token_name(nxtsymb), nxtsymb)
    if get_token_name(nxtsymb) == ';':
        pass
    elif nxtsymb[0] == 'I':
        scan()
        if get_token_name(nxtsymb) == ':':
            return ''
        if get_token_name(nxtsymb) in ['[', '(']:
            scan()
            if not check(expression()):
                return 'invalid array arguments'
            scan()
            while get_token_name(nxtsymb) == ',':
                scan()
                if not check(expression()):
                    return 'invalid array arguments'
                scan()
            if get_token_name(nxtsymb) not in [']', ')']:
                return '"]" expected'
            scan()
        if get_token_name(nxtsymb) == '=':
            if not check(assignment()):
                return 'invalid assignment declaration'
            return ''
        if get_token_name(nxtsymb) in ['(', '[']:
            scan()
            if not check(expression()):
                return 'invalid argument'
            scan()
            while get_token_name(nxtsymb) == ',':
                scan()
                if not check(expression()):
                    return 'invalid argument'
                scan()
            if get_token_name(nxtsymb) not in [')', ']']:
                return 'expected ")"'
            return ''
        return 'unexpected "'+get_token_name(nxtsymb)+'"'
    elif get_token_name(nxtsymb) == 'if':
        scan()
        if not check(condition()):
            return 'condition expected'
        scan()
        if get_token_name(nxtsymb) != 'then':
            return '"then" expected'
        scan()
        if not check(operators()):
            return 'operators expected'
        if get_token_name(nxtsymb) == 'end if':
            return ''
        elif get_token_name(nxtsymb) == 'else':
            scan()
            if not check(operators()):
                return 'operators expected'
            if get_token_name(nxtsymb) == 'end if':
                return ''
            else:
                return '"end if" expected'
        else:
            return '"else" or "end if" expected'
        return ''
    elif get_token_name(nxtsymb) == 'goto':
        scan()
        if nxtsymb[0] != 'I':
            return 'identifier expected'
        return ''
    elif get_token_name(nxtsymb) == 'while':
        scan()
        if not check(condition()):
            return 'condition expected'
        scan()
        if get_token_name(nxtsymb) != 'do':
            return '"do" expected'
        scan()
        if not check(operators()):
            return 'operators expected'
        if get_token_name(nxtsymb) != 'end while':
            return '"end while" expected'
        return ''
    elif get_token_name(nxtsymb) == 'dim':
        first_flag = True
        while get_token_name(nxtsymb) == ',' or first_flag:
            first_flag = False
            scan()
            if nxtsymb[0] != 'I':
                return 'identifier expected'
            scan()
            if get_token_name(nxtsymb) not in ['(', '[']:
                return '"(" expected'
            scan()
            if nxtsymb[0] not in ['C', 'I']:
                return 'length of array expected'
            scan()
            if get_token_name(nxtsymb) not in [')', ']']:
                return '")" expected'
            scan()
        antiscan()
    elif get_token_name(nxtsymb) == 'sub':
        scan()
        if nxtsymb[0] != 'I':
            return 'function name expected'
        scan()
        if get_token_name(nxtsymb) == '(':
            first_flag = True
            while get_token_name(nxtsymb) == ',' or first_flag:
                first_flag = False
                scan()
                if nxtsymb[0] != 'I':
                    return 'identifier expected'
                scan()
            if get_token_name(nxtsymb) != ')':
                return '")" expected'
            scan()
        if not check(operators()):
            return 'operators expected'
        print('NU SHO', get_token_name(nxtsymb))
        if get_token_name(nxtsymb) != 'end sub':
            return '"end sub" expected'
        return ''
    elif get_token_name(nxtsymb) == 'return':
        scan()
        if not check(expression()):
            return 'invalid expression'
        return ''
    else:
        return 'operator expected'
    return ''

def operators():
    scan()
    mistake = False
    while not mistake:
#         print('PERED:', get_token_name(nxtsymb), nxtsymb)
        mistake = operator()
#         print('OSHIBKA', mistake)
        if mistake:
            return ''
        if cursymb[0] == 'I' and get_token_name(nxtsymb) == ':':
            scan()
        else:
            scan()
#             print('POSLE:', get_token_name(nxtsymb), nxtsymb)
            if get_token_name(nxtsymb) == ';':
                scan()
                if get_token_name(nxtsymb) == 'stop':
                    return ''

def condition():
#     print(Fore.GREEN + 'condition' + Style.RESET_ALL)    
    if not check(expression()):
        return 'expression expected'
    scan()
    if get_token_name(nxtsymb) not in ['=', '>', '<', '>=', '<=', '<>']:
        return 'invalid comparasion operation'
    scan()
    if not check(expression()):
        return 'expression expected'
    return ''

def assignment():
#     print(Fore.GREEN + 'assignment' + Style.RESET_ALL)
    if get_token_name(nxtsymb) != '=':
        return '"=" expected'
    scan()
    if not check(expression()):
        return 'invalid expression'
    return ''

def expression():
#     print(Fore.GREEN + 'expression' + Style.RESET_ALL)    
    if not check(term()):
        return 'term expected'
    scan()
    while get_token_name(nxtsymb) in ['+', '-']:
        scan()
        if not check(term()):
            return 'term expected'
        scan()
    else:
        antiscan()
        pass
        
    return ''

def term():
#     print(Fore.GREEN + 'term' + Style.RESET_ALL)
    if not check(factor()):
        return 'factor expected'
    scan()
    while get_token_name(nxtsymb) in ['*', '/', '^']:
        scan()
        if not check(factor()):
            return 'factor expected'
        scan()
    else:
        antiscan()
        pass
        
    return ''

def factor():
#     print(Fore.GREEN + 'factor' + Style.RESET_ALL)
    if get_token_name(nxtsymb) == '(':
        scan()
        if not check(expression()):
            return 'expression expected'
        scan()
        if get_token_name(nxtsymb) != ')':
            return '")" expected'
    else:
        if not check(argument()):
            return 'constant or identifier expected'
    return ''

def argument():
#     print(Fore.GREEN + 'argument' + Style.RESET_ALL)
    if nxtsymb[0] not in ['I', 'C']:
        return 'constant or identifier expected'
    scan()
    if get_token_name(nxtsymb) in ['[', '(']:
        scan()
        if not(check(expression())):
            return 'invalid expression'
        scan()
        while get_token_name(nxtsymb) == ',':
            scan()
            if not(check(expression())):
                return 'invalid expression'
            scan()
        if get_token_name(nxtsymb) not in [']', ')']:
            return 'expected \']\' or \')\''
    else:
        antiscan()
    return ''

subprocess.run(["python", "lab1.py"])
with open('./lab1.json') as lab1_file:
    data = json.load(lab1_file)

tokens_chain = data['chain']
service_words = data['tables']['service_words']
operations = data['tables']['operations']
separators = data['tables']['separators']
constants = data['tables']['constants']
identifiers = data['tables']['identifiers']

new_tokens_chain = []
for item in tokens_chain:
    if get_token_name(item) != ' ':
        new_tokens_chain.append(item)
tokens_chain = list(new_tokens_chain)

nxtsymb = []
cursymb = []
token_index = -1

mistakes = []

def is_mistakes():
    check(wrapper())
    if mistakes:
        return mistakes[0]
    return False
# new_tokens_chain
with open('./checked.txt', 'w') as outfile:
    outfile.write(is_mistakes())


# if __name__ == '__main__':
#     print(is_mistakes())
