import serial

import time 

import csv

import numpy as np

import datetime

import easygui

import serial.tools.list_ports

import os

import signal

from collections import defaultdict

TK_SILENCE_DEPRECATION=1



charDict = {173:'-',176:'0',49:'1',50:'2',179:'3',52:'4',181:'5',182:'6',55:'7',56:'8',185:'9',174:'.',32:'',2:''}

columns = defaultdict(list) # each value in each column is appended to a list

with open('information.csv') as f:
    reader = csv.DictReader(f) # read rows into a dictionary format
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        for (k,v) in row.items(): # go over each column name and value 
            columns[k].append(v) # append the value into the appropriate list
                                 # based on column name k

chunks = np.vstack((columns["Range"],columns["Graduation"],columns["Manufacturer"]))
secret = list(filter(lambda x:len(x)!=0,["".join(a) for a in list(zip(*chunks))]))


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







while len(combination) == 0:

    msg ="Which manufacturer?"

    mchoices = list(set(columns["Manufacturer"]))

    manufacturer=""

    while len(manufacturer) == 0:

        manufacturer= easygui.choicebox(msg, title, mchoices)






    msg ="Choose the range"

    choices1 = list(set(columns["Range"]))

    range1 = ""

    while len(range1) == 0:

        range1 = easygui.choicebox(msg, title, choices1)





    msg ="Choose the graduation"

    choices2 = list(set(columns["Graduation"]))

    graduation = ""

    while len(graduation) == 0:

        graduation = easygui.choicebox(msg, title, choices2)




    combination = range1+graduation+manufacturer


    if combination not in secret:

        print("Range: {}, Graduation: {}, Manufacturer: {}".format(range1,graduation,manufacturer))

        print("You have selected invalid combination of range and graduation, please try again")



    



print("You have chosen range: {} and graduation: {} from {}".format(range1,graduation,manufacturer))

rowNumber = secret.index(combination)



print("\nPress CTRL+c for more options\n")

nominal = []

with open('information.csv') as fd:
    reader=csv.reader(fd)
    nominal=list(filter(lambda x: x!="",[row for idx, row in enumerate(reader) if idx == (rowNumber+1)][0][3:]))



length = 0

if len(nominal) >0 :

    length =  len(nominal)-1



forwardCounter = 0

backwardCounter = length

nominalList = nominal

print(nominalList)

numericalGraduation = float(graduation.split()[0])



start = time.time()


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

            print("Total time taken for measurement is {0:0.1f} minutes".format((time.time() - start)/60.0))

            exit(0)

        except:

                

            print("forward data:")

            print(fData)



            print("\n backward data")

            print(list(reversed(bData)))



            # print("Something wrong, fail to save data")

            print("Total time taken for measurement is {0:0.1f} minutes".format((time.time() - start)/60.0))

            exit(0)



    elif len(fData) == len(bData) and len(fData) != length+1 or len(bData) != length+1:

      

        print("The number of measured values are different from the number of nominal values")

        print("nominal values: \n {}\n".format(nominalList))

        print("forward values:\n{}\n".format(fData))

        print("backward values:\n{}\n".format(list(reversed(bData))))



        cmsg = "There are a total of "+str(length+1)+" nominal values but you have only measured "+str(len(fData))+" forward measurement and "+str(len(bData))+" backward measurement,therefore no data will be saved, are you sure you want to exit?"

        title = "Please Confirm"

        if easygui.ccbox(cmsg, title):     # show a Continue/Cancel dialog
            print("Total time taken for measurement is {0:0.1f} minutes".format((time.time() - start)/60.0))
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
            print("Total time taken for measurement is {0:0.1f} minutes".format((time.time() - start)/60.0))
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

