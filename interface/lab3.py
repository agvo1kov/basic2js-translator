import re
import sys
import pprint
import json
import subprocess

subprocess.run(["python", "lab2.py"])
with open('./lab2.json') as lab2_file:
    data = json.load(lab2_file)
rpn = data['rpn']
tables = data['tables']
service_words = data['tables']['service_words']
operations = data['tables']['operations']
separators = data['tables']['separators']
constants = data['tables']['constants']
identifiers = data['tables']['identifiers']

result = ''
stack = []
vars_declaring = []

function_context = None
while_context = None
if_m = None

for item in rpn:
    print(item)
    
    splitted = item.split(' ')
    if len(splitted) == 4:
        proc = 'КЦ'
    elif len(splitted) == 3:
        proc = 'ELSE'
        arity = splitted[0]
    else:
        [arity, proc,] = [0, item] if len(splitted) < 2 else splitted
    print(arity, '|', proc, stack)
#     print()
    if proc == 'НП':
        result += 'function '
        function_context = 'func'
    elif arity == 'НЦ':
        result += 'while ('
        while_context = 'while'
    elif proc == 'УПЛ' and while_context:
        result += str(stack.pop()) + ') {\n'
        while_context = None
    elif proc == 'УПЛ' and not while_context:
        result += 'if (' + str(stack.pop()) + ') {\n'
        if_m = str(arity) + ':'
    elif proc == 'ELSE':
        result += '} else {\n'
        if_m = str(arity) + ':'
    elif proc == if_m:
        result += '}\n'
    elif proc in ['КП', 'КЦ']:
        result += '}\n'
    elif proc in operations and proc != '=':
        b = stack.pop()
        a = stack.pop()
        stack.append(str(a) + ' ' + proc + ' ' + str(b))
    elif proc == 'НА':
        for i in range(int(arity)):
            var = stack.pop().split('[')
            result += var[0] + ' = new Array(' + var[1].split(']')[0] + ');\n'
    elif proc == '=':
        exp = stack.pop()
        result += str(stack.pop()) + ' = ' + str(exp) + ';\n'
    elif proc == 'Ф':
        args = ''
        for i in range(int(arity) - 1):
            args = stack.pop() + ', ' + args
        args = args[:-2]
        stack.append(str(stack.pop()) + '(' + args + ')')
        if function_context:
            result += str(stack.pop()) + ' {\n'
            function_context = None
    elif proc == 'АЭМ':
        args = ''
        for i in range(int(arity) - 1):
            args = stack.pop() + ', ' + args
        args = args[:-2]
        stack.append(str(stack.pop()) + '[' + args + ']')
    elif proc == 'RETURN':
        result += 'return ' + str(stack.pop()) + ';\n'
    else:
        print('\"' + str(proc) + '" <> "' + str(if_m) + '"')
        stack.append(proc)

# print(stack)
# print()
# print(result)

with open('./result.js', 'w') as outfile:
    outfile.write(result)

# if __name__ == '__main__':
#     print(goToCPP())
