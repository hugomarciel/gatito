import socket
import pickle

HOST = "localhost"
PORT = 8000
PORT_GATO = 8001

table = [[" " for _ in range(3)] for _ in range(3)]
game_in_progress = False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Servidor Intermediario: En ejecución en {HOST}:{PORT}")

def check_winner(symbol):
    for row in table:
        if all(s == symbol for s in row):
            return True
    for col in range(3):
        if all(table[row][col] == symbol for row in range(3)):
            return True
    if table[0][0] == table[1][1] == table[2][2] == symbol or table[0][2] == table[1][1] == table[2][0] == symbol:
        return True
    return False

def insert_move(symbol, row, col):
    if table[row][col] == " ":
        table[row][col] = symbol
        return True
    return False

def request_game_availability():
    gato_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    gato_conn.sendto(b"Disponible?", (HOST, PORT_GATO))
    data, _ = gato_conn.recvfrom(1024)
    gato_conn.close()
    disponibilidad = data.decode() == "Si"
    print(f"Servidor Intermediario: Disponibilidad del Servidor Gato: {'Disponible' if disponibilidad else 'No Disponible'}")
    return disponibilidad

def send_gato_move():
    while True:
        gato_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        gato_conn.sendto(b"Jugar", (HOST, PORT_GATO))
        data, _ = gato_conn.recvfrom(1024)
        gato_conn.close()

        jugada = data.decode().split(":")[1]
        row, col = map(int, jugada.split(","))
        if table[row][col] == " ":
            print(f"Servidor Intermediario: Jugada recibida del Servidor Gato - Fila: {row}, Columna: {col}")
            return row, col

def listen():
    global game_in_progress
    while True:
        try:
            client, address = server.accept()
            print(f"Cliente conectado: {address}")

            if game_in_progress:
                client.sendall(b"Servidor Gato No Disponible, Espere...")
                print(f"Servidor Intermediario: Cliente {address} fue rechazado porque ya hay un juego en progreso.")
                client.close()
                continue

            if request_game_availability():
                game_in_progress = True
                client.sendall(b"Disponibilidad:Si")
                print("Servidor Intermediario: El juego está disponible. Iniciando partida...")
            else:
                client.sendall(b"Disponibilidad:No")
                print("Servidor Intermediario: El Servidor Gato no está disponible. No se puede iniciar el juego.")
                client.close()
                continue

            while True:
                try:
                    data = client.recv(1024)
                    if not data:
                        print(f"Cliente {address} desconectado.")
                        break

                    data = data.decode()
                    print(f"Servidor Intermediario: Mensaje recibido del cliente: {data}")

                    if data == "Ver Tablero":
                        client.sendall(pickle.dumps(table))
                        print(f"Servidor Intermediario: Tablero enviado al cliente: {table}")
                    elif data.startswith("Jugada"):
                        _, move = data.split(":")
                        row, col = map(int, move.split(","))
                        if insert_move("X", row, col):
                            print(f"Servidor Intermediario: Jugada del cliente - Fila: {row}, Columna: {col}")
                            if check_winner("X"):
                                client.sendall(b"Jugador Gana")
                                print("Servidor Intermediario: El jugador ha ganado la partida.")
                                game_in_progress = False
                                break
                            row_gato, col_gato = send_gato_move()
                            insert_move("O", row_gato, col_gato)
                            if check_winner("O"):
                                client.sendall(b"Robot Gana")
                                print("Servidor Intermediario: El Servidor Gato ha ganado la partida.")
                                game_in_progress = False
                                break
                        client.sendall(pickle.dumps(table))
                        print(f"Servidor Intermediario: Tablero actualizado enviado al cliente: {table}")
                    elif data == "Desconectar":
                        client.sendall(b"Desconectado")
                        print(f"Servidor Intermediario: Cliente {address} solicitó la desconexión. Notificando al Servidor Gato...")
                        gato_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        gato_conn.sendto(b"Terminar", (HOST, PORT_GATO))
                        game_in_progress = False
                        client.close()
                        print("Servidor Intermediario: Partida finalizada.")
                        break
                except ConnectionResetError:
                    print(f"Cliente {address} se desconectó inesperadamente.")
                    game_in_progress = False
                    break

        except Exception as e:
            print(f"Error manejando el cliente: {e}")
            continue

listen()
