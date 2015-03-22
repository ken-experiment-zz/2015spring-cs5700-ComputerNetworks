import sys
import os
import csv

# python /Users/Ken/Dropbox/fcn/project_3/computation2.py ex2_result 10

def eachFile(filename, iteration) :
    #print filename
    dropPacket1 = 0
    receivedPacket1 = 0
    dropRate1 = 0
    totalLatency1 = 0
    latency1 = {}

    dropPacket2 = 0
    receivedPacket2 = 0
    dropRate2 = 0
    totalLatency2 = 0
    latency2 = {}

    with open(filename, 'r') as f:
        for line in f :
            arguments = line.split()
            
            if arguments[4] == "tcp" :
                #protocol 1
                if arguments[7] == '1' :
                    dropPacket1 += (arguments[0] == 'd')

                    if arguments[11] not in latency1 :
                        latency1[arguments[11]] = arguments[1]
                    elif (arguments[0] == "r" and arguments[3] == '3') : 
                        receivedPacket1 += 1
                        totalLatency1 += float(arguments[1]) - float(latency1[arguments[11]])
                                                    
                #protocol 2
                if arguments[7] == '2' :
                    dropPacket2 += (arguments[0] == 'd')

                    if arguments[11] not in latency2 :
                        latency2[arguments[11]] = arguments[1]
                    elif (arguments[0] == "r" and arguments[3] == '5') : 
                        receivedPacket2 += 1
                        totalLatency2 += float(arguments[1]) - float(latency2[arguments[11]])

        dropRate1 = float(dropPacket1) / (dropPacket1 + receivedPacket1)
        throughput1 = float(receivedPacket1) * 8 * 1000 / 10 / 1000000
        averageLatency1 = totalLatency1 / receivedPacket1
        #print "receivedPacket1", receivedPacket1
        #print "dropRate1", dropRate1
        #print "throughput1", throughput1
        #print "averageLatency1", averageLatency1

        dropRate2 = float(dropPacket2) / (dropPacket2 + receivedPacket2)
        throughput2 = float(receivedPacket2) * 8 * 1000 / 10 / 1000000
        averageLatency2 = totalLatency2 / receivedPacket2
        #print "receivedPacket2", receivedPacket2
        #print "dropRate2", dropRate2
        #print "throughput2", throughput2
        #print "averageLatency2", averageLatency2

    newPath = filename.split('/')
    info = newPath[len(newPath)-1]
    newPath = '/'.join(newPath[:len(newPath)-1])

    with open(newPath + '/statistics2.csv' , 'a') as csvfile :
        writer = csv.writer(csvfile, dialect = 'excel')
        s = []
        s.append(iteration)
        s.append(info)
        s.append(str(dropRate1))
        s.append(str(dropRate2))
        s.append(str(throughput1))
        s.append(str(throughput2))
        s.append(str(averageLatency1))
        s.append(str(averageLatency2))

        writer.writerow(s)



def main() :
    path = sys.argv[1]
    iteration = sys.argv[2]

    filePath = os.path.abspath('.')
    #filePath += '/Dropbox/FCN/project_3'
    #filePath += '/' + path + '/'

    print "iteration: ", iteration

    #with open(filePath + 'statistics2_thoughput.csv' , 'a') as csvfile :

    filename = ['Reno_Reno', 'NewReno_Reno', 'Vegas_Vegas', 'NewReno_Vegas']
    for each in filename :
        for i in range(1, 11) :
            eachFile(filePath + '/' + each + '_' + str(i) + '.tr', iteration)

if __name__ == '__main__' :
    main()
