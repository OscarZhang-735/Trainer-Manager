import utils
import shutil
import os


def project_copy(full=False):
    print("Copying project...")
    shutil.copytree(".\\resources", r"D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager-Copy\resources")
    shutil.copy("main.py", r"D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager-Copy\main.py")
    shutil.copy("utils.py", r"D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager-Copy\utils.py")
    shutil.copy("crawler.py", r"D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager-Copy\crawler.py")
    shutil.copytree(".\\venv", r"D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager-Copy\venv")
    if full:
        shutil.copy(".\\data\\data.json", r"D:\PyCharm 2023.3.4\PyCharm Projects\TrainerManager-Copy\data\data.json")
    print("Done.")


def pack_up():
    try:
        shutil.rmtree("./build")
        shutil.rmtree("./dist")
    except FileNotFoundError:
        pass
    print("Cache cleared.")
    os.system("pyinstaller main.spec")
    print("The executable file generated successfully.")
    print("Copying dependencies...")
    shutil.copytree("resources", f"dist\\{utils.PROGRAM_NAME}\\resources")
    shutil.copytree("data", f"dist\\{utils.PROGRAM_NAME}\\data")
    shutil.copytree("trainers", f"dist\\{utils.PROGRAM_NAME}\\trainers")
    os.makedirs(f"dist\\{utils.PROGRAM_NAME}\\games", exist_ok=True)
    os.makedirs(f"dist\\{utils.PROGRAM_NAME}\\patches", exist_ok=True)
    print("Dependencies copied successfully.")



if __name__ == '__main__':
    # utils.Help.report("Report Test", "This is an SMTP test", "2024-06-11")
    # queryObj = crawler.Spider.NekoNyanPatchSearch()
    # project_copy()
    pack_up()
