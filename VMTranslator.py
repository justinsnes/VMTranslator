# Written in Python 3.10.12. Python 3.8+ needed at minimum to use pathlib.Path().unlink with missing_ok
import argparse
import pathlib

from AssemblyPrinter import AssemblyPrinter

parser = argparse.ArgumentParser("VMTranslator")
parser.add_argument("vmfilepath", help="The target VM file to be translated to .asm", type=str)
args = parser.parse_args()

print(args.vmfilepath + " is the target file")

asmfilename = pathlib.Path(args.vmfilepath).name.replace(".vm", ".asm")

with open(args.vmfilepath) as vmfile:
    pathlib.Path(asmfilename).unlink(missing_ok=True)
    with open(asmfilename, 'a') as asmfile:
        for line in vmfile:

            if line.startswith("//") or not line.strip():
                continue

            asmfile.write("//" + line)

            asmOutput = AssemblyPrinter.TranslateMathLogic(line)
            for asmLine in asmOutput:
                asmfile.write(asmLine + "\n")

            

print("End VMTranslator")



