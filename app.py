from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import zipfile
import shutil
from datetime import datetime
from sqlalchemy import text

from sqlalchemy import text

app = Flask(__name__)

db = SQLAlchemy()


@app.route('/backup', methods=["POST", "GET"])
def backup():
    filename = zip_up()
    return filename


@app.route("/backups/get/five", methods=["POST"])
def five_backups():
    limit_five_items = run("SELECT * FROM sys_back ORDER BY date_added DESC LIMIT 5")
    return limit_five_items


@app.route("/backups/get/all", methods=["GET"])
def all_backups():
    return run(f"SELECT * FROM sys_back")


def to_json(filename, data):
    with open(filename, "w") as f:
        f.write(str(data))
        return True


def zip_up():
    now = datetime.now()
    if prep_up():
        export_db_file()
        # move_db_file to a location
        import shutil
        shutil.move("wambuine_cargen.bak.sql","../support/wambuine_cargen.bak.sql")
        shutil.move("user_logins.bak.sql","../support/user_logins.bak.sql")

        formatted_date = datetime.strftime(now, '%Y_%m_%d %H_%M_%S')
        filename = f"bckup_{formatted_date}"
        final_path = os.path.join(os.getcwd(), "Backups", filename)
        zipf = zipfile.ZipFile(f"{final_path}.zip", 'w', zipfile.ZIP_DEFLATED)
        # move on dir down
        os.chdir("..")
        support = os.path.join(os.getcwd(), "support")
        zip(support, zipf)
        zipf.close()
        # move path up back to backups
        os.chdir("backups")
        filesize = os.path.getsize(final_path)
        # make json file with a list of all file inf the dir
        to_json(f"{final_path}.json", zipf.filelist)
        # INSERT INTO sys_back VALUES(NULL,:name,NULL,:size,:status)
        add_data = run(f"INSERT INTO sys_back VALUES(NULL,{filename},NULL,{filesize},1)")

        # ["res" => 1111,"filename" => $folder_name,"filesize" => $size, "affectRows" => $final]
        final = {"res": 1111, "filename": zipf.filename, "filesize": filesize, "affectedRows": None}
    else:
        final = {"res": 2222}
    return final


def update_backup_dir(filename):
    return os.mkdir(os.path.join(os.getcwd(), "Backups", filename))


def export_db_file():
    os.system("mysqldump --add-drop-table -c -u root -pDevs2019c!?__ wambuine_cargen > wambuine_cargen.bak.sql")
    os.system("mysqldump --add-drop-table -c -u root -pDevs2019c!?__ user_logins > user_logins.bak.sql")
    return True


def run(sql):
    sql = text(sql)
    result = db.engine.execute(sql)
    names = [row[0] for row in result]
    return names


def prep_up():
    dir = os.path.join(os.getcwd(), "Backups")
    exists_dir = os.path.exists(dir)
    final_dir = dir if exists_dir else os.mkdir(dir)
    return final_dir


def zip(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def zip_option(output_filename, dir_name):
    shutil.make_archive(output_filename, 'zip', dir_name)


if __name__ == '__main__':
    app.run(port=8000)
