import socket
import hashlib
import uuid


HOST = '0.0.0.0'  
PORT = 8000  

def calcular_hash(arquivo):
    hasher = hashlib.sha256()
    with open(arquivo, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    while True:
        comando = input("Digite um comando (sair, arquivo <nome>, chat): ")
        client.sendall(comando.encode())
        
        if comando.lower() == "sair":
            break
        
        elif comando.lower().startswith("arquivo "):
            resposta = client.recv(1024)
            resposta = resposta.decode()
            if resposta.startswith("OK"):
                _, nome_arquivo, tamanho, hash_servidor = resposta.split(" ")
                tamanho = int(tamanho)
                client.sendall("OK".encode())
                id = uuid.uuid4()
                with open(f"{id}-{nome_arquivo}", "wb") as f:
                    recebido = 0
                    while recebido < tamanho:
                        chunk = client.recv(4096)
                        if not chunk:
                            break
                        f.write(chunk)
                        recebido += len(chunk)
                
                hash_cliente = calcular_hash(f"{id}-{nome_arquivo}")
                if hash_cliente == hash_servidor:
                    print("Arquivo recebido com sucesso e verificado!")
                else:
                    print("Erro na integridade do arquivo!")
            else:
                print(resposta)
        
        elif comando.lower() == "chat":
            resposta = client.recv(1024)
            resposta = resposta.decode()
            print(resposta)
    
    client.close()

if __name__ == "__main__":
    start_client()
