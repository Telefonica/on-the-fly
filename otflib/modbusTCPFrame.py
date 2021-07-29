from scapy.all import *

class modbusTCPFrame():
    #Functions dictionary
    functions = {
        0 : { "name":    "readCoils",                        "code" : "01" },
        1 : { "name":    "readDiscreteInputs",               "code" : "02" },
        2 : { "name":    "readMultipleHoldingRegister",      "code" : "03" },
        3 : { "name":    "readInputRegisters",               "code" : "04" },
        4 : { "name":    "writeSingleCoil",                  "code" : "05" },
        5 : { "name":    "writeSingleHoldingRegister",       "code" : "06" },
        6 : { "name":    "readExceptionStatus",              "code" : "07" },
        7 : { "name":    "diagnostic",                       "code" : "08" },
        8 : { "name":    "writeMultipleCoils",               "code" : "15" },
        9 : { "name":    "write1MultipleHoldingRegisters",   "code" : "16" },
        10 : { "name":    "reportSlaveID",                    "code" : "17" },
        11 : { "name":    "readFileRecord",                   "code" : "20" },
        12 : { "name":    "writeFileRecord",                  "code" : "21" },
        13 : { "name":    "maskWriteRegister",                "code" : "22" },
        14 : { "name":    "readWriteMultipleRegisters",       "code" : "23" },
        15 : { "name":    "readDeviceIdentification",         "code" : "43" }  
        }
    
    def __init__(self, packet, type):
        
        self.type = type
        self.packet = packet
        self.transactionId = None
        self.protocolId = None
        self.messageLength = None
        self.unitId = None
        self.functionCode = None
        self.dataAddressForTheFirstRegisterRequested = None
        self.numberOfRegistersRequested = None

    #DATA PROCESSING: Sets data values from the packet
    def processData(self ):
        data = hexdump(self.packet.lastlayer(),True)
        #print("Data:",data)
        datosList = data.split(" ")
        #print("String bytes:"+str(datosList))
        transactionId   =       str(datosList[2] + datosList[3])
        protocolId      =       str(datosList[4] + datosList[5])
        messageLength   =       str(datosList[6] + datosList[7])
        unitId          =       str(datosList[8])
        functionCode    =       str(datosList[9])
        dataAddressForTheFirstRegisterRequested = str(datosList[10] + datosList[11]) 
        numberOfRegistersRequested = ""
        
        if(self.type == "Request"):
            numberOfRegistersRequested              = str(datosList[12] + datosList[13])
        else:
            #Response packets have different data structure
            for i in range(12,len(datosList)-1):
                numberOfRegistersRequested              += str(datosList[i])
        
        modbusTCPFrame.setTransactionId(self,transactionId)
        modbusTCPFrame.setProtocolId(self, protocolId)
        modbusTCPFrame.setmessageLength(self, messageLength)
        modbusTCPFrame.setUnitId(self, unitId)
        modbusTCPFrame.setFunctionCode(self, functionCode)
        modbusTCPFrame.setDataAddressForTheFirstRegisterRequested(self, dataAddressForTheFirstRegisterRequested)
        modbusTCPFrame.setNumberOfRegistersRequested(self, numberOfRegistersRequested)
    
    def hexToDec(self,value):
        try:
            decimal = int(value,16)
            return str(decimal)
        except:
            if(str(value) != "Empty data"):
                return str("HEX: "+value)
            else: 
                return value
    
    #Verifies if the function code that is in the packet exists
    def verifyFunctionCode( self,value ):

        for i in modbusTCPFrame.functions:

            if( value ==  modbusTCPFrame.functions[i]['code']):
                return True    

        return False
    
    #DATA PRINTING                     
    def showDataBytes(self):
        print( "\tData bytes:\t" + str(self.packet[TCP].payload) )
    
    def showDataHEX(self):

            print("\nHEX Values:\n")
            print("\tTransaction ID:\t" + modbusTCPFrame.getTransactionId(self) )
            print("\tProtocol ID:\t" + modbusTCPFrame.getProtocolId(self) )
            print("\tMessageLength:\t" +  modbusTCPFrame.getMessageLength(self) )
            print("\tFunction Code:\t" + modbusTCPFrame.getFunctionCode(self) )
            print("\tData address for the first register requested:\t" + modbusTCPFrame.getDataAddressForTheFirstRegisterRequested(self) )
            print("\tNumber of registers requested:\t" + modbusTCPFrame.getNumberOfRegistersRequested(self) )
        
    def showDataDecimal(self):

        print("\nDECIMAL Values:\n")
        print("\tTransaction ID:\t" + modbusTCPFrame.hexToDec(self,modbusTCPFrame.getTransactionId(self)) )
        print("\tProtocol ID:\t" + modbusTCPFrame.hexToDec(self,modbusTCPFrame.getProtocolId(self)) )
        print("\tMessageLength:\t" + modbusTCPFrame.hexToDec(self,modbusTCPFrame.getMessageLength(self))  )
        functionCodeDecimal = modbusTCPFrame.hexToDec(self,modbusTCPFrame.getFunctionCode(self)) 
        functionCodeString = modbusTCPFrame.getFunctionCodeString(self,functionCodeDecimal)
        print("\tFunction Code:\t" + functionCodeDecimal)
        print("\tFunction:\t" + functionCodeString )
        print("\tData address for the first register requested:\t" + modbusTCPFrame.hexToDec(self,modbusTCPFrame.getDataAddressForTheFirstRegisterRequested(self)) )
        print("\tNumber of registers requested:\t" + modbusTCPFrame. hexToDec(self,modbusTCPFrame.getNumberOfRegistersRequested(self)) )

    #SETTERS
    def setTransactionId(self,value):

       self.transactionId = value
        
    def setProtocolId(self,value):

        self.protocolId = value
        
    def setmessageLength(self,value):

        self.messageLength = value
        
    def setUnitId(self,value):

        self.unitId = value
        
    def setFunctionCode(self,value):
        #hex to decimal
        decimal = int(value,16)
        if(decimal < 10):
            code = "0"+str(decimal)
        else:
            code = str(decimal)  

        if( modbusTCPFrame.verifyFunctionCode(self,code) ):
            self.functionCode = value
        
    def setDataAddressForTheFirstRegisterRequested(self,value):

        self.dataAddressForTheFirstRegisterRequested = value

    def setNumberOfRegistersRequested(self,value):
        #Filters
        value = value.replace(" ","")
        value = value.replace(".","")
        value = value.replace("\n","\t")
        #Checks if data is empty
        if( value == ""):
             self.numberOfRegistersRequested = "Empty data"
        else:
            self.numberOfRegistersRequested = value

    #GETTERS
    def getTransactionId(self):

        return self.transactionId

    def getProtocolId(self):

        return self.protocolId

    def getMessageLength(self):

        return self.messageLength

    def getUnitId(self):

        return self.unitId

    def getFunctionCode(self):

        return self.functionCode

    def getFunctionCodeString(self, functionCodeDecimal):
        
        decimal = int(functionCodeDecimal)

        if(decimal < 10):
            value = "0" + functionCodeDecimal

        else:
            value  = str(functionCodeDecimal)

        for key in modbusTCPFrame.functions:
            if( value ==  modbusTCPFrame.functions[key]['code']):
                return modbusTCPFrame.functions[key]['name']
           
        return "This function does not exist"
       
    def getDataAddressForTheFirstRegisterRequested(self):

        return self.dataAddressForTheFirstRegisterRequested 

    def getNumberOfRegistersRequested(self):

        return self.numberOfRegistersRequested
