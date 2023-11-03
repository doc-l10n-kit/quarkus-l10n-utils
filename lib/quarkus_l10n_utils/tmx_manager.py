import os
import xml.etree.ElementTree as ET
import json
import tempfile
import pathlib
import glob
import concurrent.futures
import subprocess

class TmxManager:

    __base_dir = os.path.join(os.path.dirname(__file__), "../../../../")

    __tmx_file_path = "l10n/tmx/quarkus.tmx"

    def __init__(self):
        __config_file_name = "{}/config/l10n-utils.json".format(self.__base_dir)
        with open(__config_file_name) as file:
            __config = json.load(file)
            self.__target_lang = __config["targetLang"]
            self.__tmx_file_path = __config["tmx"]["filePath"]


    def sort(self):

        dom = ET.parse(self.__tmx_file_path)
        body = dom.getroot().find('body')

        body[:] = sorted(body, key=lambda tu: tu.find('tuv/seg').text)
        dom.write(self.__tmx_file_path, encoding="UTF-8")

    def update(self):
        os.makedirs("{}/l10n/tmx".format(self.__base_dir), exist_ok=True)
        tempdir = tempfile.mkdtemp()
        pathlib.Path("{}/accumulation.po".format(tempdir)).touch()
        items = glob.glob("l10n/po/**/*.po", recursive=True)
        file_paths = [item for item in items if os.path.isdir(item) == False]
        executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="worker")
        executor.map(lambda file_path : self.__apply_po_filter(tempdir, file_path), file_paths)
        executor.shutdown(wait=True)
        print("Generating {}".format(self.__tmx_file_path))
        subprocess.run("find {}/l10n/po -name \"*.po\" | xargs msgcat --force-po --to-code=utf-8 --no-wrap --use-first -o {}/accumulation.po -i {}/accumulation.po".format(self.__base_dir, tempdir, tempdir), shell=True, check=True)
        subprocess.run("grep -v \"^#~\" {}/accumulation.po > {}/comment-filtered.po".format(tempdir, tempdir), shell=True, check=True)
        subprocess.run("po2tmx -l {} -i {}/comment-filtered.po -o {}".format(self.__target_lang, tempdir, self.__tmx_file_path), shell=True, check=True)
        self.sort()

    def __apply_po_filter(self, tempdir, file_path):
        print("Processing: {}".format(file_path))
        parent_dir = os.path.dirname("{}/{}".format(tempdir, file_path))
        os.makedirs(parent_dir, exist_ok=True)
        subprocess.run("pofilter --nonotes --nofuzzy --excludefilter=untranslated -i {} -o {}/{}".format(file_path, tempdir, file_path), shell=True, check=True)
        pathlib.Path("{}/{}".format(tempdir, file_path)).touch()

