import sys
import os
import csv

# python /Users/Ken/Dropbox/fcn/project_3/computation.py /ex1_result Tahoe 1 10

def main() :
    path = sys.argv[1]
    protocol = sys.argv[2]
    cbrRate = sys.argv[3]
    iteration = sys.argv[4]

    #filePath = sys.argv[0].split('/')
    #filePath = '/'.join(filePath[0:len(filePath)-1])
    filePath = os.path.abspath('.')
    filePath += '/' + path + '/'

    print filePath

    dropPacket = 0
    receivedPacket = 0
    dropRate = 0
    totalLatency = 0
    with open(filePath + protocol + '_' + cbrRate + '.tr', 'r') as f :
        latency = {}
        for line in f :
            arguments = line.split()

            if (arguments[4]== "tcp") :
                dropPacket += (arguments[0] == 'd')

                if arguments[11] not in latency :
                    latency[arguments[11]] = arguments[1]
                elif (arguments[0] == "r" and arguments[3] == '3') : 
                    receivedPacket += 1
                    totalLatency += float(arguments[1]) - float(latency[arguments[11]])
                                                     
        dropRate = float(dropPacket) / (dropPacket + receivedPacket)
        throughput = float(receivedPacket) * 8 * 1000 / 10 / 1000000
        averageLatency = totalLatency / receivedPacket
        #print "receivedPacket", receivedPacket
        #print "dropRate", dropRate
        #print "throughput", throughput
        #print "averageLatency", averageLatency

    with open(filePath + 'statistics1.csv' , 'a') as csvfile :
        writer = csv.writer(csvfile, dialect = 'excel')
        s = []
        s.append(iteration)
        s.append(protocol)
        s.append(cbrRate)
        s.append(str(dropRate))
        s.append(str(throughput))
        s.append(str(averageLatency))

        writer.writerow(s)

if __name__ == '__main__' :
    main()
