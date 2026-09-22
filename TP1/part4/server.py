from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import Fault

HOST = "127.0.0.1"
PORT = 8001
INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1

INVALID_MATRIX = 101
RESULT_OUT_OF_RANGE = 102
INCOMPATIBLE_DIMENSIONS = 103


def log(message):
    print(message, flush=True)


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate(name, matrix):
    if not isinstance(matrix, list) or not matrix:
        raise Fault(INVALID_MATRIX, f"{name} must be a non-empty list of rows")
    for i, row in enumerate(matrix):
        if not isinstance(row, list) or not row:
            raise Fault(INVALID_MATRIX, f"{name} row {i} must be a non-empty list of numbers")
        if len(row) != len(matrix[0]):
            raise Fault(INVALID_MATRIX, f"{name} is not rectangular: row 0 has {len(matrix[0])} values, row {i} has {len(row)}")
        for j, value in enumerate(row):
            if not is_number(value):
                raise Fault(INVALID_MATRIX, f"{name}[{i}][{j}] must be a number, got {value!r}")
    return len(matrix), len(matrix[0])


def compute_product(A, B, rows, inner, cols):
    return [
        [sum(A[i][k] * B[k][j] for k in range(inner)) for j in range(cols)]
        for i in range(rows)
    ]


def check_range(C):
    for i, row in enumerate(C):
        for j, value in enumerate(row):
            if isinstance(value, int) and not INT_MIN <= value <= INT_MAX:
                raise Fault(RESULT_OUT_OF_RANGE, f"C[{i}][{j}] = {value} exceeds the XML-RPC 32-bit integer limit")


def multiplyMatrices(A, B):
    try:
        a_rows, a_cols = validate("A", A)
        b_rows, b_cols = validate("B", B)
        if a_cols != b_rows:
            raise Fault(
                INCOMPATIBLE_DIMENSIONS,
                f"cannot multiply {a_rows}x{a_cols} by {b_rows}x{b_cols}: columns of A must equal rows of B",
            )
        C = compute_product(A, B, a_rows, a_cols, b_cols)
        check_range(C)
    except Fault as fault:
        log(f"multiplyMatrices({A}, {B}) -> rejected: {fault.faultString}")
        raise
    log(f"multiplyMatrices({A}, {B}) -> {C}")
    return C


def main():
    with SimpleXMLRPCServer((HOST, PORT), logRequests=False) as server:
        server.register_function(multiplyMatrices, "multiplyMatrices")
        log(f"Matrix RPC server listening on http://{HOST}:{PORT}/")
        log("Registered: multiplyMatrices")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            log("\nMatrix RPC server shutting down")


if __name__ == "__main__":
    main()