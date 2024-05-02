# Written in Python 3.10.12. Python 3.8+ needed at minimum to use pathlib.Path().unlink with missing_ok
import argparse
import pathlib
import os

from AssemblyPrinter import AssemblyPrinter

parser = argparse.ArgumentParser("VMTranslator")
parser.add_argument("vmfilepath", help="The target VM file/directory to be translated to .asm", type=str)
args = parser.parse_args()

print(args.vmfilepath + " is the target file/directory")

vmFiles = [];
asmFilename = "";

isVmFolder = os.path.isdir(args.vmfilepath)
if isVmFolder:
    for vmFile in os.listdir(args.vmfilepath):
        if vmFile.endswith(".vm"):
            vmFiles.append(args.vmfilepath + "/" + vmFile)
    asmFilename = args.vmfilepath + "/" + os.path.basename(args.vmfilepath) + ".asm"
else:
    vmFiles.append(args.vmfilepath)
    asmFilename = args.vmfilepath.replace(".vm", ".asm")


asmPrinter = AssemblyPrinter()

# unlink and overwrite any existing file rather than append to it
pathlib.Path(asmFilename).unlink(missing_ok=True)
with open(asmFilename, 'a+') as asmfile:
    
    
    for vmFilename in vmFiles:
        with open(vmFilename) as vmfile:
            
            for line in vmfile:

                if line.startswith("//") or not line.strip():
                    continue

                asmfile.write("//" + line)

                asmOutput = asmPrinter.TranslateVMToAssembly(line)

                for asmLine in asmOutput:
                    asmfile.write(asmLine + "\n")

      
print("End VMTranslator")



