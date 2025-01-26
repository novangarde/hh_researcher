import os
import pandas as pd

class Project_structure:
    def __init__(self):
        """Конструктор"""
        self.__data_dir = "data"
        self.__raw_dir = f'{self.__data_dir}/raw'
        self.__processed_dir = f'{self.__data_dir}/processed'
        self.__dirs = [self.raw_dir, self.processed_dir]
    
    def create_directories(self):
        """Принимает контекст экземпляра. Ничего не возвращает.
        """
        if os.path.exists("data") == False: os.mkdir("data")
        if os.path.exists("./data/raw") == False: os.mkdir("./data/raw")
        if os.path.exists("./data/processed") == False: os.mkdir("./data/processed")

    def clean_directories(self):
        """Принимает контекст экземпляра. Ничего не возвращает.
        Вызывается, чтобы очистить директории /data/raw и /data/processed от всех .csv- и .xlsx-файлов.
        """
        directories = self.dirs
        
        for dir in directories:
            files = os.listdir(dir)
            if len(files) > 0:
                for filename in files:
                    if filename.endswith('.csv') or filename.endswith('.xlsx'):
                        file_path = os.path.join(dir, filename)
                        os.remove(file_path)

    def restart_structure(self):
        """Принимает контекст экземпляра. Ничего не возвращает.
        Запускает создание директорий для данных и очистку от предыдущих данных
        """
        self.create_directories()
        self.clean_directories()
    
    def combine_files(self):
        """Функция ничего не принимает и ничего не возвращает
        Она находит все .csv-файлы в директории /data/raw и объединяет их в один .csv-файл.
        Затем она конвертирует тот же файл в .xlsx-формат"""

        csv_files = [self.raw_dir+"/" + files for files in os.listdir(self.raw_dir) if files.endswith(".csv")]
        combined_csv = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)
        combined_csv.to_csv("./data/processed/_combined.csv", index=False, encoding="utf-8-sig")
        combined_csv.to_excel("./data/processed/_combined.xlsx", index=False)

    @property
    def data_dir(self):
        return self.__data_dir
    
    @property
    def raw_dir(self):
        return self.__raw_dir
    
    @property
    def processed_dir(self):
        return self.__processed_dir
    
    @property
    def dirs(self):
        return self.__dirs
    
class Files_operations:
    test = "test"