package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"runtime"
	"time"
)

var dests = make([]string, 0)

func main() {
	if len(os.Args[1:]) < 1 {
		log.Fatal("Must specify a log name")
	}

	// build list of destination addresses
	dests = append(dests, "ucsd.edu")
	dests = append(dests, "ieng6.ucsd.edu")
	for _, dest := range os.Args[2:] {
		dests = append(dests, dest)
	}

	// load file for writing output
	var outFile = "logs" + string(os.PathSeparator) + os.Args[1] + ".log"
	file, err := os.OpenFile(outFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}

	// write host name to file
	writeF(file, []byte("-----------------------------------------------------------"))
	writeF(file, []byte("\nHOST NAME: "+os.Args[1]+"\n"))

	// write current time to file
	time := time.Now().Format(time.RFC850)
	writeF(file, []byte(time+"\n"))

	fmt.Println(runtime.GOOS)

	// for every destination address
	for _, dest := range dests {
		var out []byte

		writeF(file, []byte("\n"+dest+":\n"))
		writeF(file, []byte("...................."))

		// run ping
		if runtime.GOOS == "windows" {
			out, _ = exec.Command("ping", "-n", "15", dest).Output()
		} else {
			out, _ = exec.Command("ping", "-c", "15", dest).Output()
		}
		writeF(file, out)
		file.Sync()

		// // run iperf
		// if runtime.GOOS == "windows" {
		// 	out, _ = exec.Command("iperf/iperf3", "-c", dest).Output()
		// } else {
		// 	out, _ = exec.Command("ping", "-c", dest).Output()
		// }
		// writeF(file, []byte("\n"))
		// writeF(file, out)
		// file.Sync()

		// run traceroute/tracert
		if runtime.GOOS == "windows" {
			out, _ = exec.Command("tracert", dest).Output()
		} else {
			out, _ = exec.Command("traceroute", dest).Output()
		}
		writeF(file, out)
	}

	// flush and close the output file
	if err := file.Close(); err != nil {
		log.Fatal(err)
	}
}

func writeF(file *os.File, output []byte) {
	if _, err := file.Write(output); err != nil {
		file.Close()
		log.Fatal(err)
	}
}
