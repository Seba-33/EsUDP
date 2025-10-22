import socket
import time
import sys

# Configurazione del server di destinazione
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999

NUM_MESSAGES = 10
TIMEOUT = 2.5        # secondi: il client ritrasmette ogni 2.5s (timeout)
DELAY_BETWEEN = 0.1  # ritardo opzionale dopo ACK prima del prossimo invio
MAX_RETRIES = 5      # numero di ritentativi prima di abortire

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)

    for i in range(1, NUM_MESSAGES + 1):
        message = f"Msg {i}: Ciao server UDP, sono il client!"
        attempt = 0
        acknowledged = False

        while attempt < MAX_RETRIES and not acknowledged:
            attempt += 1
            print(f"[*] Invio messaggio {i}/{NUM_MESSAGES} (tentativo {attempt}) a {SERVER_IP}:{SERVER_PORT}")
            client_socket.sendto(message.encode('utf-8'), (SERVER_IP, SERVER_PORT))

            try:
                response_bytes, server_addr = client_socket.recvfrom(1024)
                response_message = response_bytes.decode('utf-8', errors='replace')
                print(f"[*] Risposta ricevuta da {server_addr}: {response_message}")

                if response_message.startswith("ACK"):
                    acknowledged = True
                    time.sleep(DELAY_BETWEEN)
                    break
                else:
                    print("[!] Risposta non-ACK ricevuta: interrompo gli invii.")
                    client_socket.close()
                    sys.exit(1)

            except socket.timeout:
                if attempt < MAX_RETRIES:
                    print(f"[!] Timeout: nessuna risposta per il messaggio {i}, ritrasmetto (prossimo tentativo).")
                    # il ciclo reinvia immediatamente (il recv timeout è di 2.5s)
                else:
                    print(f"[!] Timeout: nessuna risposta per il messaggio {i} dopo {MAX_RETRIES} tentativi. Interrompo gli invii.")
                    client_socket.close()
                    sys.exit(1)
            except socket.error as e:
                print(f"Errore del socket durante recv: {e}")
                client_socket.close()
                sys.exit(1)

    print("[*] Tutti i messaggi inviati (o processo interrotto).")

except socket.error as e:
    print(f"Errore del socket: {e}")
except Exception as e:
    print(f"Si è verificato un errore: {e}")
finally:
    if 'client_socket' in locals():
        client_socket.close()