#Create a simulator object
set ns [new Simulator]

#Open the trace file
set tf [open log-newreno-vegas.tr w]
$ns trace-all $tf

#Define a 'finish' procedure
proc finish {} {
	global tf
	set awkCode {
	    {
		if ($5 == "tcp" || $5 == "ack"){
		    if ($8 == "1")
			print $1, $2, $3+1, $4+1, $5, $6, $11, $12 >> "tcp-newreno-vegas-1.tr"
		    else if ($8 == "2")
			print $1, $2, $3+1, $4+1, $5, $6, $11, $12 >> "tcp-newreno-vegas-2.tr"
		}
	    }
	}
	exec rm -f tcp-newreno-vegas-1.tr
	exec rm -f tcp-newreno-vegas-1.tr
	exec awk $awkCode log-newreno-vegas.tr

	# Close the trace file (after you finish the experiment!)
	close $tf
        exit 0
}

#Create six nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n4 $n3 10Mb 10ms DropTail
$ns duplex-link $n6 $n3 10Mb 10ms DropTail

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 10000
# change rate until tcp can reach its bottleneck
$cbr set rate_ 1mb
$cbr set random_ false

#Setup a TCP1 connection
set tcp1 [new Agent/TCP/Newreno]
$tcp1 set window_ 1000000
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 1

#Setup a FTP1 over TCP1 connection
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

#Setup a TCP2 connection
set tcp2 [new Agent/TCP/Vegas]
$tcp2 set window_ 1000000
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
$tcp2 set fid_ 2

#Setup a FTP2 over TCP2 connection
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP

#Schedule events for the CBR and FTP agents
$ns at 0 "$cbr start"
$ns at 0 "$ftp1 start"
$ns at 0 "$ftp2 start"
$ns at 120 "$ftp1 stop"
$ns at 120 "$ftp2 stop"
$ns at 120 "$cbr stop"

#Call the finish procedure after 9 seconds of simulation time
$ns at 120 "finish"

#Run the simulation
$ns run

