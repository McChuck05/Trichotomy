# Trichotomy
Similar to Subleq Improved, but A B C where [C] = [B] - [A].
Also has push and pop to a stack, a conditional goto, conditional call, conditonal return, and unconditional halt.

See the Trichotomy page on the Esolangs wiki for detailed information.

https://esolangs.org/wiki/Trichotomy

Usage:  python trichotomy.py infile (outfile)

The outfile is optional, but will contain just the code numbers in three columns, with addresses.  It will prompt you if an existing outfile is named.


Format:

The first number in the program file (memory location 0) must be the address where the first instruction to be executed is located.

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
 
Assembler instructions

     @        This address
     ?        The following address
     !        0, useful for indicating alternate functions
     \#       What follows is a comment
     \*        Indirection.  Makes the following address negative.
     " '      Quoted strings.  Can use the other mark inside.  Good form is to follow a string with a 0.
     .        Data marker.  Data is unformatted, where instructions are always three integers.
     :        At the end of a word creates a symbol, which the parser uses as an alias for an address.  
                  Note that symbols are used without the trailing colon.
                  Example:   .Message1: ? "The quick brown fox jumps over the lazy dog." 0          
     + -      Appended to a symbol allows simple math.  ? is equivalent to @+1.
     ZERO     An addressed value of 0, automatically added by the compiler if not already present.
     ;        Separates commands.
     /        Prepends an assembler macro.
        /sub A B C   C = B-A  Not necessary, but available.  Alternate: /subleq
        /sub A B     B = B-A  shorthand.  The "/sub" is not necessary.
        /sub A       A = A-A  shorthand.  The "/sub" is not necessary.
        /goto A C    If A is omitted, ZERO is inserted to make the branch mandatory.  Alternates: /goto? /jmp /jmp?  
        /call B C    If B is omitted, ZERO is inserted to make the branch mandatory.  Alternates: /call? /jsr /jsr? 
        /return B    If B is omitted, ZERO is inserted to make the branch mandatory.  Alternate: /return? /ret /ret? 
        /io A B      Perform input or output with A as target and B as format.  Alternate:  /inout
                         1: print character  2: print number  -1: echo input character  -2: noecho input character                    
        /print A     Prints A as a character.  "/print A 2" will print A as a number.  Alternates:  /output /out   
        /input A     Inputs a character to A.  "/input A -2" will input without echo.  Alternate:  /in
    /push A      Pushes A onto the stack.
    /pop C       Pops the top of stack and stores it in C.
    /halt        Unconditional program halt.
    /copy B C    Equivalent to ZERO B C.  Alternate:  /move
    
