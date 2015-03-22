set k 1
foreach  i  $argv  {
	if {$k == 1} {set protocol1 $i}
	if {$k == 2} {set protocol2 $i}
	if {$k == 3} {set cbrRate $i}
	incr k
	}

set filePath "ex2_result/"
append filePath $protocol1
append filePath "_"
append filePath $protocol2
append filePath "_"
append filePath $cbrRate
append filePath ".tr"

puts $filePath

#Create a simulator object
set ns [new Simulator]

#Open the trace file
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
$ns duplex-link $n1 $n2 10Mb 1ms DropTail
$ns duplex-link $n5 $n2 10Mb 1ms DropTail
$ns duplex-link $n3 $n2 10Mb 1ms DropTail
$ns duplex-link $n4 $n3 10Mb 1ms DropTail
$ns duplex-link $n6 $n3 10Mb 1ms DropTail

#Set Queue Size of link (n2-n3) to 10
$ns queue-limit $n2 $n3 10

set clocktime [clock microseconds]
$defaultRNG seed [expr $clocktime % 1000000]

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp
set null [new Agent/Null]
$ns attach-agent $n3 $null
$ns connect $udp $null
$udp set fid_ 3

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ [expr $cbrRate]mb
$cbr set random_ 1
puts "cbrRate is [expr $cbrRate]"

#Setup a first type TCP connection
if {$protocol1 eq "Reno"} {
    set tcp1 [new Agent/TCP/Reno]
    puts "protocol1 is Reno"
} 
if {$protocol1 eq "NewReno"} {
	set tcp1 [new Agent/TCP/Newreno]
	puts "protocol1 is NewReno"
} 
if {$protocol1 eq "Vegas"} {
	set tcp1 [new Agent/TCP/Vegas]
	puts "protocol1 is Vegas"}
$tcp1 set class_ 2
$ns attach-agent $n1 $tcp1
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp1 $sink
$tcp1 set fid_ 1

#Setup a FTP over TCP connection
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

#Setup a second type TCP connection
if {$protocol2 eq "Reno"} {
    set tcp2 [new Agent/TCP/Reno]
    puts "protocol2 is Reno"
} elseif {$protocol2 eq "Vegas"} {
	set tcp2 [new Agent/TCP/Vegas]
	puts "protocol2 is Vegas"}
$tcp2 set class_ 2
$ns attach-agent $n5 $tcp2
set sink [new Agent/TCPSink]
$ns attach-agent $n6 $sink
$ns connect $tcp2 $sink
$tcp2 set fid_ 2

#Setup a FTP over TCP connection
set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP

#Schedule events for the CBR and FTP agents
$ns at 0.1 "$cbr start"
$ns at 3.0 "$ftp1 start"
$ns at 3.0 "$ftp2 start"
$ns at 13.0 "$ftp1 stop"
$ns at 13.0 "$ftp2 stop"
$ns at 14.4 "$cbr stop"

#Call the finish procedure after 5 seconds of simulation time
$ns at 14.5 "finish"

#Run the simulation
$ns run

