import argparse
import subprocess

def prompt_if_none(value, prompt_text):
    if value is None:
        return input(prompt_text)
    return value

def run_llm(directory, model, size, gen_type):
    print(f"Running LLM fuzz evaluation with:")
    print(f"  directory={directory}, model={model}, size={size}, type={gen_type}")
    subprocess.run([
        "python", "src/scripts/llmfuzz_eval.py",
        directory,
        model,
        size,
        gen_type
    ], check=True)

def run_traditional(fuzzer,time, output_dir, yg_path='./yarpgen.out'):
    subprocess.run([
        "python", "src/scripts/tradfuzz_eval.py",
        "--fuzzer", fuzzer,
        "--timeout", time,
        "--output", output_dir,
        "--yarpgen-path", yg_path
    ], check=True)

def main():
    parser = argparse.ArgumentParser(description="Interactive CLI for fuzz evaluation")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # LLM subcommand
    parser_llm = subparsers.add_parser("llm", help="Evaluate LLM fuzzing output")
    parser_llm.add_argument("--directory", type=str, help="Directory containing C files to compile.")
    parser_llm.add_argument("--model", type=str, help="Model name.")
    parser_llm.add_argument("--size", type=str, help="Model size.")
    parser_llm.add_argument("--type", type=str, help="Type of generation (e.g. chain or single).")

    # Traditional fuzz subcommand
    parser_trad = subparsers.add_parser("traditional", help="Run traditional fuzz evaluation")
    parser_trad.add_argument("--fuzzer", type=int, help="Fuzzer ('csmith' or 'yarpgen')")
    parser_trad.add_argument("--time", type=float, help="Time of generation (in seconds)")
    parser_trad.add_argument("--output", type=str, help="Directory to store results")

    args = parser.parse_args()

    if args.mode == "llm":
        directory = prompt_if_none(args.directory, "Enter directory containing C files to compile: ")
        model = prompt_if_none(args.model, "Enter model name: ")
        size = prompt_if_none(args.size, "Enter model size: ")
        gen_type = prompt_if_none(args.type, "Enter type of generation (e.g. chain or single): ")
        run_llm(directory, model, size, gen_type)

    elif args.mode == "traditional":
        fuzzer = args.fuzzer if args.fuzzer is not None else input("Fuzzer name ('csmith' or 'yarpgen'): ")
        time_to_run = args.time if args.time is not None else float(input("Time to run in seconds:"))
        output_dir = args.output if args.output is not None else input("Enter directory to store results: ")
        yarpgen_path = './yarpgen.out'
        if fuzzer == 'yarpgen':
            yarpgen_path = input("Path to yarpgen binary(default='./yarpgen.out'): ")
        run_traditional(fuzzer,time_to_run, output_dir, yarpgen_path)

if __name__ == "__main__":
    main()
