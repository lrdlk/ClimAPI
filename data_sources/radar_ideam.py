import subprocess
import re
from pathlib import Path


BUCKET = "s3://s3-radaresideam/"
RADAR_CODE = "RDSA"   # Santa Elena


def aws_s3_ls(prefix=""):
    """Run `aws s3 ls` with no-sign-request and return raw output."""
    cmd = ["aws", "s3", "ls", "--no-sign-request", BUCKET + prefix]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Error running AWS CLI: {result.stderr}")

    return result.stdout


def list_santa_elena_files():
    """List all Santa Elena radar files (RDSA)."""
    output = aws_s3_ls()
    lines = output.splitlines()

    files = []
    pattern = re.compile(rf".*({RADAR_CODE}.*)")
    
    for line in lines:
        match = pattern.search(line)
        if match:
            files.append(match.group(1))

    return sorted(files)


def download_file(filename, output_folder="downloads"):
    """Download a selected Santa Elena file."""
    Path(output_folder).mkdir(exist_ok=True)

    cmd = [
        "aws", "s3", "cp",
        "--no-sign-request",
        BUCKET + filename,
        str(Path(output_folder) / filename)
    ]

    print(f"Downloading: {filename}")
    subprocess.run(cmd, check=True)
    print("Done!")


if __name__ == "__main__":
    print("📡 Listando archivos del radar Santa Elena (RDSA)...\n")

    files = list_santa_elena_files()

    if not files:
        print("No se encontraron archivos RDSA.")
        exit()

    print("\n".join(files[:20]))  # Muestra los primeros 20 encontrados

    latest = files[-1]
    print(f"\n📥 Archivo más reciente: {latest}")

    # Descargar el archivo más reciente
    download_file(latest)
