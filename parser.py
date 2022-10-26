 # Trichotomy Parser
 # Copyright (C) 2022 McChuck
 # original Copyright (C) 2013 Chris Lloyd
 # Released under GNU General Public License
 # See LICENSE for more details.
 # https://github.com/cjrl
 # lloyd.chris@verizon.net

 #  The first instruction (memory location 0) MUST be the start address of the code to execute.

 #  A B C       [C] = [B] - [A]        Like Subleq, but with a subtraction target instead of a conditional address
 #  A *B -C     [[C]] = [[B]] - [A]    Indirect addressing, accomplished through negative addresses
 #  shorthand:
 #      A B         [B] = [B] - [A]    (A B B)
 #      A           [A] = 0            (A A A)

 #  A 0 C       if [A] <= 0, GOTO C (Halt if C <= 0)
 #  0 B C       if [B] <= 0, CALL C (Halt if c <= 0)
 #  0 B 0       if [B] <= 0, RETURN (Halt if return stack is empty)
 #  A B 0       perform I/O on [A] with format [B]
 #                  1:  print character
 #                  2+: print number
 #                  -1: input character with echo
 #                  -2-:input character without echo
 #  A 0 0       PUSH [A] onto the stack
 #  0 0 C       POP the top of stack to C
 #  0 0 0       HALT



 #  ?           next address
 #  @           this address
 #  label:      address label, cannot be the only thing on a line
 #  *label      pointer to address label, represented as a negative address
 #                  labels can end with +n or -n, where n is a number of addresses to offset by
 #                  For example, "@+1" = "?"
 #  !           0
 #                  Convenient marker for goto, call, return, push, pop, input, output, and halting
 #  ;           end of instruction
 #  #           comment
 #  .           data indicator, keeps parser from trying to read as shorthand
 #  " or '      string delimeters, must be data

 #  //import    Imports a module and appends its code at the end.  The file name must end in ".slm"
 #                  Modules cannot import other modules.


import sys
import os

class Parser:

    tokens = []
    label_table = {}

    def parse(self, raw_string):
        raw_string = self.expand_literals(raw_string)
        raw_string = self.format_chars(raw_string)
        self.tokens = self.strip_tokens(raw_string)
        self.import_modules()
        self.parse_labels()
        self.handle_macros()
        self.expand_instructions()
        self.update_labels()
        self.tokens = [token for token in sum(self.tokens,[]) if token != '.']
        self.resolve_labels()
        try:
            response = []
            for token in self.tokens:
                response.append(int(token))
            return(response)
        except ValueError:
            print("Unmatched label:", token, flush=True)
            raise


    def expand_literals(self, starting_string):
        in_dq_literal = False       # "
        in_sq_literal = False       # '
        in_comment  = False
        expanded_string = ""
        for char in starting_string:
            if char == "#" and not in_sq_literal and not in_dq_literal:
                in_comment = True
            if in_comment:
                if ord(char) == 10 or ord(char) == 13:
                    in_comment = False
                else:
                    char = ""
            if char == '"' and not in_sq_literal:
                in_dq_literal ^= True
            elif char == "'" and not in_dq_literal:
                in_sq_literal ^= True
            elif in_dq_literal or in_sq_literal:
                expanded_string += str(ord(char)) + ' '
            else:
                expanded_string += char
        return expanded_string


    def format_chars(self, starting_string):
        new_string = starting_string.replace('\n',';')
        new_string = new_string.replace('#',';#')
        new_string = new_string.replace(':',': ')
        new_string = new_string.replace('.','. ')
        new_string = new_string.replace('!', "0 ")
        new_string = new_string.replace(',', ' ')
        return new_string


    def strip_tokens(self, string):
        stripped_tokens=[]
        stripped_tokens = [token.split() for token in string.split(';') if not '#' in token and token.strip()]
        if 'ZERO:' not in sum(stripped_tokens, start=[]):
            stripped_tokens.append(['.', 'ZERO:', '0'])
        return stripped_tokens


    def import_modules(self):
        tokens_to_remove = []
        for token_index, token in enumerate(self.tokens):
            if token[0] == "//import":
                if len(token) == 1:
                    print("No file to be imported named.\n", flush=True)
                    raise ValueError
                else:
                    mod_name = token[1] + ".slm"
                    if not os.path.isfile(mod_name):
                        print("Module >", mod_name, "< not found.\n", flush=True)
                        raise ValueError
                    else:
                        mod_raw = ""
                        mod_tokens = []
                        with open(mod_name, "r") as mod_file:
                            mod_raw = mod_file.read()
                            mod_file.close()
                        mod_raw = self.expand_literals(mod_raw)
                        mod_raw = self.format_chars(mod_raw)
                        mod_tokens = self.strip_tokens(mod_raw)
                        self.tokens.extend(mod_tokens)      # extend strips off the outer list layer
                        tokens_to_remove.append(token_index)
        tokens_to_remove.reverse()      # clean up
        if len(tokens_to_remove) > 0:
            for token in tokens_to_remove:
                self.tokens.pop(token)


    def parse_labels(self):
        for token_index, token in enumerate(self.tokens):
            if len(token) == 1 and token[0][-1] == ':':                         # correcting for lone label
                token.extend(self.tokens[token_index+1])
                self.tokens.pop(token_index+1)
            for operand_index, operand in enumerate(token):
                if operand[-1] == ':':
                    token.remove(operand)
                    operand = operand[:-1]
                    self.label_table[operand] = (token_index, operand_index)


    def handle_macros(self):
        for i, token in enumerate(self.tokens):
            instr = token[0]
            if instr[0] == '/':
                self.tokens[i].remove(instr)
                count = len(token)

                if instr == "/subleq" or instr == "/sub":                                           # A B C  where [C] = [B] - [A]
                    if count == 0 or count > 3:
                        self.macro_fail(instr, token)

                elif instr == "/jmp" or instr == "/jmp?" or instr == "/goto" or instr == "/goto?":  # A 0 C
                    if count == 1:      # unconditional
                        self.tokens[i].insert(0, 'ZERO')
                        self.tokens[i].insert(1, '0')
                    elif count == 2:
                        self.tokens[i].insert(1, '0')
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/jsr" or instr == "/jsr?" or instr == "/call" or instr == "/call?":  # 0 B C
                    if count == 1:      # unconditional
                        self.tokens[i].insert(0, '0')
                        self.tokens[i].insert(1, 'ZERO')
                    elif count == 2:
                        self.tokens[i].insert(0, '0')
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/ret" or instr == "/ret?" or instr == "/return" or instr == "/return?":                                           # 0 B 0
                    if count == 0:                  # unconditional
                        self.tokens[i] = ['0', 'ZERO', '0']
                    elif count == 1:
                        self.tokens[i].insert(0, '0')
                        self.tokens[i].append('0')
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/push":                                                              # A 0 0
                    if count == 1:
                        self.tokens[i].extend(['0', '0'])
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/pop":                                                               # 0 0 C
                    if count == 1:
                        self.tokens[i].insert(0, '0')
                        self.tokens[i].insert(0, '0')
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/io" or instr == "/inout":                                           # A B 0
                    if count == 2:
                        self.tokens[i].append('0')
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/print" or instr == "/output" or instr == "/out":                    # A B 0 where B > 0
                    if count == 2:                  # formatted output
                        self.tokens[i].append('0')
                    elif count == 1:                # assume character output
                        self.tokens[i].append('1')
                        self.tokens[i].append('0')
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/input" or instr == "/in":                                           # A B 0 where B < 0
                    if count == 2:                  # formatted input
                        self.tokens[i].append('0')
                    elif count == 1:                # assume inptut is echoed
                        self.tokens[i].append('-1')
                        self.tokens[i].append('0')
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/copy" or instr == "/move":                                         # ZERO B C meta command
                    if count == 2:
                        self.tokens[i].insert(0, "ZERO")
                    else:
                        self.macro_fail(instr, token)

                elif instr == "/halt":                                                              # 0 0 0
                    self.tokens[i] = ['0', '0', '0']

                else:
                    self.macro_fail(instr, token)


    def expand_instructions(self):                      #   handle shorthand
        if not self.tokens[0][0] == '.':
            self.tokens[0].insert(0, '.')                   #   mem[0] = instruction pointer, mark as data
        for token_index, token in enumerate(self.tokens):
            if not token[0] == '.':                         #   ignore data
                num_tokens = len(token)                     #   standard form is A B C
                if num_tokens == 1:
                    operands = [token[0],token[0],token[0]]     # A = A - A
                elif num_tokens == 2:
                    operands = [token[0], token[1], token[1]]   # B = B - A
                elif num_tokens == 3:
                    operands = [token[0], token[1], token[2]]   # C = B - A
                else:
                    print("Incorrect number of addresses @:", token_index, token, "\n", flush=True)
                    raise ValueError
                self.tokens[token_index] = operands


    def update_labels(self):
        for i, label in enumerate(self.label_table):
            self.label_table[label] = self.get_label_index(label)


    def resolve_labels(self):
        try:
            for i, token in enumerate(self.tokens):
                modifier = 0
                plus = token.find('+')
                minus = token.find('-')
                if plus > 0:
                    modifier = int(token[plus:])
                    token = token[:plus]
                elif minus > 0:
                    modifier = int(token[minus:])
                    token = token[:minus]
                if token == '?':     # next IP
                        self.tokens[i] = i+1+modifier
                elif token == '@':   # this IP
                        self.tokens[i] = i+modifier
                elif token[0] == "*":     # pointer
                    token = token[1:]
                    if token in self.label_table:
                        self.tokens[i] = -(self.label_table[token]+modifier)
                else:
                    if token in self.label_table:
                        self.tokens[i] = self.label_table[token]+modifier
        except:
            print("\nError resolving label: ", token, " @ ", i, flush=True)
            raise


    def get_label_index(self,label):
        index = 0
        address, x = self.label_table[label]
        for i in range(address):
            index += len(self.tokens[i])
            if '.' in self.tokens[i][0]:
                index -= 1 
        if '.' in self.tokens[address][0]:
            return index + x - 1
        return index


    def macro_fail(self, instr, token):
        print("Macro", instr, "failed at", token)
        raise ValueError

