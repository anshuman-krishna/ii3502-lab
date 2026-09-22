import sys
import xmlrpc.client

URL = "http://127.0.0.1:8000/"
OPERATIONS = ("add", "subtract", "multiply", "divide")

DIVISION_BY_ZERO = 100
INVALID_ARGUMENT = 101
RESULT_OUT_OF_RANGE = 102

TESTS = [
    ("add", 95, 23),
    ("subtract", 711, 420),
    ("multiply", 6, 7),
    ("divide", 83, 4),
    ("add", 12.5, 0.25),
    ("divide", 7, 0),
    ("multiply", 100000, 100000),
    ("add", "5", 3),
]

def call(proxy, name, x, y):
    remote_function = getattr(proxy, name)
    try:
        return remote_function(x, y)
    except xmlrpc.client.Fault as fault:
        if fault.faultCode == DIVISION_BY_ZERO:
            raise ZeroDivisionError(fault.faultString) from None
        if fault.faultCode in (INVALID_ARGUMENT, RESULT_OUT_OF_RANGE):
            raise ValueError(fault.faultString) from None
        raise

def run_one(proxy, name, x, y):
    try:
        result = call(proxy, name, x, y)
        print(f"{name}({x!r}, {y!r}) = {result}")
    except ZeroDivisionError as e:
        print(f"{name}({x!r}, {y!r}) raised ZeroDivisionError: {e}")
    except ValueError as e:
        print(f"{name}({x!r}, {y!r}) raised ValueError: {e}")

def parse_number(text):
    try:
        return int(text)
    except ValueError:
        return float(text)

def main():
    try:
        with xmlrpc.client.ServerProxy(URL) as proxy:
            if len(sys.argv) == 4:
                name = sys.argv[1]
                if name not in OPERATIONS:
                    print(f"Unknown operation '{name}'. Use one of: {', '.join(OPERATIONS)}")
                    sys.exit(1)
                try:
                    x, y = parse_number(sys.argv[2]), parse_number(sys.argv[3])
                except ValueError:
                    print("Both operands must be numbers.")
                    sys.exit(1)
                run_one(proxy, name, x, y)
            else:
                for name, x, y in TESTS:
                    run_one(proxy, name, x, y)
    except ConnectionRefusedError:
        print(f"No RPC server at {URL}. Start server.py first.")
        sys.exit(1)
    except OSError as e:
        print(f"Connection problem: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()