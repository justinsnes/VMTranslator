class AssemblyPrinter:
    def __init__(self):
        self.jumpCounter = 0

    def incrementStackPointer(self, asmLines):
        asmLines.append("@SP")
        asmLines.append("M=M+1")
    
    def popLastTwoDM(self, asmLines):
        asmLines.append("@SP")
        asmLines.append("M=M-1")
        asmLines.append("A=M")
        asmLines.append("D=M")
        asmLines.append("@SP")
        asmLines.append("M=M-1")
        asmLines.append("A=M")

    def TranslateMathLogic(self, vmcommand):
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
        elif vmcommand in ["add", "sub"]:
            self.popLastTwoDM(asmLines)
            if (vmcommand.startswith("add")):
                asmLines.append("M=M+D")
            elif (vmcommand.startswith("sub")):
                asmLines.append("M=M-D")
        elif vmcommand in ["neg", "not"]:
            asmLines.append("@SP")
            asmLines.append("M=M-1")
            asmLines.append("A=M")
            if (vmcommand.startswith("neg")):
                asmLines.append("M=-M")
            elif (vmcommand.startswith("not")):
                asmLines.append("M=!M")
        # the VM represents true as -1(0x1111/1111111111111111) and false as 0(0x0000/0000000000000000)
        elif vmcommand in ["eq", "lt", "gt", "and", "or"]:
            # pop and prepare to compare both values in D and M
            self.popLastTwoDM(asmLines)
            # use subtract or logic to see what the value between the two are.
            if vmcommand in ["eq", "lt", "gt"]:
                asmLines.append("D=M-D")
                # default SP value to TRUE. 
                asmLines.append("M=-1")
                # if it actually IS true, skip over assigning back to FALSE to (ISTRUE) label
                asmLines.append("@ISTRUE" + str(self.jumpCounter) + "")
                asmLines.append("D;J" + vmcommand.upper())
                # this part sets the SP location to FALSE instead if the condition is not TRUE
                asmLines.append("@SP")
                asmLines.append("A=M")
                asmLines.append("M=0")
                asmLines.append("(ISTRUE" + str(self.jumpCounter) + ")")
                self.jumpCounter += 1
            elif vmcommand.startswith("and"):
                asmLines.append("M=D&M")
            elif vmcommand.startswith("or"):
                asmLines.append("M=D|M")

        self.incrementStackPointer(asmLines)

        return asmLines

