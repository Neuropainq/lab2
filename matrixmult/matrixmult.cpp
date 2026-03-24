#include <Windows.h>
#include <omp.h>

#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

using Matrix = vector<long long>;

struct Config {
    vector<int> sizes;
    int threads = 1;
    int cores = 6;
    bool save_result = true;
};

bool fileExists(const string& path) {
    ifstream file(path);
    return file.is_open();
}

bool parseNFromAFile(const string& name, int& n) {
    if (name.size() < 7) return false;
    if (name[0] != 'A' || name[1] != '_') return false;
    if (name.substr(name.size() - 4) != ".txt") return false;

    string num = name.substr(2, name.size() - 6);
    if (num.empty()) return false;

    for (char c : num) {
        if (c < '0' || c > '9') return false;
    }

    n = stoi(num);
    return true;
}

vector<int> collectSizes(const string& base) {
    vector<int> sizes;

    WIN32_FIND_DATAA findData;
    HANDLE hFind = FindFirstFileA((base + "A_*.txt").c_str(), &findData);
    if (hFind == INVALID_HANDLE_VALUE) {
        return sizes;
    }

    do {
        int n = 0;
        if (parseNFromAFile(findData.cFileName, n)) {
            sizes.push_back(n);
        }
    } while (FindNextFileA(hFind, &findData));

    FindClose(hFind);

    sort(sizes.begin(), sizes.end());
    sizes.erase(unique(sizes.begin(), sizes.end()), sizes.end());
    return sizes;
}

string findDataBase() {
    const string bases[] = {"data/", "../data/", "../../data/", "../../../data/"};

    for (const string& base : bases) {
        if (!collectSizes(base).empty()) {
            return base;
        }
    }

    return "";
}

Matrix readMatrix(const string& path, int n) {
    ifstream in(path);
    Matrix matrix(n * n, 0);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            in >> matrix[i * n + j];
        }
    }

    return matrix;
}

void saveMatrix(const string& path, const Matrix& matrix, int n) {
    ofstream out(path);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            out << matrix[i * n + j];
            if (j + 1 < n) {
                out << ' ';
            }
        }
        out << '\n';
    }
}

Matrix transposeMatrix(const Matrix& matrix, int n) {
    Matrix transposed(n * n, 0);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            transposed[j * n + i] = matrix[i * n + j];
        }
    }

    return transposed;
}

Matrix multiplyOpenMP(const Matrix& a, const Matrix& b, int n, int threads) {
    Matrix c(n * n, 0);
    Matrix bt = transposeMatrix(b, n);

    omp_set_num_threads(threads);

    #pragma omp parallel for schedule(static)
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            long long sum = 0;
            for (int k = 0; k < n; ++k) {
                sum += a[i * n + k] * bt[j * n + k];
            }
            c[i * n + j] = sum;
        }
    }

    return c;
}

bool parseIntList(const string& text, vector<int>& values) {
    values.clear();
    string part;
    stringstream ss(text);

    while (getline(ss, part, ',')) {
        if (part.empty()) return false;
        values.push_back(stoi(part));
    }

    return !values.empty();
}

bool parseArgs(int argc, char* argv[], Config& config) {
    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];

        if (arg == "--threads" && i + 1 < argc) {
            config.threads = stoi(argv[++i]);
        } else if (arg == "--cores" && i + 1 < argc) {
            config.cores = stoi(argv[++i]);
        } else if (arg == "--sizes" && i + 1 < argc) {
            if (!parseIntList(argv[++i], config.sizes)) {
                return false;
            }
        } else if (arg == "--no-save") {
            config.save_result = false;
        } else {
            return false;
        }
    }

    return true;
}

void printUsage() {
    cout << "Usage: matrixmult [--threads N] [--cores N] [--sizes 200,400,800] [--no-save]\n";
}

int limitProcessToCores(int cores) {
    if (cores <= 0) return 0;

    DWORD_PTR processMask = 0;
    DWORD_PTR systemMask = 0;
    if (!GetProcessAffinityMask(GetCurrentProcess(), &processMask, &systemMask)) {
        return 0;
    }

    DWORD_PTR mask = 0;
    int count = 0;
    for (int bit = 0; bit < static_cast<int>(sizeof(DWORD_PTR) * 8); ++bit) {
        DWORD_PTR current = (static_cast<DWORD_PTR>(1) << bit);
        if ((systemMask & current) != 0) {
            mask |= current;
            ++count;
            if (count == cores) {
                break;
            }
        }
    }

    if (mask == 0) return 0;
    if (!SetProcessAffinityMask(GetCurrentProcess(), mask)) return 0;
    return count;
}

int main(int argc, char* argv[]) {
    Config config;
    if (!parseArgs(argc, argv, config)) {
        printUsage();
        return 1;
    }

    string base = findDataBase();
    if (base.empty()) {
        cout << "Cannot find data folder with A_*.txt files\n";
        return 1;
    }

    if (config.sizes.empty()) {
        config.sizes = collectSizes(base);
    }

    if (config.sizes.empty()) {
        cout << "No sizes available for experiment\n";
        return 1;
    }

    int actualCores = limitProcessToCores(config.cores);
    if (actualCores == 0) {
        SYSTEM_INFO info;
        GetSystemInfo(&info);
        actualCores = static_cast<int>(info.dwNumberOfProcessors);
    }

    cout << "Data folder: " << base << "\n";
    cout << "Threads: " << config.threads << " | Cores: " << actualCores << "\n";

    for (int n : config.sizes) {
        string aPath = base + "A_" + to_string(n) + ".txt";
        string bPath = base + "B_" + to_string(n) + ".txt";
        string cPath = base + "C_" + to_string(n) + ".txt";

        if (!fileExists(aPath) || !fileExists(bPath)) {
            cout << "Skip N=" << n << " (missing A or B file)\n";
            continue;
        }

        Matrix a = readMatrix(aPath, n);
        Matrix b = readMatrix(bPath, n);

        auto start = chrono::high_resolution_clock::now();
        Matrix c = multiplyOpenMP(a, b, n, config.threads);
        auto end = chrono::high_resolution_clock::now();

        if (config.save_result) {
            saveMatrix(cPath, c, n);
        }

        auto ms = chrono::duration_cast<chrono::milliseconds>(end - start).count();
        long long ops = 2LL * n * n * n;

        cout << "N=" << n
             << " | Threads: " << config.threads
             << " | Cores: " << actualCores
             << " | Time: " << ms << " ms"
             << " | Task volume: " << ops << " operations";

        if (config.save_result) {
            cout << " | Saved: " << cPath;
        }

        cout << "\n";
    }

    return 0;
}
