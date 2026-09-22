from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import Fault

HOST = "127.0.0.1"
PORT = 8000
INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1

DIVISION_BY_ZERO = 100
INVALID_ARGUMENT = 101
RESULT_OUT_OF_RANGE = 102

def log(message):
    print(message, flush=True)

def check_numbers(name, x, y):
    for value in (x, y):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            log(f"{name}({x!r}, {y!r}) -> rejected: invalid argument")
            raise Fault(INVALID_ARGUMENT, f"{name} expects two numbers, got {value!r}")

def finish(name, x, y, result):
    if isinstance(result, int) and not INT_MIN <= result <= INT_MAX:
        log(f"{name}({x}, {y}) -> rejected: result out of range")
        raise Fault(RESULT_OUT_OF_RANGE, f"{name}({x}, {y}) = {result} exceeds the XML-RPC 32-bit integer limit")
    log(f"{name}({x}, {y}) -> {result}")
    return result

def add(x, y):
    check_numbers("add", x, y)
    return finish("add", x, y, x + y)

def subtract(x, y):
    check_numbers("subtract", x, y)
    return finish("subtract", x, y, x - y)

def multiply(x, y):
    check_numbers("multiply", x, y)
    return finish("multiply", x, y, x * y)

def divide(x, y):
    check_numbers("divide", x, y)
    if y == 0:
        log(f"divide({x}, {y}) -> rejected: division by zero")
        raise Fault(DIVISION_BY_ZERO, "cannot divide by zero")
    return finish("divide", x, y, x / y)

def main():
    with SimpleXMLRPCServer((HOST, PORT), logRequests=False) as server:
        for function in (add, subtract, multiply, divide):
            server.register_function(function, function.__name__)
        log(f"RPC server listening on http://{HOST}:{PORT}/")
        log("Registered: add, subtract, multiply, divide")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            log("\nRPC server shutting down")

if __name__ == "__main__":
    main()