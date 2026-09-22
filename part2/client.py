import socket
import sys

HOST = "127.0.0.1"
PORT = 65432
TIMEOUT = 5

TEST_MESSAGES = [
    b"Hello, world!",
    b"second message",
    b"   ",
    b"\xff\xfe\xfa",
    b"x" * 2000,
    "héllo ünïcode".encode("utf-8"),
    b"quit",
]

def send_and_receive(sock, reader, payload):
    sock.sendall(payload + b"\n")
    reply = reader.readline()
    if not reply:
        raise ConnectionError("server closed the connection")
    return reply.decode("utf-8", errors="replace").rstrip("\n")

def run_tests(sock, reader):
    for payload in TEST_MESSAGES:
        reply = send_and_receive(sock, reader, payload)
        shown = payload if len(payload) <= 40 else payload[:40] + b"..."
        print(f"sent {shown!r:<50} received {reply!r}")

def run_interactive(sock, reader):
    print("Type messages, 'quit' to exit")
    while True:
        try:
            text = input("> ")
        except EOFError:
            text = "quit"
        reply = send_and_receive(sock, reader, text.encode("utf-8"))
        print(reply)
        if reply == "BYE":
            break

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "interactive"
    try:
        with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as sock, sock.makefile("rb") as reader:
            print(f"Connected to {HOST}:{PORT}")
            if mode == "test":
                run_tests(sock, reader)
            else:
                run_interactive(sock, reader)
    except ConnectionRefusedError:
        print(f"No server on {HOST}:{PORT}. Start server.py first.")
        sys.exit(1)
    except TimeoutError:
        print("Server did not respond in time.")
        sys.exit(1)
    except OSError as e:
        print(f"Connection problem: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nClient stopped")

if __name__ == "__main__":
    main()