import os
import subprocess
import glob
import shutil
import concurrent.futures
import json

class PoManager:

    __base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))

    __excluded_yaml_files = []
    __html_files = []

    __max_workers = None

    def __init__(self):
        __config_file_name = "{}/config/l10n-utils.json".format(self.__base_dir)
        with open(__config_file_name) as file:
            __config = json.load(file)
            self.__target_lang = __config["targetLang"]
            self.__excluded_yaml_files = __config["sourceSets"]["yaml"]["exclude"]
            self.__html_files = __config["sourceSets"]["html"]


    def update_po(self):
        self.update_adoc_po_files()
        self.update_md_po_files()
        self.update_yaml_po_files()
        self.update_html_po_files()
        self.normalize()

    def translate_po(self):
        # memo: .adoc files are no longer translated with po4a.
        # It is translated with `doc-l10n-kit/asciidoctor-l10n` asciidoctor extension
        self.translate_md_po_files()
        self.translate_yaml_po_files()
        self.translate_html_po_files()

    def remove_obsolete_po(self):
        po_file_paths = glob.glob("l10n/po/**/*.po", recursive=True)
        relative_file_paths = [os.path.relpath(po_file_path, self.__base_dir + "/l10n/po/" + self.__target_lang) for po_file_path in po_file_paths if os.path.isdir(po_file_path) == False]
        for relative_file_path in relative_file_paths:
            original_file_path = self.__base_dir + "/upstream/" + os.path.splitext(relative_file_path)[0]
            po_file_path = self.__base_dir + "/l10n/po/" + self.__target_lang + "/" + relative_file_path
            if os.path.exists(original_file_path) == False:
                print("remove obsolete po file: " + po_file_path)
                os.remove(po_file_path)

    def normalize(self):
        file_paths = glob.glob("l10n/po/**/*.po".format(self.__target_lang), recursive=True)
        file_paths = [ file_path for file_path in file_paths if os.path.isdir(file_path) == False ]
        concurrent.futures.ThreadPoolExecutor(thread_name_prefix="worker", max_workers=self.__max_workers).map(self.__normalize, file_paths)

    def __normalize(self, file_path):
        print("Processing: {}".format(file_path))
        subprocess.run("sed -e '/^#|/d' {} -i".format(file_path), shell=True, check=True)
        subprocess.run("msgcat --to-code=utf-8 --lang={} --no-wrap -o {} {}".format(self.__target_lang, file_path, file_path), shell=True, check=True)

    def update_adoc_po_files(self):
        if os.path.exists("{}/build/jekyll-source".format(self.__base_dir)):
            shutil.rmtree("{}/build/jekyll-source".format(self.__base_dir))
        shutil.copytree("{}/upstream".format(self.__base_dir), "{}/build/jekyll-source".format(self.__base_dir))
        subprocess.run("cd {}/build/jekyll-source; bundle config set --local path {}/vendor/bundle".format(self.__base_dir, self.__base_dir), shell=True, check=True)
        subprocess.run("cd {}/build/jekyll-source; bundle install".format(self.__base_dir), shell=True, check=True)
        returncode = subprocess.run("cd {}/build/jekyll-source; bundle list | grep jekyll-l10n".format(self.__base_dir), shell=True, check=False).returncode
        if returncode != 0:
            subprocess.run("cd {}/build/jekyll-source; bundle add 'jekyll-l10n' --group jekyll_plugins --git https://github.com/doc-l10n-kit/asciidoctor-l10n --branch main".format(self.__base_dir), shell=True, check=True)
        subprocess.run("cd {}/build/jekyll-source; L10N_MODE=update_po L10N_PO_BASE_DIR={}/l10n/po/{} bundle exec jekyll build -d {}/docs/ --config _config.yml".format(self.__base_dir, self.__base_dir, self.__target_lang, self.__base_dir), shell=True, check=True)

    def update_md_po_files(self):
        items = glob.glob("upstream/**/*.md", recursive=True)
        relative_file_paths = [os.path.relpath(item, self.__base_dir + "/upstream") for item in items if os.path.isdir(item) == False]
        relative_file_paths = [ relative_file_path for relative_file_path in relative_file_paths]
        executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="worker", max_workers=self.__max_workers)
        futures = executor.map(self.__update_md_po_file, relative_file_paths)
        executor.shutdown(wait=True)
        for _ in futures:
            pass

    def update_yaml_po_files(self):
        items = glob.glob("upstream/**/*.yaml", recursive=True)
        relative_file_paths = [os.path.relpath(item, self.__base_dir + "/upstream") for item in items if os.path.isdir(item) == False]
        relative_file_paths = [relative_file_path for relative_file_path in relative_file_paths if ((relative_file_path in self.__excluded_yaml_files) == False)]
        executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="worker", max_workers=self.__max_workers)
        futures = executor.map(self.__update_yaml_po_file, relative_file_paths)
        executor.shutdown(wait=True)
        for _ in futures:
            pass


    def update_html_po_files(self):
        relative_file_paths = self.__html_files
        relative_file_paths = [ relative_file_path for relative_file_path in relative_file_paths ]
        executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="worker", max_workers=self.__max_workers)
        futures = executor.map(self.__update_html_po_file, relative_file_paths)
        executor.shutdown(wait=True)
        for _ in futures:
            pass

#     def mk_output_dir(self):
#         upstream = "{}/upstream".format(self.__base_dir)
#         output_dir = "{}/build/jekyll-source/{}".format(self.__base_dir, self.__target_lang)
#         shutil.rmtree(output_dir, ignore_errors=True)
#         os.makedirs("{}/build/jekyll-source".format(self.__base_dir), exist_ok=True)
#         shutil.copytree(upstream, output_dir)

    def translate_md_po_files(self):
        items = glob.glob("upstream/**/*.md", recursive=True)
        relative_file_paths = [os.path.relpath(item, self.__base_dir + "/upstream") for item in items if os.path.isdir(item) == False]
        relative_file_paths = [ relative_file_path for relative_file_path in relative_file_paths]
        executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="worker", max_workers=self.__max_workers)
        futures = executor.map(self.__translate_md_po_files, relative_file_paths)
        executor.shutdown(wait=True)
        for _ in futures:
            pass


    def translate_yaml_po_files(self):
        items = glob.glob("upstream/**/*.yaml", recursive=True)
        relative_file_paths = [os.path.relpath(item, self.__base_dir + "/upstream") for item in items if os.path.isdir(item) == False]
        relative_file_paths = [relative_file_path for relative_file_path in relative_file_paths if ((relative_file_path in self.__excluded_yaml_files) == False)]
        executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="worker", max_workers=self.__max_workers)
        futures = executor.map(self.__translate_yaml_po_file, relative_file_paths)
        executor.shutdown(wait=True)
        for _ in futures:
            pass

    def translate_html_po_files(self):
        relative_file_paths = self.__html_files
        relative_file_paths = [ relative_file_path for relative_file_path in relative_file_paths]
        executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="worker", max_workers=self.__max_workers)
        futures = executor.map(self.__translate_html_po_files, relative_file_paths)
        executor.shutdown(wait=True)
        for _ in futures:
            pass


    def __update_md_po_file(self, relative_file_path):
        print("Processing: {}".format(relative_file_path))
        relative_file_dir = os.path.dirname(relative_file_path)
        os.makedirs("{}/l10n/po/{}/{}".format(self.__base_dir, self.__target_lang, relative_file_dir), exist_ok=True)
        subprocess.run("PERLLIB=vendor/po4a/lib vendor/po4a/po4a-updatepo --msgmerge-opt --no-fuzzy-matching --master-charset UTF-8 -f text -o markdown -o neverwrap --master upstream/{} --po l10n/po/{}/{}.po".format(relative_file_path, self.__target_lang, relative_file_path), shell=True, check=True)
        subprocess.run("msgcat --to-code=utf-8 --no-wrap -o l10n/po/{}/{}.po l10n/po/{}/{}.po".format(self.__target_lang, relative_file_path, self.__target_lang, relative_file_path), shell=True, check=True)

    def __update_yaml_po_file(self, relative_file_path):
        print("Processing: {}".format(relative_file_path))
        relative_file_dir = os.path.dirname(relative_file_path)
        os.makedirs("{}/l10n/po/{}/{}".format(self.__base_dir, self.__target_lang, relative_file_dir), exist_ok=True)
        upstream_file_path = "upstream/{}".format(relative_file_path)
        if os.path.exists(upstream_file_path):
            subprocess.run("PERLLIB=vendor/po4a/lib vendor/po4a/po4a-updatepo --msgmerge-opt --no-fuzzy-matching --master-charset UTF-8 -f yaml --master {} --po l10n/po/{}/{}.po".format(upstream_file_path, self.__target_lang, relative_file_path), shell=True, check=True)
            subprocess.run("msgcat --to-code=utf-8 --no-wrap -o l10n/po/{}/{}.po l10n/po/{}/{}.po".format(self.__target_lang, relative_file_path, self.__target_lang, relative_file_path), shell=True, check=True)
        else:
            print("Skip: {} since upstream file is missing".format(relative_file_path))


    def __update_html_po_file(self, relative_file_path):
        print("Processing: {}".format(relative_file_path))
        relative_file_dir = os.path.dirname(relative_file_path)
        os.makedirs("{}/l10n/po/{}/{}".format(self.__base_dir, self.__target_lang, relative_file_dir), exist_ok=True)
        upstream_file_path = "upstream/{}".format(relative_file_path)
        if os.path.exists(upstream_file_path):
            subprocess.run("PERLLIB=vendor/po4a/lib vendor/po4a/po4a-updatepo --msgmerge-opt --no-fuzzy-matching --master-charset UTF-8 -f xhtml --master {} --po l10n/po/{}/{}.po".format(upstream_file_path, self.__target_lang, relative_file_path), shell=True, check=True)
            subprocess.run("msgcat --to-code=utf-8 --no-wrap -o l10n/po/{}/{}.po l10n/po/{}/{}.po".format(self.__target_lang, relative_file_path, self.__target_lang, relative_file_path), shell=True, check=True)
        else:
            print("Skip: {} since upstream file is missing".format(relative_file_path))


    def __translate_md_po_files(self, relative_file_path):
        print("Processing: {}".format(relative_file_path))
        subprocess.run("PERLLIB=vendor/po4a/lib vendor/po4a/po4a-translate --master-charset UTF-8 --localized-charset UTF-8 -f text -o markdown -o neverwrap --keep 0 --master upstream/{} --localized build/jekyll-source/{} --po l10n/po/{}/{}.po".format(relative_file_path, relative_file_path, self.__target_lang, relative_file_path), shell=True, check=True)

    def __translate_yaml_po_file(self, relative_file_path):
        print("Processing: {}".format(relative_file_path))
        upstream_file_path = "upstream/{}".format(relative_file_path)
        if os.path.exists(upstream_file_path):
            subprocess.run("PERLLIB=vendor/po4a/lib vendor/po4a/po4a-translate --master-charset UTF-8 --localized-charset UTF-8 -f yaml --keep 0 --master upstream/{} --localized build/jekyll-source/{} --po l10n/po/{}/{}.po".format(relative_file_path, relative_file_path, self.__target_lang, relative_file_path), shell=True, check=True)
        else:
            print("Skip: {} since upstream file is missing".format(relative_file_path))


    def __translate_html_po_files(self, relative_file_path):
        print("Processing: {}".format(relative_file_path))
        upstream_file_path = "upstream/{}".format(relative_file_path)
        if os.path.exists(upstream_file_path):
            subprocess.run("PERLLIB=vendor/po4a/lib vendor/po4a/po4a-translate --master-charset UTF-8 --localized-charset UTF-8 -f xhtml --keep 0 --master {} --localized build/jekyll-source/{} --po l10n/po/{}/{}.po".format(upstream_file_path, relative_file_path, self.__target_lang, relative_file_path), shell=True, check=True)
        else:
            print("Skip: {} since upstream file is missing".format(relative_file_path))
