import requests
import shutil
import os

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download&confirm=1"

    session = requests.Session()

    response = session.get(URL, params={"id": id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

def extract_images_folder(file_gdrive_id):
    download_file_from_google_drive(file_gdrive_id, 'my_test.zip')
    shutil.unpack_archive('my_test.zip', 'my_test')
    dir_list = os.listdir('my_test')
    if dir_list:
        return os.path.join('my_test', dir_list[0])
