from system_fixer.program_fetcher import write_programs_json

def refresh_programs():
    write_programs_json("programs.json")

if __name__ == "__main__":
    refresh_programs()
