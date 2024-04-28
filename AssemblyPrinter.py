class AssemblyPrinter:
    def __init__(self):
        pass

    def TranslateMathLogic(vmcommand):
        vmcommand = vmcommand.replace('\n', '').replace('\r', '')
        asmLines = []
        if vmcommand.startswith("push"):
            words = vmcommand.split(" ")
            action = vmcommand[0]
            memoryLocation = words[1]
            offset = words[2]

            if (memoryLocation == "constant"):
                asmLines.append("@" + offset)
                asmLines.append("D=A")

            asmLines.append("@SP")
            asmLines.append("A=M")
            asmLines.append("M=D")
            asmLines.append("@SP")
            asmLines.append("M=M+1")
        elif vmcommand.startswith("add"):
            asmLines.append("@SP")
            asmLines.append("M=M-1")
            asmLines.append("A=M")
            asmLines.append("D=M")
            asmLines.append("@SP")
            asmLines.append("M=M-1")
            asmLines.append("A=M")
            asmLines.append("M=M+D")
            asmLines.append("@SP")
            asmLines.append("M=M+1")

        return asmLines

