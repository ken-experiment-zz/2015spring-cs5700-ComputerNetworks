import time

class Record:
    def __init__(self, seq, startTime):
        self.seq = seq
        self.startTime = startTime
        self.endTime = 0
        self.dropped = False

def seqInLines(seq, lines):
    for line in lines:
        if line.seq == seq:
            return True
    return False

def readFile(filename):
    f = open(filename, 'rt')
    lines = f.readlines()
    f.close()
    return lines

def calculateLatency(type, rate, qNum, send, recv, beginTime, timeLength, isQ3):
    # send = 1 in Q1
    # recv = 1 in Q1
    if isQ3:
        records = readFile("data/Q" + qNum + "/tcp-" + type + ".tr")
    else:
        records = readFile("data/Q" + qNum + "/rate=" + rate + "/tcp-" + type + ".tr")
    packetsNumber = 0
    totalLatency = 0
    lines = []
    for record in records:
        items = record.split(" ")
        event = items[0]
        time = float(items[1])
        fromNode = items[2]
        toNode = items[3]
        if time > time + timeLength:
            break
        if time >= beginTime:
            if len(items) == 12:
                seq = items[10]
            else:
                seq = items[6]
            if event == "-" and fromNode == str(send):
                if not seqInLines(seq, lines):
                    line = Record(seq, time)
                    lines.append(line)
            if event == "d":
                for line in lines:
                    if line.seq == seq:
                        line.dropped = True
            if event == "r" and toNode == str(recv):
                for line in lines:
                    if line.seq == seq and line.endTime == 0 and not line.dropped:
                        line.endTime = time
    for line in lines:
        if not line.endTime == 0:
            packetsNumber += 1
            totalLatency += (line.endTime - line.startTime)
    if packetsNumber == 0:
        return 0
    return totalLatency / packetsNumber

def calculateDropRate(type, rate, qNum, send, beginTime, timeLength, isQ3):
    # send = 1 in Q1
    # source = "0.0" in Q1
    if isQ3:
        records = readFile("data/Q" + qNum + "/tcp-" + type + ".tr")
    else:
        records = readFile("data/Q" + qNum + "/rate=" + rate + "/tcp-" + type + ".tr")
    sendNumber = 0
    dropNumber = 0
    for record in records:
        items = record.split(" ")
        event = items[0]
        fromNode = items[2]
        time = float(items[1])
        if time > beginTime + timeLength:
            break
        if time > beginTime:
            if event == "-" and fromNode == str(send):
                sendNumber += 1
            if event == "d":
                dropNumber += 1
    if sendNumber == 0:
        return 0
    dropRate = float(dropNumber) / sendNumber
    return dropRate

def calculateThroughput(type, rate, qNum, recv, beginTime, timeLength, isQ3):
    # recv = 4 in Q1
    if isQ3:
        records = readFile("data/Q" + qNum + "/tcp-" + type + ".tr")
    else:
        records = readFile("data/Q" + qNum + "/rate=" + rate + "/tcp-" + type + ".tr")
    sendNumber = 0
    lastTime = 0
    firstTime = 0
    for record in records:
        items = record.split(" ")
        event = items[0]
        time = float(items[1])
        toNode = items[3]
        if time > beginTime + timeLength:
            break
        if time > beginTime:
            if event == "-" and toNode == str(recv) and firstTime == 0:
                firstTime = time
            if event == "r" and toNode == str(recv):
                sendNumber += 1
                lastTime = time
    if sendNumber == 0:
        return 0
    throughput = sendNumber * 1040 * 8 / (lastTime - firstTime) / 1024000
    return throughput

def CalculateQ1():
    types = ["tahoe", "reno", "newreno", "vegas"]
    beginRate = 4
    endRate = 10
    question = 1
    beginTime = 0
    timeLength = 120
    for type in types:
        for rate in range (beginRate, (endRate + 1)):
            dropRateOutput = open("Results/Q" + str(question) + "/dropRate-" + type + ".csv", 'a')
            throughputOutput = open("Results/Q" + str(question) + "/throughput-" + type + ".csv", 'a')
            latencyOutput = open("Results/Q" + str(question) + "/latency-" + type + ".csv", 'a')
            dropRateOutput.write(str(rate) + ";" + str(calculateDropRate(type, str(rate), str(question), 1, beginTime, timeLength, False)) + "\n")
            throughputOutput.write(str(rate) + ";" + str(calculateThroughput(type, str(rate), str(question), 4, beginTime, timeLength, False)) + "\n")
            latencyOutput.write(str(rate) + ";" + str(calculateLatency(type, str(rate), str(question), 1, 1, beginTime, timeLength, False)) + "\n")
            dropRateOutput.close()
            throughputOutput.close()
            latencyOutput.close()

def CalculateQ2():
    typesFor1 = ["newreno-reno-1", "newreno-vegas-1", "reno-reno-1", "vegas-vegas-1"]
    typesFor2 = ["newreno-reno-2", "newreno-vegas-2", "reno-reno-2", "vegas-vegas-2"]
    beginRate = 1
    endRate = 10
    question = 2
    beginTime = 0
    timeLength = 120
    for type in typesFor1:
        for rate in range (beginRate, (endRate + 1)):
            dropRateOutput = open("Results/Q" + str(question) + "/dropRate-" + type + ".csv", 'a')
            throughputOutput = open("Results/Q" + str(question) + "/throughput-" + type + ".csv", 'a')
            latencyOutput = open("Results/Q" + str(question) + "/latency-" + type + ".csv", 'a')
            dropRateOutput.write(str(rate) + ";" + str(calculateDropRate(type, str(rate), str(question), 1, beginTime, timeLength, False)) + "\n")
            throughputOutput.write(str(rate) + ";" + str(calculateThroughput(type, str(rate), str(question), 4, beginTime, timeLength, False)) + "\n")
            latencyOutput.write(str(rate) + ";" + str(calculateLatency(type, str(rate), str(question), 1, 1, beginTime, timeLength, False)) + "\n")
            dropRateOutput.close()
            throughputOutput.close()
            latencyOutput.close()
    for type in typesFor2:
        for rate in range (beginRate, (endRate + 1)):
            dropRateOutput = open("Results/Q" + str(question) + "/dropRate-" + type + ".csv", 'a')
            throughputOutput = open("Results/Q" + str(question) + "/throughput-" + type + ".csv", 'a')
            latencyOutput = open("Results/Q" + str(question) + "/latency-" + type + ".csv", 'a')
            dropRateOutput.write(str(rate) + ";" + str(calculateDropRate(type, str(rate), str(question), 5, beginTime, timeLength, False)) + "\n")
            throughputOutput.write(str(rate) + ";" + str(calculateThroughput(type, str(rate), str(question), 6, beginTime, timeLength, False)) + "\n")
            latencyOutput.write(str(rate) + ";" + str(calculateLatency(type, str(rate), str(question), 5, 5, beginTime, timeLength, False)) + "\n")
            dropRateOutput.close()
            throughputOutput.close()
            latencyOutput.close()
            
def CalculateQ3():
    typesFor1 = ["reno-droptail-1", "reno-RED-1", "sack-droptail-1", "sack-RED-1"]
    typesFor2 = ["reno-droptail-2", "reno-RED-2", "sack-droptail-2", "sack-RED-2"]
    beginTime = 0
    timeSlot = 5
    endTime = 40
    question = 3
    for type in typesFor1:
        latencyOutput = open("Results/Q" + str(question) + "/latency-" + type + ".csv", 'a')
        latencyOutput.write("10" + ";" + str(calculateLatency(type, "1", str(question), 1, 1, 10, 30, True)) + "\n")
        latencyOutput.close()
        for i in range (0, int(endTime / timeSlot)):
            rate = 0
            beginTime = timeSlot * i
            timeLength = timeSlot
            dropRateOutput = open("Results/Q" + str(question) + "/dropRate-" + type + ".csv", 'a')
            throughputOutput = open("Results/Q" + str(question) + "/throughput-" + type + ".csv", 'a')
            dropRateOutput.write(str(beginTime) + ";" + str(calculateDropRate(type, str(rate), str(question), 1, beginTime, timeLength, True)) + "\n")
            throughputOutput.write(str(beginTime) + ";" + str(calculateThroughput(type, str(rate), str(question), 4, beginTime, timeLength, True)) + "\n")
            dropRateOutput.close()
            throughputOutput.close()
    for type in typesFor2:
        for i in range (0, int(endTime / timeSlot)):
            rate = 0
            beginTime = timeSlot * i
            timeLength = timeSlot
            dropRateOutput = open("Results/Q" + str(question) + "/dropRate-" + type + ".csv", 'a')
            throughputOutput = open("Results/Q" + str(question) + "/throughput-" + type + ".csv", 'a')
            dropRateOutput.write(str(beginTime) + ";" + str(calculateDropRate(type, str(rate), str(question), 5, beginTime, timeLength, True)) + "\n")
            throughputOutput.write(str(beginTime) + ";" + str(calculateThroughput(type, str(rate), str(question), 6, beginTime, timeLength, True)) + "\n")
            dropRateOutput.close()
            throughputOutput.close()


if __name__ == '__main__':
    CalculateQ1()
    CalculateQ2()
    CalculateQ3()

def calculateCongestionWindow():
    times = {'0':0}
    f = open("inputTimes.csv", "rt")
    lines = f.readlines()
    lines = lines[0].split("\r")
    f.close()
    oldTime = 0
    oldKey = 0
    for line in lines:
        time = float(line)
        if (time - oldTime < 0.005):
            times[str(oldKey)] = times[str(oldKey)] + 1
            oldTime = time
        else:
            key = time
            times[str(key)] = 1
            oldKey = key
            oldTime = time
    output = open("timeResult.csv" , "w")
    for k in times:
        output.write(str(k) + "," + str(times.get(k)) + "\n")
    output.close()