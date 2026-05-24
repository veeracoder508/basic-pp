from . import BVM
from .compiler import compile_source
from .compiler.ast_a import write_bytecode_to_file
import argparse
import os
from pprint import pprint

parser = argparse.ArgumentParser(
    prog="basicpp",
    usage="%(prog)s [options] <filename>",
    description="Basic++ Interpreter",
)

parser.add_argument('src_file',
                    help='the source(.bpp)/byte(.bc) code')
parser.add_argument('-v', '--verbose', 
                    action='store_const',
                    dest='verbose',
                    const=True,
                    help='increase output verbosity')
parser.add_argument('-b',
                    action='store_const',
                    const=True,
                    dest='bytecode',
                    help='display the byte code.')
parser.add_argument('--bc', '--write-bc',
                    action='store_const',
                    const=True,
                    dest='write_bc',
                    help='write the byte code to a file.')

args = parser.parse_args()

def file_extension(filename: str) -> str:
    if filename.endswith('.bpp'):
        return 'BPP'
    elif filename.endswith('.bc'):
        return 'BC'
    else:
        return filename.split('.')[-1]
    
def run_bc(src: str) -> str:
    return compile_source(src)

def run_bpp(src: str) -> None:
    return BVM(compile_source(src)).run()

def disp_bytecode(src: str) -> str:
    return compile_source(src)


def cli():
    """The cli for the script
    Usage:
    >>> basicpp <filename> [option]
    """
    if not os.path.exists(args.src_file):
        print(f"Error: File '{args.src_file}' not found.")
        return

    with open(args.src_file, 'r', encoding='utf-8') as f:
        content = f.read()

    file_ex = file_extension(args.src_file)

    if args.verbose:
        print("===== ARGS =====")
        print(f"file_name: {args.src_file}")
        print(f"file_extension: {file_ex}")
        print("================")

    if args.bytecode:
        pprint(disp_bytecode(content))
        return
    
    if args.write_bc:
        write_bytecode_to_file(file_name=f"{args.src_file.split('.')[0]}.bc", content=run_bc(content))
        return

    if file_ex == 'BPP':
        if args.verbose:
            print("===== SOURCE =====")
            print(content)
            print("===== BYTECODE =====")
            pprint(run_bc(content))
            print("===== OUTPUT =====")
        run_bpp(content)
    elif file_ex == 'BC':
        # Currently, the VM expects a bytecode dictionary. 
        # If .bc files are raw source, we run them; otherwise, a loader is needed.
        run_bpp(content)
    else:
        raise ValueError(f"Invalid file extension: {file_ex}")
