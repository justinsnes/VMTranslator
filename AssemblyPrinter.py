class AssemblyPrinter:
    def __init__(self):
        self.jumpCounter = 0
        self.vmToAsmMemory = {"local":"LCL","argument":"ARG","this":"THIS","that":"THAT",
                              "temp":"R5","pointer":"THIS","static":"16"}

    currentFnParamCount = 0
    asmLineNumber = 0

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

    def setupSymbolInSavedFrame(self, asmLines, symbolName):
        asmLines.append(symbolName)
        asmLines.append("D=M")
        asmLines.append("@SP")
        asmLines.append("A=M")
        asmLines.append("M=D")
        self.incrementStackPointer(asmLines)

    def TranslateVMToAssembly(self, vmcommand):
        vmcommand = vmcommand.replace('\n', '').replace('\r', '').replace('\t', '')
        vmcommand = vmcommand.strip() # remove leading and trailing whitespace
        asmLines = []
        words = vmcommand.split(" ")
        action = words[0]

        if action in ["label", "goto", "if-goto"]:
            labelName = words[1]
            self.TranslateProgramFlow(asmLines, action, labelName)
        elif action in ["function", "call"]:
            functionName = words[1]
            numParameters = int(words[2])
            self.TranslateFunctionLine(asmLines, action, functionName, numParameters)
        elif action == "return":
            self.TranslateFunctionLine(asmLines, action, "", 0)
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

    def TranslateFunctionLine(self, asmLines, fnCommand, fnName, numParams):
        if fnCommand == "function":
            self.currentFnParamCount = numParams
            asmLines.append("(" + fnName + ")")
            # set LCL symbol
            asmLines.append("@SP")
            asmLines.append("D=M")
            asmLines.append("@LCL")
            asmLines.append("M=D")
            # setup local variables and set them to 0
            for param in range(numParams):
                asmLines.append("@SP")
                asmLines.append("A=M")
                asmLines.append("M=0")
                self.incrementStackPointer(asmLines)
        elif fnCommand == "call":
            # call uses R13 for the function's @ARG location
            #store future @ARG location in R13
            for param in range(numParams):
                self.popStack(asmLines)
            asmLines.append("@SP")
            asmLines.append("D=M")
            asmLines.append("@R13")
            asmLines.append("M=D")
            # go back after setting @ARG location
            for param in range(numParams):
                self.incrementStackPointer(asmLines)
            # set return address
            asmLines.append("@" + fnName + ".return")
            asmLines.append("D=A")
            asmLines.append("@SP")
            asmLines.append("A=M")
            asmLines.append("M=D")
            self.incrementStackPointer(asmLines)
            # set previous LCL on stack
            self.setupSymbolInSavedFrame(asmLines, "@LCL")
            # set previous ARG
            self.setupSymbolInSavedFrame(asmLines, "@ARG")
            # set previous THIS
            self.setupSymbolInSavedFrame(asmLines, "@THIS")
            # set previous THAT
            self.setupSymbolInSavedFrame(asmLines, "@THAT")
            # set @ARG symbol from previously calculated arg[0] location
            asmLines.append("@R13")
            asmLines.append("D=M")
            asmLines.append("@ARG")
            asmLines.append("M=D")
            # goto the called function
            asmLines.append("@" + fnName)
            asmLines.append("0;JMP")
            # setup the return location
            asmLines.append("(" + fnName + ".return)")
        elif fnCommand == "return":
            # Return uses R13 for the return value and R14 for the target return address
            #store return value in a register
            self.popStack(asmLines)
            asmLines.append("@R13")
            asmLines.append("M=D")
            # store the ARG address for the return value later before we reassign it back
            asmLines.append("//STORE ARG ADDRESS FOR RETURN LOCATION")
            asmLines.append("@ARG")
            asmLines.append("D=M")
            asmLines.append("@retvalLocation")
            asmLines.append("M=D")
            #rewind local variables used
            asmLines.append("//REWIND LOCAL VARIABLES")
            for param in range(self.currentFnParamCount):
                self.popStack(asmLines)
            #reassign THAT
            asmLines.append("//REASSIGN THAT, THIS, ARG, LCL, RETURN ADDRESS (respectively)")
            self.popStack(asmLines)
            asmLines.append("@THAT")
            asmLines.append("M=D")
            #reassign THIS
            self.popStack(asmLines)
            asmLines.append("@THIS")
            asmLines.append("M=D")
            #reassign ARG
            self.popStack(asmLines)
            asmLines.append("@ARG")
            asmLines.append("M=D")
            #reassign LCL
            self.popStack(asmLines)
            asmLines.append("@LCL")
            asmLines.append("M=D")
            #store return address in a register
            self.popStack(asmLines)
            asmLines.append("@R14")
            asmLines.append("M=D")
            # rewind arguments used for stack pointer
            asmLines.append("//REWIND ARGUMENTS")
            asmLines.append("@retvalLocation")
            asmLines.append("D=M")
            asmLines.append("@SP")
            asmLines.append("M=D")
            # place result on callback for stack pointer
            asmLines.append("@R13")
            asmLines.append("D=M")
            asmLines.append("@SP")
            asmLines.append("A=M")
            asmLines.append("M=D")
            self.incrementStackPointer(asmLines)
            # go back to return address
            asmLines.append("@R14")
            asmLines.append("A=M")
            asmLines.append("0;JMP")
