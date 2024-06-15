# Trichotomy master program
# Copyright (C) 2022 McChuck
# Released under GNU General Public License
# See LICENSE for more details.
# Many thanks to Chris Lloyd (github.com/cjrl) and Lawrence Woodman for inspiration and examples.
# Check out         https://techtinkering.com/articles/subleq-a-one-instruction-set-computer/
# And especially    https://techtinkering.com/2009/05/15/improving-the-standard-subleq-oisc-architecture/
# And maybe watch   https://www.youtube.com/watch?v=FvwcRaE9yxc

import sys
import os
from parser import Parser
from vm import VM
try:
    from getch import getch, getche         # Linux
except ImportError:
    from msvcrt import getch, getche        # Windows


def Write_slc(slc_file, mem):
    maxpc = len(mem)
    slc_file.write('{}  # START\n'.format(mem[0]))
    pc = 1
    while pc < maxpc:
        a = mem[pc]
        slc_file.write('{: >6} '.format(a))
        pc += 1
        if pc % 3 == 1 and pc > 1:
            slc_file.write('  # Lines {: >4} - {: >4}\n'.format(pc-3, pc-1))
    slc_file.write('  # Last: {} \n'.format(pc-1))


def Trichotomy(args):
    try:
        sla_name = args[0]
        slc_name = None
        if len(args) > 1:
            slc_name = args[1]
        parser = Parser()
        mem = []
        with open(sla_name, "r") as sla_file:
            raw = sla_file.read()
            sla_file.close()
        mem = parser.parse(raw)
        if  slc_name != None:
            with open(slc_name, "w") as slc_file:
                Write_slc(slc_file, mem)
                slc_file.close()
        VM.execute(mem)
    except(ValueError, IndexError):
        print("I just don't know what went wrong!\n")
        sla_file.close()

def main(args):
    try:
        print()
        if len(args) == 1:
            Trichotomy(args)
        elif len(args) == 2:
            if os.path.isfile(args[1]):
                print(args[1], "exists.  Overwrite? ", end="", flush=True)
                answer = getche()
                if answer in [b'y', b'Y']:
                    print()
                    print(args[1], "replaced \n\n", flush=True)
                    Trichotomy(args)
                else:
                    print()
                    print(args[1], "retained \n\n", flush=True)
                    Trichotomy([args[0]])
            else:
                print("creating", args[1], "\n\n", flush=True)
                Trichotomy(args)
        else:
            print("usage: python trichotomy.py infile.sla [outfile.slc]\n")
    except FileNotFoundError:
        print("< *Peter_Lorre* >\nYou eediot!  What were you theenking?\nTry it again, but thees time with a valid file name!\n</ *Peter_Lorre* >\n")
        print("usage: python trichotomy.py infile.sla [outfile.slc]\n")


if __name__ == '__main__':
    main(sys.argv[1:])
