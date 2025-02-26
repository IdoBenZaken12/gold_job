import socket
import json
import threading

HOST = '127.0.0.1'
PORT = 12345

jobs = []  # Store job postings in memory
lock = threading.Lock()  # Ensure thread-safe modifications


def handle_client(client_socket):
    """Handles communication with a connected client."""
    global jobs

    while True:
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                break  # Client disconnected

            print(f"Received data: {data}")
            request = json.loads(data)

            if "request" in request and request["request"] == "get_jobs":
                # Send job list to client
                with lock:
                    client_socket.sendall(json.dumps(jobs).encode('utf-8'))
                    print(f"Sent jobs: {jobs}")

            else:
                # Assume request is a job posting
                with lock:
                    jobs.append(request)
                    print(f"Added job: {request}")

                client_socket.sendall(json.dumps({"status": "success"}).encode('utf-8'))

        except Exception as e:
            print(f"Error handling client: {str(e)}")
            break

    client_socket.close()
    print("Client disconnected")


def start_server():
    """Starts the job board server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"New connection from {addr}")

            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
