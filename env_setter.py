import os
import zipfile
import requests as req

def set_env(path):
    os.chdir(path)

    url = 'https://api.github.com/repos/jingooo5/hardhat-dev-settings/zipball/latest'
    file = req.get(url, allow_redirects=True)

    with open("setting.zip", 'wb') as setting:
        setting.write(file.content)
        # for chunk in file.iter_content(chunk_size=2048):
        #     if chunk:
        #         setting.write(chunk)

    with zipfile.ZipFile("setting.zip", 'r') as zip_ref:
        zip_ref.extractall("./")

    os.remove("./setting.zip")

    folder = os.listdir()[0]
    print(folder)
    os.chdir(folder)

    for file in os.scandir():
        os.replace(file.name, "../"+file.name)

    os.chdir("../")
    os.rmdir(folder)
    os.system("npm i")

def scan_dir():
    for file in os.scandir():
        print(file.name)

#scan_dir()
set_env('/Users/user/Desktop/curl')