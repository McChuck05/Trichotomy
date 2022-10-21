# Trichotomy
Similar to Subleq Improved, but A B C where [C] = [B] - [A].
Also has push and pop to a stack, a conditional goto, conditional call, conditonal return, and unconditional halt.

See the Trichotomy page on the Esolangs wiki for detailed information.

https://esolangs.org/wiki/Trichotomy

Format:

A B C    C = B - A
A 0 C    If A <= 0, goto C
0 B C    If B <= 0, call C
0 B 0    If B <= 0, return.  Halt if the return stack is empty.
A B 0    Perform I/O with A as a target and B as the format
            1:  Print A as a character
            2+: Print A as a number
            -1: Input a character with echo, store its value in A
            -2-:Input a character without echo, store its value in A
A 0 0    Push A to the stack
0 0 C    Pop the top of stack to C
0 0 0    Halt

Assembler (parser) instructions:

