set k 1
 foreach  i  $argv  {
	 if {$k == 1} {set protocol $i}
	 if {$k == 2} {set cbrRate $i}
	 incr k
	  }

puts "prototol is = $protocol"
puts "cbrRate is = $cbrRate"

set filePath "ex1_result/"
append filePath $protocol
append filePath "_" 
append filePath $cbrRate
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

#Create links between the nodes
$ns duplex-link $n1 $n2 10Mb 1ms DropTail
$ns duplex-link $n2 $n3 10Mb 1ms DropTail
$ns duplex-link $n3 $n4 10Mb 1ms DropTail

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
$udp set fid_ 2

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ [expr $cbrRate]mb
$cbr set random_ 1

#Setup a TCP connection
if {$protocol eq "Tahoe"} {
	set tcp [new Agent/TCP]
	puts "protocol is Tahoe"}
if {$protocol eq "Reno"} {
	set tcp [new Agent/TCP/Reno]
	puts "protocol is Reno"}
if {$protocol eq "NewReno"} {
	set tcp [new Agent/TCP/Newreno]
	puts "protocol is NewReno"}
if {$protocol eq "Vegas"} {
	set tcp [new Agent/TCP/Vegas]
	puts "protocol is Vegas"}
$tcp set class_ 2
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1
$tcp set window_ 70 

#Setup a FTP over TCP connection
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP

#Schedule events for the CBR and FTP agents
$ns at 0.1 "$cbr start"
$ns at 3.0 "$ftp start"
$ns at 13.0 "$ftp stop"
$ns at 14.4 "$cbr stop"

#Detach tcp and sink agents (not really necessary)
$ns at 14.5 "$ns detach-agent $n1 $tcp ; $ns detach-agent $n4 $sink"

#Call the finish procedure after 5 seconds of simulation time
$ns at 15.0 "finish"


#Run the simulation
$ns run
