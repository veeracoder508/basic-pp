from . import BVM
from .compiler import compile_source
import argparse


parser = argparse.ArgumentParser(
    prog="basicpp",
    usage="%(prog)s [options] <filename>",
    description="Basic++ Interpreter",
)

parser.add_argument('src_file',
                    help='the source(.bpp)/byte(.bc) code')
parser.add_argument('-v', '--verbose', 
                    action='store_const',
                    help='increase output verbosity')

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
    return BVM(run_bc(src)).run()


def cli():
    """The cli for the script
    Usage:
    >>> basicpp <filename>
    """
    file_ex = file_extension(args.src_file)

    if args.verbose:
        print(f"file_name: {args.src_file}")
        print(f"file_extension: {file_ex}")

    if file_ex == 'BPP':
        if args.verbose:
            print("===== SOURCE =====")
            print(args.src_file)
            print("===== BYTECODE =====")
            print(run_bc(args.src_file))
            print("===== OUTPUT =====")
        run_bc(args.src_file)
    elif file_ex == 'BC':
        run_bpp(args.src_file)
    else:
        raise ValueError(f"Invalid file extension: {file_ex(args.src_file)}")