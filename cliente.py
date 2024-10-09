import socket
import pickle

HOST = "localhost"
PORT = 8000
MESSAGE_MAIN_MENU = """
--------- Bienvenido al Juego Gato ---------
Selecciona una opción para jugar:
    1. Jugar
    2. Salir
"""
MESSAGE_ENTER_MOVE = "Ingrese su jugada (fila,columna): "

def show_table(table):
    """ Imprime el tablero con las posiciones de filas y columnas """
    print("   0   1   2")
    for idx, row in enumerate(table):
        print(f"{idx}  " + " | ".join(row))
        if idx < 2:  # No imprimir el separador después de la última fila
            print("  ---+---+---")

def handle_gameplay(server):
    """ Maneja el flujo de juego """
    while True:
        print("1- Ver Tablero\n2- Ingresar Jugada\n3- Salir")
        option = input("Seleccione una opción: ")

        if option == "1":
            server.sendall("Ver Tablero".encode())
            data = server.recv(1024)
            table = pickle.loads(data)
            show_table(table)
        elif option == "2":
            move = input(MESSAGE_ENTER_MOVE)
            server.sendall(f"Jugada:{move}".encode())
            data = server.recv(1024)
            if data == b"Jugador Gana":
                print("¡Felicidades! Ganaste.")
                break
            elif data == b"Robot Gana":
                print("El robot ganó.")
                break
            table = pickle.loads(data)
            show_table(table)
        elif option == "3":
            server.sendall("Desconectar".encode())
            print("Desconectado del juego.")
            break

def main():
    """ Función principal del cliente """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.connect((HOST, PORT))
        print(MESSAGE_MAIN_MENU)
        option = input("Selecciona una opción: ")

        if option == "1":
            print("Comienza el juego...")
            handle_gameplay(server)
        else:
            print("Saliendo del juego.")

if __name__ == "__main__":
    main()