from pathlib import Path

output_dir = Path("output")

output_dir.mkdir(parents=True, exist_ok=True)

file_name = "results.txt"

def saveFile(content:str, filename:str):
    file_path = output_dir / filename
    print(f"Saving file to {file_path}")
    with open(file_path, 'w',encoding="utf-8") as f:
        f.write(str(content))
    