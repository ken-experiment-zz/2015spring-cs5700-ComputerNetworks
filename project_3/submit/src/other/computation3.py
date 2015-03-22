import sys
import os
import csv

# python /Users/Ken/Dropbox/fcn/project_3/computation.py ex3_result/DropTail_Reno.tr iter

def main() :
    path = sys.argv[1]
    iteration = sys.argv[2]

    filePath = os.path.abspath('.')
    filePath += '/Dropbox/FCN/project_3'
    filePath += '/'

    print filePath

    interval = 1
    dropPacket = 0
    receivedPacket = 0
    dropRate = 0
    totalLatency = 0
    latency = {}
    timeline = {}

    with open(filePath + path, 'r') as f :
        for line in f :
            arguments = line.split()

            if float(arguments[1]) >= interval * 0.5 :
                dropRate = float(dropPacket) / (dropPacket + receivedPacket)
                throughput = float(receivedPacket) * 8 * 1000 / 10 / 1000000
                averageLatency = totalLatency / receivedPacket
                
                timeline[interval * 0.5] = [dropRate, throughput, averageLatency]
                #print "interval", interval
                #print "receivedPacket", receivedPacket
                #print "dropRate", dropRate
                #print "throughput", throughput
                #print "averageLatency", averageLatency
                #print "----------------------------------"

                interval += 1
                dropPacket = 0
                receivedPacket = 0
                dropRate = 0
                totalLatency = 0
                latency = {}

            if (arguments[4]== "tcp") :
                dropPacket += (arguments[0] == 'd')

                if arguments[11] not in latency :
                    latency[arguments[11]] = arguments[1]
                elif (arguments[0] == "r" and arguments[3] == '3') : 
                    receivedPacket += 1
                    totalLatency += float(arguments[1]) - float(latency[arguments[11]])

    filePath += 'ex3_result/'
    with open(filePath + 's3_droprate.csv', 'a') as d, open(filePath + 's3_throughput.csv', 'a') as t, open(filePath + 's3_latency.csv', 'a') as l:

        dr = [path, iteration]
        th = [path, iteration]
        la = [path, iteration]

        for each in sorted(timeline) :
            #print each, timeline[each]
            dr.append(timeline[each][0])
            th.append(timeline[each][1])
            la.append(timeline[each][2])

        #print dr
        #print th
        #print la

        de = csv.writer(d, dialect = 'excel')
        te = csv.writer(t, dialect = 'excel')
        le = csv.writer(l, dialect = 'excel')

        de.writerow(dr)
        te.writerow(th)
        le.writerow(la)
#
if __name__ == '__main__' :
    main()
