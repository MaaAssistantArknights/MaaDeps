import sys
import os

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "pefile.zip")
sys.path.insert(0, basedir)

def find_pdb_file(filename):
    # type: (str) -> bytes | None
    import pefile
    pe = pefile.PE(filename, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DEBUG']])
    for entry_record in pe.DIRECTORY_ENTRY_DEBUG:
        if entry_record.struct.Type == pefile.DEBUG_TYPE['IMAGE_DEBUG_TYPE_CODEVIEW']:
            return entry_record.entry.PdbFileName[:-1] 
    return None

if __name__ == "__main__":
    print(find_pdb_file(sys.argv[1]).decode('utf-8'))
