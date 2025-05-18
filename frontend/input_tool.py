"""
Handles user input.
"""
import sys
import logging
import argparse
import os
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGE = ["it", "en"]

def get_path(path: str) -> Path:
    """Get a file path if it exists.

    Arguments:
        path: The path to the file to convert.
    """
    if not os.path.exists(path):
        logger.error("file to read %s does not exist", path)
        sys.exit(1)
    return Path(path)

def get_sys_input(main_path:str, format_output:str="m4b") -> tuple[str, str, str]:
    """Get input and output path files.

    Arguments:
        main_path: The path of the script that calls this function.
        format_output: The format to save the result file as.

    Returns:
        result: A tuple that comprises the path to the file to convert, the path to save the converted file to, and the language abbreviation of the converted audio file.
    """
    argparser = argparse.ArgumentParser(
            usage='usage: %(prog)s <input.docx> <language>',
            prog=sys.argv[0])
    argparser.add_argument('file',
            default=None,
            help='file to be read',
            type=get_path)
    argparser.add_argument('language',
            nargs='?', default="it",
            choices=SUPPORTED_LANGUAGE,
            help='language used by TTS backend')
    argparser.add_argument('--verbose',
            action='store_true', dest='verbose',
            help=('DEBUG mode.'))
    args = argparser.parse_args()
    output_file_name = args.file.stem
    output_file_path = os.path.join(main_path,
                                    output_file_name) + f".{format_output}"
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    logger.debug("%s: read %s language: %s", sys.argv[0],
                 args.file, args.language)
    return args.file, output_file_path, args.language
