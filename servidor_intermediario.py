import socket
import pickle

HOST = "localhost"
PORT = 8000
PORT_GATO = 8001

# Estado inicial del tablero 3x3
table = [[" " for _ in range(3)] for _ in range(3)]

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

def send_gato_move():
    gato_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    gato_conn.sendto(b"Jugar", (HOST, PORT_GATO))
    data, _ = gato_conn.recvfrom(1024)
    gato_conn.close()
    
    jugada = data.decode().split(":")[1]
    row, col = map(int, jugada.split(","))
    return row, col

def listen():
    while True:
        client, address = server.accept()
        print(f"Cliente conectado: {address}")
        while True:
            data = client.recv(1024).decode()
            
            if data == "Ver Tablero":
                client.sendall(pickle.dumps(table))
            elif data.startswith("Jugada"):
                _, move = data.split(":")
                row, col = map(int, move.split(","))
                if insert_move("X", row, col):
                    if check_winner("X"):
                        client.sendall(b"Jugador Gana")
                        break
                    # Turno del Gato
                    row_gato, col_gato = send_gato_move()
                    insert_move("O", row_gato, col_gato)
                    if check_winner("O"):
                        client.sendall(b"Robot Gana")
                        break
                client.sendall(pickle.dumps(table))
            elif data == "Desconectar":
                client.sendall(b"Desconectado")
                client.close()
                break

listen()
