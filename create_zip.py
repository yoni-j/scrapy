import json
from zipfile import ZipFile
from datetime import datetime


def create_zip():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Get current timestamp in the format: YYYYMMDDHHMMSS
    zip_file_name = f'function_file_{timestamp}.zip'     # Append the timestamp to the ZIP file name

    zipObj = ZipFile(zip_file_name, 'w')
    files_to_include = ["main.py", "data_service.py", "vendors.py", "requirements.txt"]
    for file in files_to_include:
        zipObj.write(file)
    zipObj.close()

    return zip_file_name  # Return the generated ZIP file name


if __name__ == "__main__":
    generated_zip_file = create_zip()
    result = {"zip_file_name": generated_zip_file}
    print("created")
    print(json.dumps(result))
