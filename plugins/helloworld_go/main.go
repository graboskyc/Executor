package main

import (
	"fmt"
	"os"
	"time"

	"github.com/fatih/color"
)

func main() {
	color.Green("Hello World from Go!")
	fmt.Println(time.Now())
	color.Cyan("Environment variables:")
	for _, env := range os.Environ() {
		fmt.Println(env)
	}
}
