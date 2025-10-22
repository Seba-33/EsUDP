import socket
import random
import time

# Configurazione
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999
LOSS_PROB = 0.3          # probabilità di drop (30%)
CACHE_TTL = 120          # secondi: quanto tempo tenere in cache i messaggi visti

# Cache per deduplicazione: mappa (addr, message) -> last_seen_timestamp
seen_messages = {}

def cleanup_cache():
    now = time.time()
    to_delete = [k for k, ts in seen_messages.items() if now - ts > CACHE_TTL]
    for k in to_delete:
        del seen_messages[k]

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"[*] Server UDP in ascolto su {SERVER_IP}:{SERVER_PORT} (drop={LOSS_PROB*100:.0f}%)")

    while True:
        cleanup_cache()

        data, addr = server_socket.recvfrom(4096)
        message = data.decode('utf-8', errors='replace')
        key = (addr, message)

        # Stampa solo la prima volta che vediamo (addr, message)
        if key not in seen_messages:
            seen_messages[key] = time.time()
            print(f"[*] Ricevuto da {addr}: {message}")

        # Simula perdita del pacchetto: se viene droppato, non inviare ACK
        if random.random() < LOSS_PROB:
            continue

        # Ritardo casuale prima dell'ACK (0..5s)
        delay = random.uniform(0, 5)
        time.sleep(delay)

        response = f"ACK: Messaggio ricevuto - {message}"
        server_socket.sendto(response.encode('utf-8'), addr)

except socket.error as e:
    print(f"Errore del socket: {e}")
finally:
    if 'server_socket' in locals():
        server_socket.close()