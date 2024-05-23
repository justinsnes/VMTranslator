# Written in Python 3.10.12. Python 3.8+ needed at minimum to use pathlib.Path().unlink with missing_ok
import argparse
import pathlib
import os

from AssemblyPrinter import AssemblyPrinter

parser = argparse.ArgumentParser("VMTranslator")
parser.add_argument("vmfilepath", help="The target VM file/directory to be translated to .asm", type=str)
args = parser.parse_args()

# expanduser translates ~ to the exact path it represents. needed on Windows
targetFilepath = os.path.expanduser(args.vmfilepath)
print(targetFilepath + " is the target file/directory")

vmFiles = [];
asmFilename = "";

isVmFolder = os.path.isdir(targetFilepath)
if isVmFolder:
    for vmFile in os.listdir(targetFilepath):
        if vmFile.endswith(".vm"):
            vmFiles.append(targetFilepath + "/" + vmFile)
    asmFilename = targetFilepath + "/" + os.path.basename(targetFilepath) + ".asm"
else:
    vmFiles.append(targetFilepath)
    asmFilename = targetFilepath.replace(".vm", ".asm")


asmPrinter = AssemblyPrinter()

# unlink and overwrite any existing file rather than append to it
pathlib.Path(asmFilename).unlink(missing_ok=True)
with open(asmFilename, 'a+') as asmfile:
    
    # if there are multiple VM files, we need to use Bootstrap Code
    if len(vmFiles) > 1:
        asmOutput = asmPrinter.TranslateVMToAssembly("bootstrap")
        for asmLine in asmOutput:
            asmfile.write(asmLine + "  // line " + str(asmPrinter.asmLineNumber) + "\n")
            if (not (asmLine.startswith("(") or asmLine.startswith("//")) ):
                asmPrinter.asmLineNumber += 1

    for vmFilename in vmFiles:
        with open(vmFilename) as vmfile:
            
            asmPrinter.currentVmFileClass = pathlib.Path(vmFilename).stem

            for line in vmfile:

                if line.startswith("//") or not line.strip():
                    continue

                asmfile.write("\n")
                asmfile.write("//" + line)

                asmOutput = asmPrinter.TranslateVMToAssembly(line)

                for asmLine in asmOutput:
                    asmfile.write(asmLine + "  // line " + str(asmPrinter.asmLineNumber) + "\n")
                    if (not (asmLine.startswith("(") or asmLine.startswith("//")) ):
                        asmPrinter.asmLineNumber += 1

      
print("End VMTranslator")



