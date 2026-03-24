from pathlib import Path
import numpy as np


def generate_matrix(size, low=0, high=100):
    matrix_a = np.random.randint(low, high, (size, size))
    matrix_b = np.random.randint(low, high, (size, size))
    return matrix_a, matrix_b



def save_matrix(matrix, filepath):
    np.savetxt(filepath, matrix, fmt="%d")


def main():
    sizes = [200, 400, 800, 1200, 1600, 2000]

    matrix_path = Path("data")
    matrix_path.mkdir(exist_ok=True)


    for size in sizes:
        matrix_a, matrix_b = generate_matrix(size)

        save_path_a = matrix_path / f'A_{size}.txt'
        save_path_b = matrix_path / f'B_{size}.txt'

        save_matrix(matrix_a, save_path_a)
        save_matrix(matrix_b, save_path_b)



if __name__ == "__main__":
    main()
