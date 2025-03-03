import socket
import threading
import hashlib
import os

HOST = '0.0.0.0'  
PORT = 8000

def calcular_hash(arquivo):
    hasher = hashlib.sha256()
    with open(arquivo, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def handle_client(conn, addr):
    print(f"Nova conexão de {addr} - Threads ativas: {threading.active_count()}")
    historico = []
    while True:
        try:
            requisicao = conn.recv(1024).decode()
            historico.append(requisicao)
            if not requisicao:
                break
            
            if requisicao.lower() == "sair":
                print(f"Cliente {addr} desconectado")
                break
            
            elif requisicao.lower().startswith("arquivo "):
                nome_arquivo = requisicao.split(" ", 1)[1]
                if os.path.exists(nome_arquivo):
                    tamanho = os.path.getsize(nome_arquivo)
                    hash_arquivo = calcular_hash(nome_arquivo)
                    print(f"OK {nome_arquivo} {tamanho} {hash_arquivo}")
                    conn.sendall(f"OK {nome_arquivo} {tamanho} {hash_arquivo}".encode())

                    confirmacao = conn.recv(1024).decode() 
                    historico.append(confirmacao)
                    if confirmacao == "OK":
                        with open(nome_arquivo, 'rb') as f:
                            while chunk := f.read(4096):
                                conn.sendall(chunk)
                    else:
                        conn.sendall("NC Nao houve confirmacao para envio do arquivo".encode())
                else:
                    conn.sendall("NOK Arquivo nao existe".encode())
            
            elif requisicao.lower() == "chat": 
                historico_str = "\n".join(historico)
                conn.sendall(historico_str.encode())

        except:
            break
    
    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.bind((HOST, PORT))
    server.listen(5) 
    print(f"Servidor escutando em {HOST}:{PORT}")
    print(f"Threads ativas ao iniciar o servidor: {threading.active_count()}")
    while True:
        conn, addr = server.accept() 
        print(f"Nova thread a ser adicionada: {threading.active_count()}")
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"Threads ativas: {threading.active_count()}")

if __name__ == "__main__":
    start_server()