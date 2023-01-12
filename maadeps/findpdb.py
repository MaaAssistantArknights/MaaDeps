import sys
import os

def find_pdb_file(filename):
    # type: (str) -> bytes | None
    from .vendor import pefile
    pe = pefile.PE(filename, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DEBUG']])
    for entry_record in pe.DIRECTORY_ENTRY_DEBUG:
        if entry_record.struct.Type == pefile.DEBUG_TYPE['IMAGE_DEBUG_TYPE_CODEVIEW']:
            return entry_record.entry.PdbFileName[:-1] 
    return None

if __name__ == "__main__":
    print(find_pdb_file(sys.argv[1]).decode('utf-8'))
