import os
import sys
import glob
import time
import random
import string
import shutil
import subprocess
import argparse
import pandas as pd

GCC_VERSION = '11'
YARPGEN_PATH = './yarpgen.out'

class GenerationPipeline:
    def __init__(self, output_dir_base: str, fuzzer="yarpgen"):
        self.output_dir_base = output_dir_base
        self.totalTime = 0
        self.totalTries = 0
        self.failures = 0
        self.success = 0
        self.regressions = 0
        self.first_regression_time = 0
        self.fuzzer = fuzzer

    def yarpgen_program(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        print("[*] Generating program with YARPGen...")
        result = subprocess.run([YARPGEN_PATH, "--std=c", f"--out-dir={output_dir}"])
        if result.returncode != 0:
            print("[!] YARPGen failed")
            sys.exit(1)
        print("[*] YARPGen program generated successfully")

    def csmith_program(self, output_dir: str, source: str):
        os.makedirs(output_dir, exist_ok=True)
        print("[*] Generating program with Csmith...")
        with open(f"{output_dir}/{source}.c", "w") as output_file:
            result = subprocess.run(["csmith"], stdout=output_file)
        if result.returncode != 0:
            print("[!] Csmith failed")
            sys.exit(1)
        print("[*] Csmith program generated successfully")

    def compile_program(self, source_dir: str, out_dir: str, out_file: str):
        os.makedirs(out_dir, exist_ok=True)
        opt_flags = ['-O0', '-O1', '-O2', '-O3', '-Os', '-Ofast']
        print("[*] Compiling the program...")
        c_files = glob.glob(f"{source_dir}/*.c")
        for opt_flag in opt_flags:
            result = subprocess.run([
                f"gcc-{GCC_VERSION}", opt_flag, *c_files,
                f'-I{source_dir}', "-o", f'{out_dir}/{out_file}{opt_flag}.out'
            ])
            if result.returncode != 0:
                print("[!] Compilation failed")
                self.failures += 1
                return False
        self.success += 1
        return True

    def folder_generator(self, size=4):
        chars = string.ascii_uppercase
        while True:
            random_name = ''.join(random.choice(chars) for _ in range(size))
            folder_path = os.path.join(self.output_dir_base, random_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                return folder_path, random_name

    def get_binary_size(self, file_path):
        if not os.path.exists(file_path):
            return 0
        result = subprocess.run(['size', file_path], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        if len(lines) < 2:
            return 0
        return int(lines[1].split()[0])

    def verify_regression(self, binary_dir: str, binary_file: str) -> bool:
        if not os.path.exists(binary_dir):
            print(f"Directory {binary_dir} does not exist.")
            return False

        opt_flags = ['-O0', '-O1', '-O2', '-O3', '-Os', '-Ofast']
        sizes = {}
        for opt_flag in opt_flags:
            binary_path = os.path.join(binary_dir, f"{binary_file}{opt_flag}.out")
            sizes[opt_flag] = self.get_binary_size(binary_path)
            print(f"Binary size for {opt_flag}: {sizes[opt_flag]} bytes")

        for opt_flag in opt_flags:
            if opt_flag != '-Os' and sizes['-Os'] - sizes[opt_flag] > 32:
                return True
        return False

    def generate(self):
        start_time = time.time()
        self.totalTries += 1
        folder_path, random_name = self.folder_generator()

        match self.fuzzer:
            case "yarpgen":
                self.yarpgen_program(folder_path)
            case "csmith":
                self.csmith_program(folder_path, random_name)

        compiled = self.compile_program(folder_path, folder_path, random_name)
        regression = False

        if not compiled:
            shutil.rmtree(folder_path)
        else:
            regression = self.verify_regression(folder_path, random_name)
            if regression:
                self.regressions += 1
                if self.first_regression_time == 0:
                    self.first_regression_time = time.time() - start_time
                print(f"[!] Regression detected in {folder_path}")
            else:
                shutil.rmtree(folder_path)

        elapsed = time.time() - start_time
        self.totalTime += elapsed
        return regression, elapsed, self.totalTime

    def print_status(self):
        print(f"Total time: {self.totalTime:.2f}s")
        print(f"Failures: {self.failures}")
        print(f"Success: {self.success}")
        print(f"Regressions: {self.regressions}")
        if self.regressions > 0:
            print(f"First regression time: {self.first_regression_time:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Run traditional fuzzer evaluation (YARPGen or Csmith).")
    parser.add_argument("--fuzzer", choices=["yarpgen", "csmith"], required=True, help="Choose the fuzzer to run.")
    parser.add_argument("--timeout", type=float, default=10800.0, help="Total runtime in seconds (default: 3 hours).")
    parser.add_argument("--output-dir", type=str, default="", help="Base output directory.")
    parser.add_argument("--yarpgen-path", type=str, default="./yarpgen.out", help="Yarpgen binary path")
    args = parser.parse_args()

    output_dir = os.path.join(args.output_dir, args.fuzzer)
    os.makedirs(output_dir, exist_ok=True)
    pipeline = GenerationPipeline(output_dir, fuzzer=args.fuzzer)

    while pipeline.totalTime < args.timeout:
        pipeline.generate()

    df = pd.DataFrame({
        'fuzzer': pipeline.fuzzer,
        'total_tries': pipeline.totalTries,
        'total_time': pipeline.totalTime,
        'failures': pipeline.failures,
        'success': pipeline.success,
        'regressions': pipeline.regressions,
        'first_regression_time': pipeline.first_regression_time
    }, index=[0])

    df.to_csv(os.path.join(output_dir, "results.csv"), index=False)
    pipeline.print_status()


if __name__ == "__main__":
    main()
