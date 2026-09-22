import socket
import sys

HOST = "127.0.0.1"
PORT = 65432
MAX_LINE = 1024
IDLE_TIMEOUT = 120


def log(addr, message):
    print(f"[{addr[0]}:{addr[1]}] {message}", flush=True)


def skip_rest(reader):
    while True:
        chunk = reader.readline(MAX_LINE)
        if not chunk or chunk.endswith(b"\n"):
            return


def process(raw):
    try:
        text = raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return "ERROR: invalid UTF-8"
    if not text:
        return "ERROR: empty message"
    if text.lower() == "quit":
        return "BYE"
    return f"ECHO: {text}"


def handle_client(conn, addr):
    log(addr, "connected")
    count = 0
    try:
        with conn, conn.makefile("rb") as reader:
            while True:
                line = reader.readline(MAX_LINE + 1)
                if not line:
                    break
                if len(line) > MAX_LINE and not line.endswith(b"\n"):
                    skip_rest(reader)
                    reply = "ERROR: message too long"
                else:
                    reply = process(line)
                count += 1
                shown = line if len(line) <= 40 else line[:40] + b"..."
                log(addr, f"#{count} recv {shown!r} -> {reply}")
                conn.sendall((reply + "\n").encode("utf-8"))
                if reply == "BYE":
                    break
    except TimeoutError:
        log(addr, "idle timeout")
    except (ConnectionResetError, BrokenPipeError):
        log(addr, "connection lost")
    except OSError as e:
        log(addr, f"socket error: {e}")
    finally:
        log(addr, f"disconnected after {count} messages")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((HOST, PORT))
        except OSError as e:
            print(f"Cannot bind {HOST}:{PORT}: {e}")
            sys.exit(1)
        server.listen()
        print(f"Server listening on {HOST}:{PORT}", flush=True)
        try:
            while True:
                conn, addr = server.accept()
                conn.settimeout(IDLE_TIMEOUT)
                handle_client(conn, addr)
        except KeyboardInterrupt:
            print("\nServer shutting down")


if __name__ == "__main__":
    main()