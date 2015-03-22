set k 1
foreach  i  $argv  {
	if {$k == 1} {set queueType $i}
	if {$k == 2} {set protocol $i}
	incr k
}

puts "queueType is = $queueType"
puts "prototol is = $protocol"

set filePath "ex3_result/"
append filePath $queueType
append filePath "_"
append filePath $protocol
append filePath ".tr"

puts $filePath

#Create a simulator object
set ns [new Simulator]

#Open the NAM trace file
set nf [open $filePath w]
$ns trace-all $nf

#Define a 'finish' procedure
proc finish {} {
        global ns nf
        $ns flush-trace
        close $nf
        exit 0
}

#Create four nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#Create links between the nodes
if {$queueType eq "DropTail"} {
	$ns duplex-link $n1 $n2 10Mb 1ms DropTail
	$ns duplex-link $n4 $n3 10Mb 1ms DropTail
	$ns duplex-link $n5 $n2 10Mb 1ms DropTail
	$ns duplex-link $n3 $n2 10Mb 1ms DropTail
	$ns duplex-link $n6 $n3 10Mb 1ms DropTail
	puts "queuType is $queueType"
} elseif {$queueType eq "RED"} {
	$ns duplex-link $n1 $n2 10Mb 1ms RED
	$ns duplex-link $n4 $n3 10Mb 1ms RED
	$ns duplex-link $n5 $n2 10Mb 1ms RED
	$ns duplex-link $n3 $n2 10Mb 1ms RED
	$ns duplex-link $n6 $n3 10Mb 1ms RED
	puts "queuType is $queueType"
}

#Set Queue Size of link (n2-n3) to 10
$ns queue-limit $n2 $n3 10

set clocktime [clock microseconds]
$defaultRNG seed [expr $clocktime % 1000000]

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null
$udp set fid_ 2

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ 7mb
$cbr set random_ 1 

#Setup a TCP connection
if {$protocol eq "Reno"} {
	set tcp [new Agent/TCP/Reno]
	$tcp set class_ 2
	$ns attach-agent $n1 $tcp
	set sink [new Agent/TCPSink]
	$ns attach-agent $n4 $sink
	$ns connect $tcp $sink
	$tcp set fid_ 1
	puts "protocol is Reno"
} elseif {$protocol eq "SACK"} {
	set tcp [new Agent/TCP/Sack1]
	$tcp set class_ 2
	$ns attach-agent $n1 $tcp
	set sink [new Agent/TCPSink/Sack1]
	$ns attach-agent $n4 $sink
	$ns connect $tcp $sink
	$tcp set fid_ 1
	puts "protocol is SACK"
}

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP


#Schedule events for the CBR and FTP agents
$ns at 0.1 "$ftp start"
$ns at 5.0 "$cbr start"
$ns at 35.0 "$cbr stop"
$ns at 39.9 "$ftp stop"

#Call the finish procedure after 5 seconds of simulation time
$ns at 40.0 "finish"

#Run the simulation
$ns run

