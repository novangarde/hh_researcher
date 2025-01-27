import sys
import src.config
import src.parser
import src.analizer
from src.files_handler import Project_structure

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "":
        raise Exception('Передайте в аргумент ключевые слова для сбора данных о вакансии:\n\nПример 1: python3 researcher.py Программист\nПример 2: python3 researcher.py "Водитель такси"\nПример 3: python3 researcher.py "[Data scientist, Data analyst, Data engineer]"\nПример 4: python3 researcher.py keywords_list.txt\n\nПодробнее в README.md')

    config = src.config.Config()
    ps = Project_structure()
    parser = src.parser.Parser(sys.argv[1], config, ps)
    stats = src.analizer.Analizer()

    ps.restart_structure()

    print("Загружаем настройки поиска...\n")
    if config.experience: print(f'Опыт работы: {config.experience}')
    if config.employment: print(f'Тип занятости: {config.employment}')
    if config.schedule: print(f'График работы: {config.schedule}')
    print("Область поиска: "+config.country, config.region, config.city+"\n") 

    print("Начинаем парсинг...")
    parser.collect_vacancies()
    ps.combine_files()
    print("\nГотово!\nРезультат парсинга в ./data")

    stats.calculate_stats()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'Ошибка: {e}')