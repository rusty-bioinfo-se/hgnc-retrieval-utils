import logging
import os


def check_infile_status(
    infile: str = None, 
    extension: str = None
) -> None:
    """Check if the file exists, if it is a regular file and whether it has content.

    Args:
        infile (str): the file to be checked

    Raises:
        None
    """
    
    error_ctr = 0
    
    if infile is None or infile == '':
        logging.error(f"'{infile}' is not defined")
        error_ctr += 1
    else:
        if not os.path.exists(infile):
            error_ctr += 1
            logging.error(f"'{infile}' does not exist")
        else:
            if not os.path.isfile(infile):
                error_ctr += 1
                logging.error(f"'{infile}' is not a regular file") 
            if os.stat(infile).st_size == 0:
                logging.error(f"'{infile}' has no content")
                error_ctr += 1
            if extension is not None and not infile.endswith(extension):
                logging.error(f"'{infile}' does not have filename extension '{extension}'")
                error_ctr += 1

    if error_ctr > 0:
        raise Exception(f"Detected problems with input file '{infile}'")
