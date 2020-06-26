import serial
import time 
import csv
import numpy as np
import datetime
import easygui
import serial.tools.list_ports
import os
import signal
TK_SILENCE_DEPRECATION=1

charDict = {173:'-',176:'0',49:'1',50:'2',179:'3',52:'4',181:'5',182:'6',55:'7',56:'8',185:'9',174:'.',32:'',2:''}

fData = []
bData = []
combination = ""
mode = 'f'
formats = ["xls","csv"]
ports = serial.tools.list_ports.comports(include_links=False)
msg = "Enter filename (e.g data1.csv)"
title = " Logger"
fieldNames = []
fieldValues = []  # we start with blanks for the values
while not fieldValues:
    fieldValues = easygui.enterbox(msg,title, fieldNames)

if fieldValues.split(".")[-1] not in formats:
    fieldValues =  fieldValues+".csv"

msg ="Which port are you using?"
choices = [port.device for port in ports]
port = ""
while len(port) == 0:
    port = easygui.choicebox(msg, title, choices)

ser = serial.Serial(
    port=port,\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)


nominal = {'6-3-BS':[-0.02000,-0.01900,-0.01800,-0.01700,-0.01500,-0.01000,-0.00900,-0.00800,-0.00700,-0.00600,-0.00500,0.00000,0.00100,0.00200,0.00300,0.00500,0.01000,0.01100,0.01200,0.01300,0.01400,0.01500,0.02000],
'5-3-BS':[-0.01500,-0.01400,-0.01300,-0.01200,-0.01000,-0.00500,0.00000,0.00100,0.00200,0.00300,0.00500,0.01000,0.01500],
'1-1-BS':[-0.004000,-0.003900,-0.003800,-0.003700,-0.003500,-0.003000,-0.002500,-0.002000,-0.001900,-0.001800,-0.001700,-0.001500,-0.001000,-0.000500,0.000000,0.000100,0.000200,0.000300,0.000500,0.001000,0.001500,0.002000,0.002100,0.002200,0.002300,0.002500,0.003000,0.003500,0.004000],
'2-1-BS':[-0.005000,-0.004900,-0.004800,-0.004700,-0.004500,-0.004000,-0.003500,-0.002500,-0.002400,-0.002300,-0.002200,-0.002000,-0.001500,-0.001000,0.000000,0.000100,0.000200,0.000300,0.000500,0.001000,0.001500,0.002500,0.002600,0.002700,0.002800,0.003000,0.003500,0.004000,0.005000],
'3-1-BS':[-0.008000,-0.007900,-0.007800,-0.007700,-0.007500,-0.007000,-0.006500,-0.004000,-0.003900,-0.003800,-0.003700,-0.003500,-0.003000,-0.002500,0.000000,0.000100,0.000200,0.000300,0.000500,0.001000,0.001500,0.004000,0.004100,0.004200,0.004300,0.004500,0.005000,0.005500,0.008000],
'5-2-BS':[-0.01500,-0.01450,-0.01400,-0.01350,-0.01250,-0.01000,-0.00750,-0.00700,-0.00650,-0.00600,-0.00550,-0.00500,-0.00250,0.00000,0.00050,0.00100,0.00150,0.00250,0.00500,0.00750,0.00800,0.00850,0.00900,0.00950,0.01000,0.01250,0.01500],
'7-2-BS':[-0.03000,-0.02950,-0.02900,-0.02850,-0.02750,-0.02500,-0.02250,-0.01500,-0.01450,-0.01400,-0.01350,-0.01250,-0.01000,-0.00750,0.00000,0.00050,0.00100,0.00150,0.00250,0.00500,0.00750,0.01500,0.01550,0.01600,0.01650,0.01750,0.02000,0.02250,0.03000],
'4-2-BS':[-0.01000,-0.00950,-0.00900,-0.00850,-0.00750,-0.00500,-0.00450,-0.00400,-0.00350,-0.00300,-0.00250,0.00000,0.00050,0.00100,0.00150,0.00250,0.00500,0.00550,0.00600,0.00650,0.00700,0.00750,0.01000],
'12-6-BS':[-0.4000,-0.3900,-0.3800,-0.3700,-0.3500,-0.3000,-0.2500,-0.2000,-0.1900,-0.1800,-0.1700,-0.1500,-0.1000,-0.0500,0.0000,0.0100,0.0200,0.0300,0.0500,0.1000,0.1500,0.2000,0.2100,0.2200,0.2300,0.2500,0.3000,0.3500,0.4000],
'13-6-BS':[-0.2500,-0.2400,-0.2300,-0.2200,-0.2000,-0.1500,-0.1400,-0.1300,-0.1200,-0.1100,-0.1000,-0.0500,0.0000,0.0100,0.0200,0.0300,0.0500,0.1000,0.1100,0.1200,0.1300,0.1400,0.1500,0.2000,0.2500],
'15-6-BS':[-0.5000,-0.4900,-0.4800,-0.4700,-0.4500,-0.4000,-0.3500,-0.2500,-0.2400,-0.2300,-0.2200,-0.2000,-0.1500,-0.1000,0.0000,0.0100,0.0200,0.0300,0.0500,0.1000,0.1500,0.2500,0.2600,0.2700,0.2800,0.3000,0.3500,0.4000,0.5000],
'17-6-BS':[-0.8000,-0.7900,-0.7800,-0.7700,-0.7500-0.7000,-0.6500,-0.4000,-0.3900,-0.3800,-0.3700,-0.3500,-0.3000,-0.2500,0.0000,0.0100,0.0200,0.0300,0.0500,0.1000,0.1500,0.4000,0.4100,0.4200,0.4300,0.4500,0.5000,0.5500,0.8000],
'16-6-BS':[-0.7500,-0.7400,-0.7300,-0.7200,-0.7000,-0.6500,-0.6000,-0.3700,-0.3600,-0.3500,-0.3400,-0.3000,-0.2500,-0.2000,0.0000,0.0100,0.0200,0.0300,0.0500,0.1000,0.1500,0.3800,0.3900,0.4000,0.4100,0.4500,0.5000,0.5500,0.7500],
'14-5-BS':[-0.3000,-0.2980,-0.2960,-0.2940,-0.2920,-0.2900,-0.2880,-0.2860,-0.2840,-0.2820,-0.2800,-0.2600,-0.2400,-0.2200,-0.2000,-0.1800,-0.1600,-0.1400,-0.1200,-0.1000,-0.0800,-0.0600,-0.0400,-0.0200,0.0000,0.0200,0.0400,0.0600,0.0800,0.1000,0.1200,0.1400,0.1600,0.1800,0.2000,0.2200,0.2400,0.2600,0.2800,0.3000],
'9-5-BS':[-0.1000,-0.0980,-0.0960,-0.0940,-0.0900,-0.0800,-0.0700,-0.0500,-0.0480,-0.0460,-0.0440,-0.0400,-0.0300,-0.0200,0.0000,0.0020,0.0040,0.0060,0.0100,0.0200,0.0300,0.0500,0.0520,0.0540,0.0560,0.0600,0.0700,0.0800,0.1000],
'10-5-BS':[-0.1400,-0.1380,-0.1360,-0.1340,-0.1300,-0.1200,-0.1100,-0.0700,-0.0680,-0.0660,-0.0640,-0.0600,-0.0500,-0.0400,0.0000,0.0020,0.0040,0.0060,0.0100,0.0200,0.0300,0.0700,0.0720,0.0740,0.0760,0.0800,0.0900,0.1000,0.1400],
'12-6-JIS':[-0.4000,-0.3900,-0.3800,-0.3700,-0.3600,-0.3500,-0.3400,-0.3300,-0.3200,-0.3100,-0.3000,-0.2000,-0.1000,0.0000,0.1000,0.2000,0.3000,0.4000],
'9-5-JIS':[-0.1000,-0.0980,-0.0960,-0.0940,-0.0920,-0.0900,-0.0880,-0.0860,-0.0840,-0.0820,-0.0800,-0.0600,-0.0400,-0.0200,0.0000,0.0200,0.0400,0.0600,0.0800,0.1000],
'11-5-MAHR':[-0.2000,-0.1980,-0.1960,-0.1940,-0.1920,-0.1900,-0.1880,-0.1860,-0.1840,-0.1820,-0.1800,-0.1600,-0.1400,-0.1200,-0.1000,-0.0800,-0.0600,-0.0400,-0.0200,0.0000,0.0200,0.0400,0.0600,0.0800,0.1000,0.1200,0.1400,0.1600,0.1800,0.2000],
'8-4-MANU':[-0.0700,-0.0690,-0.0680,-0.0670,-0.0660,-0.0650,-0.0640,-0.0630,-0.0620,-0.0610,-0.0600,-0.0500,-0.0400,-0.0300,-0.0200,-0.0100,0.0000,0.0100,0.0200,0.0300,0.0400,0.0500,0.0600,0.0700],
'1-1-MITU':[-0.004000,-0.003900,-0.003800,-0.003700,-0.003500,-0.003000,-0.002500,-0.002000,-0.001900,-0.001800,-0.001700,-0.001500,-0.001000,-0.000500,0.000000,0.000100,0.000200,0.000300,0.000500,0.001000,0.001500,0.002000,0.002100,0.002200,0.002300,0.002500,0.003000,0.003500,0.004000],
'5-2-MITU':[-0.01500,-0.01450,-0.01400,-0.01350,-0.01300,-0.01250,-0.01200,-0.01150,-0.01100,-0.01050,-0.01000,-0.00750,-0.00500,-0.00250,0.00000,0.00250,0.00500,0.00750,0.01000,0.01250,0.01500],
'12-6-MITU':[-0.4000,-0.3900,-0.3800,-0.3700,-0.3600,-0.3500,-0.3400,-0.3300,-0.3200,-0.3100,-0.3000,-0.2500,-0.2000,-0.1500,-0.1000,-0.0500,0.0000,0.0500,0.1000,0.1500,0.2000,0.2500,0.3000,0.3500,0.4000],
'9-5-MITU':[-0.1000,-0.0980,-0.0960,-0.0940,-0.0920,-0.0900,-0.0880,-0.0860,-0.0840,-0.0820,-0.0800,-0.0600,-0.0400,-0.0200,0.0000,0.0200,0.0400,0.0600,0.0800,0.1000],
'1-1-TESA':[-0.004000,-0.003900,-0.003800,-0.003700,-0.003500,-0.003000,-0.002500,-0.002000,-0.001900,-0.001800,-0.001700,-0.001500,-0.001000,-0.000500,0.000000,0.000100,0.000200,0.000300,0.000500,0.001000,0.001500,0.002000,0.002100,0.002200,0.002300,0.002500,0.003000,0.003500,0.004000],
'12-6-TESA':[-0.4000,-0.3900,-0.3800,-0.3700,-0.3500,-0.3000,-0.2500,-0.2000,-0.1900,-0.1800,-0.1700,-0.1500,-0.1000,-0.0500,0.0000,0.0100,0.0200,0.0300,0.0500,0.1000,0.1500,0.2000,0.2100,0.2200,0.2300,0.2500,0.3000,0.3500,0.4000],
'9-5-TESA':[-0.1000,-0.0980,-0.0960,-0.0940,-0.0900,-0.0800,-0.0700,-0.0500,-0.0480,-0.0460,-0.0440,-0.0400,-0.0300,-0.0200,0.0000,0.0020,0.0040,0.0060,0.0100,0.0200,0.0300,0.0500,0.0520,0.0540,0.0560,0.0600,0.0700,0.0800,0.1000]
}

while combination == 0 or combination not in nominal:
    msg ="Which manufacturer?"
    mchoices = ['BS','JIS','MAHR','MANUSPEC','MITUTOYO','TESA']
    manufacturer=""
    while len(manufacturer) == 0:
        manufacturer= easygui.choicebox(msg, title, mchoices)

    if len(manufacturer) > 4:
        manufacturer = manufacturer[:4]



    msg ="Choose the range"
    choices1 = ['0.008 inches','0.01 inches','0.016 inches','0.02 inches','0.03 inches','0.04 inches','0.06 inches','0.14 mm','0.2 mm','0.28 mm','0.4 mm','0.8 mm','0.5 mm','0.6 mm','1 mm','1.5 mm', '1.6 mm']
    range1 = ""
    while len(range1) == 0:
        range1 = easygui.choicebox(msg, title, choices1)


    msg ="Choose the graduation"
    choices2 = ['0.0001 inches','0.0005 inches','0.001 inches','0.001 mm','0.002 mm','0.01 mm','0.2 mm']
    graduation = ""
    while len(graduation) == 0:
        graduation = easygui.choicebox(msg, title, choices2)




    combination = str(choices1.index(range1)+1)+"-"+str(choices2.index(graduation)+1)+"-"+manufacturer

    if combination not in nominal:
        print(combination)
        print("You have selected invalid combination of range and graduation, please try again")

    

print("You have chosen range: {} and graduation: {}".format(range1,graduation))


print("\nPress CTRL+c for more options\n")

if combination in nominal:
    length =  len(nominal[combination])-1

forwardCounter = 0
backwardCounter = length
nominalList = nominal[combination]
numericalGraduation = float(graduation.split()[0])


def toggle():
    global mode
    
    if mode == 'f' and forwardCounter<=length:
        print("\nMeasuring forward")
        print("nominal value: {}".format(str(nominalList[forwardCounter])))
    elif mode == 'b' and backwardCounter>=0:
        print("\nMeasuring backward")
        print("nominal value: {}".format(str(nominalList[backwardCounter])))

    elif  mode == 'f' and forwardCounter>length and backwardCounter>=0:
        cmsg = "You have finish all the values in forward direction, do you want to proceed to backward direction?"
        title = "Please Confirm"
        if easygui.ccbox(cmsg, title):     # show a Continue/Cancel dialog
            mode = "b"
            print("\nMeasuring backward")
            print("nominal value: {}".format(str(nominalList[backwardCounter])))
        else:  # user chose Cancel
            pass
    elif  mode == 'b' and forwardCounter<=length and backwardCounter<0:
        cmsg = "You have finish all the values in backward direction, do you want to proceed to forward direction?"
        title = "Please Confirm"
        if easygui.ccbox(cmsg, title):     # show a Continue/Cancel dialog
            mode = "f"
            print("\nMeasuring forward")
            print("nominal value: {}".format(str(nominalList[forwardCounter])))
        else:  # user chose Cancel
            pass
    elif len(fData) == length+1 and len(bData) == length+1:
        print("here6")
        #all values done
        cmsg = "You have finish all values, press continue to save and quit "
        title = "Please Confirm"
        if easygui.ccbox(cmsg, title):     # show a Continue/Cancel dialog
            quit()
        else:  # user chose Cancel
            pass


def quit():
    flag = False
        
    if len(fData) == len(bData) and len(fData) == length+1 and len(bData) == length+1:
        try:
            if not os.path.exists("./data/"+fieldValues):
                flag = True


            # with open("./data/"+fieldValues, mode='a',newline='') as data:
            with open("./data/"+fieldValues, mode='a',newline='') as data:
                data_writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                if flag:
                    data_writer.writerow(["range: ",range1,"graduation: ",graduation])
                    data_writer.writerow([])

                    data_writer.writerow(["nominal","Forward","Backward"])
                    flag = False

                bData.reverse()
                for n,x,y in zip(nominalList,fData,bData):
                    data_writer.writerow([n,x,y])

            exit(0)
        except:
                
            print("forward data:")
            print(fData)

            print("\n backward data")
            print(list(reversed(bData)))

            # print("Something wrong, fail to save data")

            exit(0)

    elif len(fData) == len(bData) and len(fData) != length+1 or len(bData) != length+1:
      
        print("The number of measured values are different from the number of nominal values")
        print("nominal values: \n {}\n".format(nominalList))
        print("forward values:\n{}\n".format(fData))
        print("backward values:\n{}\n".format(list(reversed(bData))))

        cmsg = "There are a total of "+str(length+1)+" nominal values but you have only measured "+str(len(fData))+" forward measurement and "+str(len(bData))+" backward measurement,therefore no data will be saved, are you sure you want to exit?"
        title = "Please Confirm"
        if easygui.ccbox(cmsg, title):     # show a Continue/Cancel dialog
            exit(0)
        else:  # user chose Cancel
            if mode == 'f':
                print("Measuring forward\n")
                print("nominal value: {}".format(str(nominalList[forwardCounter])))
            else:
                print("Measuring backward\n")
                print("nominal value: {}".format(str(nominalList[backwardCounter])))

    else:
        print("The number of measured values are different from the number of nominal values")
        print("nominal values: \n {}\n".format(nominalList))
        print("forward values:\n{}\n".format(fData))
        print("backward values:\n{}\n".format(reversed(bData)))

        cmsg = "The number of measured values are different from the number of nominal values, no data will be saved, are you sure you want to exit?"
        title = "Please Confirm"
        if easygui.ccbox(cmsg, title):     # show a Continue/Cancel dialog
            exit(0)
        else:  # user chose Cancel
            if mode == 'f':
                print("Measuring forward\n")
                print("nominal value: {}".format(str(nominalList[forwardCounter])))
            else:
                print("Measuring backward\n")
                print("nominal value: {}".format(str(nominalList[backwardCounter])))




def optionMenu():
    global mode
    global fData
    global bData
    
    print("\n")
    phrase = ""
    if mode == 'f':
        phrase = "\'Forward\'"
    else:
        phrase = "\'Backward\'"
    msg = "What do you want? you are currently measuring "+ phrase
    choices = ["Forward","Backward","Quit callibration"]
    reply = easygui.buttonbox(msg,choices=choices)

    if reply == "Forward":
        mode = 'f'
        # print("Measuring forward\n")
        # print("nominal value: {}".format(str(nominalList[forwardCounter])))

    elif reply =="Backward":
        mode = 'b'
        # print("Measuring backward\n")
        # print("nominal value: {}".format(str(nominalList[backwardCounter])))

    else:
        quit()

    toggle()
        

   

def keyboardInterruptHandler(signal, frame):
    optionMenu()




signal.signal(signal.SIGINT, keyboardInterruptHandler)

toggle()

str1 = ""
while True:
    

    for c in ser.read():
        #print(str(c))
        if c == " ":
            str1 += "."
        if c != 138 and c in charDict:
            str1 += charDict[c]
        else:
            print(str1)     

    # str1 = input()
    # if len(str1)>0:

    #     if len(str1)>0:
            

            cval = float(str1)
            if mode == 'f' and forwardCounter<=length:
                
                if cval>nominalList[forwardCounter]-numericalGraduation and cval<nominalList[forwardCounter]+numericalGraduation:
                    fData.append(str1)
                    forwardCounter+=1
                else:
                    cmsg = "The nominal value is "+str(nominalList[forwardCounter])+" but your measured value is "+str(cval)+", do you want to proceed and keep the measure value?"
                    title = "Please Confirm"
                    if easygui.ccbox(cmsg, title):     # show a Continue/Cancel dialog
                        fData.append(str1)
                        forwardCounter+=1
                    else:  # user chose Cancel
                        pass

            elif  mode == 'b' and backwardCounter>=0: 

                cval = float(str1)
                if cval>nominalList[backwardCounter]-numericalGraduation and cval<nominalList[backwardCounter]+numericalGraduation:
                    bData.append(str1)
                    backwardCounter-=1
                else:
                    cmsg = "The nominal value is "+str(nominalList[backwardCounter])+" but your measured value is "+str(cval)+", do you want to proceed and keep the measured value?"
                    title = "Please Confirm"
                    if easygui.ccbox(cmsg, title):     # show a Continue/Cancel dialog
                        bData.append(str1)
                        backwardCounter-=1
                        
                    else:  # user chose Cancel
                        pass
            toggle()


            str1 = ""
  
            ser.flushInput()
            ser.flushOutput()
            # break            
    time.sleep(.005)

ser.close()
