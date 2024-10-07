package main

import (
	"crypto/rand"
	"fmt"
	"math/big"
	"net"
	"os"
)

var moves = 9
var main_port = "8001"

func main() {
	fmt.Println("Servidor Gato: En ejecución, esperando mensajes...")
	GenerateListenConnectionToStart()
}

func GenerateMove() (int, int) {
	moves -= 1
	row, col := ChooseRandomMove()
	fmt.Printf("Servidor Gato: Jugada - fila: %d, columna: %d\n", row+1, col+1)
	return row, col
}

func ChooseRandomMove() (int, int) {
	randomRow, _ := rand.Int(rand.Reader, big.NewInt(3)) // Filas 0-2
	randomCol, _ := rand.Int(rand.Reader, big.NewInt(3)) // Columnas 0-2
	return int(randomRow.Int64()), int(randomCol.Int64())
}

func GenerateListenConnectionToStart() {
	address := "127.0.0.1:" + main_port
	udpAddr, err := net.ResolveUDPAddr("udp", address)
	if err != nil {
		fmt.Println("Error al resolver dirección:", err)
		os.Exit(1)
	}

	conn, err := net.ListenUDP("udp", udpAddr)
	if err != nil {
		fmt.Println("Error al escuchar en:", address, err)
		os.Exit(1)
	}
	defer conn.Close()

	buf := make([]byte, 1024)
	for moves > 0 {
		n, addr, _ := conn.ReadFromUDP(buf)
		message := string(buf[:n])
		fmt.Println("Servidor Gato: Mensaje recibido -", message)

		if message == "Jugar" {
			row, col := GenerateMove()
			response := fmt.Sprintf("Jugada:%d,%d", row, col)
			conn.WriteToUDP([]byte(response), addr)
		} else if message == "Desconectar" {
			fmt.Println("Servidor Gato: Finalizando juego.")
			conn.WriteToUDP([]byte("Desconectado"), addr)
			break
		}
	}
}
