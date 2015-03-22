#Create a simulator object
set ns [new Simulator]

#Open the trace file
set tf [open log-vegas.tr w]
$ns trace-all $tf

#Define a 'finish' procedure
proc finish {} {
	global tf
	set awkCode {
	    {
		if ($5 == "tcp" || $5 == "ack"){
			print $1, $2, $3+1, $4+1, $5, $6, $7, $8, $9, $10, $11, $12 >> "tcp-vegas.tr"
		}
	    }
	}
	exec rm -f tcp-vegas.tr
	exec awk $awkCode log-vegas.tr

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
$cbr set rate_ 10mb
$cbr set random_ false

#Setup a TCP connection
set tcp [new Agent/TCP/Vegas]
$tcp set window_ 1000000
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP

#Schedule events for the CBR and FTP agents
$ns at 0 "$cbr start"
$ns at 0 "$ftp start"
$ns at 50 "$ftp stop"
$ns at 50 "$cbr stop"

#Call the finish procedure after 9 seconds of simulation time
$ns at 50 "finish"

#Run the simulation
$ns run

