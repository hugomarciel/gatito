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
        if idx < 2:
            print("  ---+---+---")

def handle_gameplay(server):
    """ Maneja el flujo de juego """
    while True:
        try:
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
        except ConnectionResetError:
            print("Conexión con el servidor perdida.")
            break
        except Exception as e:
            print(f"Error durante el juego: {e}")
            break

def main():
    """ Función principal del cliente """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.connect((HOST, PORT))
            print(MESSAGE_MAIN_MENU)
            option = input("Selecciona una opción: ")

            if option == "1":
                server.sendall("Solicitar Partida".encode())
                data = server.recv(1024)
                if data == b"Disponibilidad:Si":
                    print("Comienza el juego...")
                    handle_gameplay(server)
                elif data == b"Servidor Gato No Disponible, Espere...":
                    print("Servidor Gato No Disponible, Espere...")
                else:
                    print("Lo siento, el juego no está disponible en este momento.")
            else:
                print("Saliendo del juego.")
    except ConnectionRefusedError:
        print("No se pudo conectar al servidor.")
    except Exception as e:
        print(f"Error en el cliente: {e}")

if __name__ == "__main__":
    main()
