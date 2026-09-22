import sys
import xmlrpc.client

URL = "http://127.0.0.1:8001/"

INVALID_MATRIX = 101
RESULT_OUT_OF_RANGE = 102
INCOMPATIBLE_DIMENSIONS = 103

TESTS = [
    ("example for TP", [[1, 2], [3, 4]], [[5, 6], [7, 8]], [[19, 22], [43, 50]]),
    ("identity", [[4, -2], [7, 3]], [[1, 0], [0, 1]], [[4, -2], [7, 3]]),
    ("floats", [[0.5, 1.5], [2, 0]], [[2, 4], [1, 0.5]], [[2.5, 2.75], [4, 8]]),
    ("non-square 2x3 by 3x2", [[1, 2, 3], [4, 5, 6]], [[7, 8], [9, 10], [11, 12]], [[58, 64], [139, 154]]),
    ("incompatible dimensions", [[1, 2], [3, 4]], [[1, 2, 3]], None),
    ("not rectangular", [[1, 2], [3]], [[1, 0], [0, 1]], None),
    ("invalid element", [[1, "x"], [3, 4]], [[1, 0], [0, 1]], None),
    ("overflow", [[100000, 0], [0, 1]], [[100000, 0], [0, 1]], None),
]


def format_matrix(matrix):
    cells = [[str(value) for value in row] for row in matrix]
    width = max(len(cell) for row in cells for cell in row)
    return "\n".join("  [ " + "  ".join(cell.rjust(width) for cell in row) + " ]" for row in cells)


def multiply_remote(proxy, A, B):
    try:
        return proxy.multiplyMatrices(A, B)
    except xmlrpc.client.Fault as fault:
        if fault.faultCode in (INVALID_MATRIX, INCOMPATIBLE_DIMENSIONS, RESULT_OUT_OF_RANGE):
            raise ValueError(fault.faultString) from None
        raise


def run_test(proxy, title, A, B, expected):
    print(f"=== {title} ===")
    print("A =")
    print(format_matrix(A))
    print("B =")
    print(format_matrix(B))
    try:
        C = multiply_remote(proxy, A, B)
    except ValueError as e:
        print(f"Server rejected the request: {e}")
        passed = expected is None
        print("Result: error, as expected\n" if passed else "Result: FAIL, unexpected error\n")
        return passed
    print("C = A x B =")
    print(format_matrix(C))
    passed = C == expected
    print("Result: matches expected\n" if passed else f"Result: FAIL, expected {expected}\n")
    return passed


def main():
    tests = TESTS[:1] if len(sys.argv) > 1 and sys.argv[1] == "lab" else TESTS
    try:
        with xmlrpc.client.ServerProxy(URL) as proxy:
            passed = sum(run_test(proxy, *test) for test in tests)
    except ConnectionRefusedError:
        print(f"No RPC server at {URL}. Start server.py first.")
        sys.exit(1)
    except OSError as e:
        print(f"Connection problem: {e}")
        sys.exit(1)
    print(f"{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    main()