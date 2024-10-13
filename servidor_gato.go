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
var disponible = true

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

func GenerateRandomPort() int {
	randomPort, _ := rand.Int(rand.Reader, big.NewInt(65535-8000+1))
	return int(randomPort.Int64()) + 8000
}

func CreateNewConnectionForMove() (*net.UDPConn, int) {
	port := GenerateRandomPort()
	address := fmt.Sprintf("127.0.0.1:%d", port)
	udpAddr, err := net.ResolveUDPAddr("udp", address)
	if err != nil {
		fmt.Println("Error al resolver dirección:", err)
		os.Exit(1)
	}

	conn, err := net.ListenUDP("udp", udpAddr)
	if err != nil {
		fmt.Println("Error al escuchar en el puerto:", port, err)
		os.Exit(1)
	}

	fmt.Printf("Servidor Gato: Conexión UDP abierta en el puerto %d para realizar la jugada.\n", port)
	return conn, port
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

		if message == "Disponible?" {
			if disponible {
				conn.WriteToUDP([]byte("Si"), addr)
			} else {
				conn.WriteToUDP([]byte("No"), addr)
			}
		} else if message == "Jugar" {
			disponible = false // Marcar como no disponible durante el juego
			// Crear una nueva conexión UDP en un puerto aleatorio para cada jugada
			newConn, port := CreateNewConnectionForMove()
			defer newConn.Close()

			// Generar jugada
			row, col := GenerateMove()
			response := fmt.Sprintf("Jugada:%d,%d", row, col)
			conn.WriteToUDP([]byte(response), addr)
			fmt.Printf("Servidor Gato: Jugada enviada desde el puerto %d - Fila: %d, Columna: %d\n", port, row, col)
			fmt.Printf("Servidor Gato: Cerrando la conexión en el puerto %d.\n", port)

		} else if message == "Terminar" {
			fmt.Println("Servidor Gato: Finalizando juego.")
			disponible = true // Marcar como disponible después de terminar el juego
			conn.WriteToUDP([]byte("Terminado"), addr)
			break
		}
	}
}
