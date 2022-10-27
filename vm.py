# Subleq Improved Virtual Machine
# Copyright (C) 2022 McChuck
# original Copyright (C) 2013 Chris Lloyd
# Released under GNU General Public License
# See LICENSE for more details.
# https://github.com/cjrl
# This Subleq Virtual Machine was based on the pseudocode from the OSIC Wikipedia article:
# http://en.wikipedia.org/wiki/One_instruction_set_computer

try:
    from getch import getch, getche         # Linux
except ImportError:
    from msvcrt import getch, getche        # Windows

class VM:
    @staticmethod 
    def execute(mem):
        pointer = int(mem[0])        #   Instruction Pointer initialized to the first number in the file!  MANDATORY!
        running = True
        maxmem = len(mem)-1
        return_stack = []
        data_stack = []
        if pointer <= 0 or pointer > (maxmem - 2):
            print("/nInstruction pointer out of bounds at program init./n")
            running = False
            raise IndexError

        def deref(where):
            index = int(where)
            if out_of_bounds(index):
                print(" at instruction location: ", where, flush=True)
                raise IndexError
            if index < 0:
                index = mem[abs(index)]
                if index < 0:
                    print("Dereferenced location", index, "from", where, "is negative.")
                    raise IndexError
            return index

        def out_of_bounds(where):
            if abs(where) > maxmem:
                print("\nReference out of bounds:", where, end="")
                return True
            else:
                return False

        while running:
            try:
                a = mem[pointer]
                b = mem[pointer+1]
                c = mem[pointer+2]
                ap = deref(a)
                bp = deref(b)
                cp = deref(c)
                a_val = mem[ap]
                b_val = mem[bp]
                c_val = mem[cp]
                next_ip = pointer + 3

                # print(pointer, "A", a, ap, a_val, "B", b, bp, b_val, "C", c, cp, c_val, flush=True)

                if a != 0 and b != 0 and c != 0:        # SUBLEQ A B C
                    mem[cp] = b_val - a_val

                elif a != 0 and b == 0 and c == 0:      # PUSH A 0 0
                    data_stack.append(a_val)

                elif a == 0 and b == 0 and c != 0:      # POP 0 0 C
                    if len(data_stack) > 0:
                        mem[cp] = data_stack.pop(-1)
                    else:
                        print("Cannot pop from an empty stack @", pointer, flush=True)
                        print("A", a, ap, a_val, "B", b, bp, b_val, "C", c, cp)
                        running = False

                elif a == 0 and b != 0 and c == 0:      # RET? 0 B 0
                    if b_val <= 0:
                        if len(return_stack) > 0:
                            next_ip = return_stack[-1]
                            return_stack.pop(-1)
                        else:
                            print("Attempted to return from an empty stack @", pointer, flush=True)
                            print("A", a, ap, a_val, "B", b, bp, b_val, "C", c, cp)
                            running = False

                elif a != 0 and b == 0 and c != 0:      # GOTO? A 0 C
                    if a_val <= 0:
                        if cp <= 0:
                            print("\nInvalid address:", cp, "  Halted @:", pointer, "\n")
                            running = False
                        else:
                            next_ip = cp

                elif a == 0 and b != 0 and c != 0:      # CALL? 0 B C
                    if b_val <= 0:
                        if cp <= 0:
                            print("\nInvalid address:", cp, "  Halted @:", pointer, "\n")
                            running = False
                        else:
                            next_ip = cp
                            return_stack.append(pointer+3)

                elif a != 0 and b != 0 and c == 0:      # I/O   A B 0   where A is the target and B is the format
                    if b > 0:                               # Print
                        if b == 1:                              # character
                            if a_val >= 0:
                                print(chr(a_val), end="", flush=True)
                            else:
                                print("\nInvalid character:", a_val, " @ memory:", ap, " @ instrtuction:", pointer)
                                running = False
                                raise ValueError
                        else:                                   # number
                            print(a_val, end="", flush=True)
                    else:                                   # Input character
                        if b == -1:                             # echo
                            mem[ap] = ord(getche())
                        else:                                   # no echo
                            mem[ap] = ord(getch())

                else:                                   # HALT 0 0 0
                    print("\n\n\nProgram successfully halted @", pointer, "\n", flush=True)
                    running = False


                pointer = next_ip
                mem[0] = pointer
                if pointer <= 0 or pointer > (maxmem - 2):
                    running = False
                    raise IndexError

            except IndexError:
                print("Memory out of bounds error at instruction", pointer)
                print("A", a, ap, a_val, "B", b, bp, b_val, "C", c, cp, c_val)
                running = False
            except ValueError:
                print("Value error at instruction", pointer)
                print("A", a, ap, a_val, "B", b, bp, b_val, "C", c, cp, c_val)
                running = False
