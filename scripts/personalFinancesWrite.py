import os

'''
################################################################################
#                               Write the Stuff                                #
################################################################################
'''

def writeDataToFile(filename,data,catagories,types,subtypes):

    path = os.path.dirname(__file__)

    readFile = open(path + '\\' + filename, 'r')
    oldCatagories = readFile.readline().strip().split("\t")
    readFile.close()

    if len(data) == len(catagories) == len(types) == len(subtypes):
        if len(catagories) < len(oldCatagories):
            print('Insufficient data...')
        elif len(catagories) == len(oldCatagories):
            writeStr = ''.join([x + '\t' for x in data])
            writeFile = open(path + '\\' + filename, 'a')
            writeFile.write(writeStr.replace('none', '') + '\n')
            writeFile.close()
            print('Data added!')
        else: # len(catagories) > len(oldCatagories):
            print('Adding a new catagory...')
            myFile = open(path + '\\' + filename,'r')
            catLine = myFile.readline()
            typLine = myFile.readline()
            subLine = myFile.readline()
            newCatLine = ''.join([x + '\t' for x in catagories])
            newTypLine = ''.join([x + '\t' for x in types])
            newSubLine = ''.join([x + '\t' for x in subtypes])
            rest = ''.join(myFile.readlines())
            myFile.close()
            myFile = open(path + '\\' + filename, 'w')
            myFile.write(newCatLine + '\n' + newTypLine + '\n' + newSubLine + '\n' + rest)
            myFile.close()
            writeStr = ''.join([x + '\t' for x in data])
            writeFile = open(path + '\\' + filename, 'a')
            writeFile.write(writeStr.replace('none', '') + '\n')
            writeFile.close()
            print('Data added!')
    else:
        print('Insufficient data...')
