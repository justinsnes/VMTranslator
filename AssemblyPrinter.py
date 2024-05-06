class AssemblyPrinter:
    def __init__(self):
        self.jumpCounter = 0
        self.vmToAsmMemory = {"local":"LCL","argument":"ARG","this":"THIS","that":"THAT",
                              "temp":"R5","pointer":"THIS","static":"16"}

    def incrementStackPointer(self, asmLines):
        asmLines.append("@SP")
        asmLines.append("M=M+1")

    def popStack(self, asmLines):
        asmLines.append("@SP")
        asmLines.append("M=M-1")
        asmLines.append("A=M")
        asmLines.append("D=M")
    
    def popLastTwoDM(self, asmLines):
        self.popStack(asmLines)
        asmLines.append("@SP")
        asmLines.append("M=M-1")
        asmLines.append("A=M")

    def TranslateVMToAssembly(self, vmcommand):
        vmcommand = vmcommand.replace('\n', '').replace('\r', '').replace('\t', '')
        vmcommand = vmcommand.strip() # remove leading and trailing whitespace
        asmLines = []
        words = vmcommand.split(" ")
        action = words[0]

        if action in ["label", "goto", "if-goto"]:
            labelName = words[1]
            self.TranslateProgramFlow(asmLines, action, labelName)
        elif action in ["push", "pop"]:
            memoryLocation = words[1]
            offset = words[2]
            self.TranslateMemoryAccess(asmLines, action, memoryLocation, offset)
        elif action in ["add", "sub", "neg", "not", "eq", "lt", "gt", "and", "or"]:
            self.TranslateMathLogic(asmLines, action)
        
        return asmLines


    def TranslateMathLogic(self, asmLines, action):
        if action in ["add", "sub"]:
            self.popLastTwoDM(asmLines)
            if (action == "add"):
                asmLines.append("M=M+D")
            elif (action == "sub"):
                asmLines.append("M=M-D")
        elif action in ["neg", "not"]:
            asmLines.append("@SP")
            asmLines.append("M=M-1")
            asmLines.append("A=M")
            if (action == "neg"):
                asmLines.append("M=-M")
            elif (action == "not"):
                asmLines.append("M=!M")
        # the VM represents true as -1(0x1111/1111111111111111) and false as 0(0x0000/0000000000000000)
        elif action in ["eq", "lt", "gt", "and", "or"]:
            # pop and prepare to compare both values in D and M
            self.popLastTwoDM(asmLines)
            # use subtract or logic to see what the value between the two are.
            if action in ["eq", "lt", "gt"]:
                asmLines.append("D=M-D")
                # default SP value to TRUE. 
                asmLines.append("M=-1")
                # if it actually IS true, skip over assigning back to FALSE to (ISTRUE) label
                asmLines.append("@ISTRUE" + str(self.jumpCounter) + "")
                asmLines.append("D;J" + action.upper())
                # this part sets the SP location to FALSE instead if the condition is not TRUE
                asmLines.append("@SP")
                asmLines.append("A=M")
                asmLines.append("M=0")
                asmLines.append("(ISTRUE" + str(self.jumpCounter) + ")")
                self.jumpCounter += 1
            elif action == "and":
                asmLines.append("M=D&M")
            elif action == "or":
                asmLines.append("M=D|M")

        self.incrementStackPointer(asmLines)


    def TranslateMemoryAccess(self, asmLines, action, memoryLocation, offset):
        if action == "push":
            if (memoryLocation == "constant"):
                asmLines.append("@" + offset)
                asmLines.append("D=A")
            elif (memoryLocation in self.vmToAsmMemory):
                asmLines.append("@" + self.vmToAsmMemory[memoryLocation])
                if (memoryLocation in ["temp","pointer","static"]):
                    asmLines.append("D=A")
                else:
                    asmLines.append("D=M")
                asmLines.append("@" + offset)
                asmLines.append("D=D+A")
                asmLines.append("A=D")
                asmLines.append("D=M")

            asmLines.append("@SP")
            asmLines.append("A=M")
            asmLines.append("M=D")

            self.incrementStackPointer(asmLines)

        if action == "pop":
            asmLines.append("@" + self.vmToAsmMemory[memoryLocation])
            if (memoryLocation in ["temp","pointer","static"]):
                asmLines.append("D=A")
            else:
                asmLines.append("D=M")
            asmLines.append("@" + offset)
            asmLines.append("D=D+A")
            asmLines.append("@R13")
            asmLines.append("M=D")
            self.popStack(asmLines)
            asmLines.append("@R13")
            asmLines.append("A=M")
            asmLines.append("M=D")
            
    def TranslateProgramFlow(self, asmLines, flowCommand, labelName):
        if flowCommand == "label":
            asmLines.append("(" + labelName + ")")
        elif flowCommand == "if-goto":
            self.popStack(asmLines)
            asmLines.append("@" + labelName)
            asmLines.append("D;JNE")
        elif flowCommand == "goto":
            asmLines.append("@" + labelName)
            asmLines.append("0;JMP")

    def TranslateFunctionLine(self):
        pass
