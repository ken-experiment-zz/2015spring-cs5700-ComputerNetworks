def recvbyline(self, s) :
    recvfile = s.makefile('rb')
    data_recv = []
    linedata = recvfile.readline()

    while recvfile and linedata :
        data_recv.append(linedata)
        linedata = recvfile.readline()

    return "".join(data_recv)
