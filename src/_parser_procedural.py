import sys
import httpx
import csv
import os
import pandas as pd
import config

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "":
        raise Exception('Передайте в аргумент ключевое слово для поиска вакансии:\n\nПример 1: python3 parser.py Программист\nПример 2: python3 parser.py "Водитель такси"\nПример 3: python3 parser.py "[Data scientist, Data analyst, Data engineer]"\nПример 4: python3 parser.py keywords_list.txt\n\nПодробнее в README.md')
    if os.path.exists("../data/raw") == False: os.mkdir("../data/raw")
    if os.path.exists("../data/processed") == False: os.mkdir("../data/processed")
    
    print("Начинаем парсинг. Подождите...")

    vacancy_input = sys.argv[1]
    vacancies_lists = get_vacancies_list(vacancy_input)

    clean_vacancies_directory()

    for vacancy_group in vacancies_lists:
        print("\nГруппа вакансий: "+vacancy_group[0])
        parse_vacancies_from_hh(vacancy_group)
    
    combine_files()

    print("\nГотово!\nРезультат парсинга в ./data")

def get_vacancies_list(vacancy_input):
    """Функция принимает пользовательский аргумент: ключевое слово, несколько ключевых слов,
    либо название файла с ключевыми словами.
    Возвращает список списков ключевых слов, по которым будет осуществляться поиск.
    Списки ключевых слов находятся внутри списка, потому что делятся по группам.
    Это необходимо для того, чтобы реализовать функционал поиска вакансии по синонимам"""
    
    vacancies = []

    if vacancy_input.endswith(".txt"):
        with open(vacancy_input, "r", encoding='utf-8') as file:
            for line in file:
                keywords = [vac.replace(" ", "+") for vac in line.strip("[]\n").split(", ")]
                vacancies.append(keywords)
    elif vacancy_input.startswith("["):
        vacancies = [[
            vac.replace(" ", "+") for vac in vacancy_input.strip("[]\n").split(", ")
        ]]
    else:
        vacancies = [[vacancy_input]]

    return vacancies
        
def parse_vacancies_from_hh(vacancy_group):
    """Функция принимает список ключевых слов для поиска вакансий, объединенных в группу.
    Все эти ключевые слова - синонимы одной нужной вакансии.
    Названием группы синонимов считаем синоним, расположенный по индексу 0.
    Функция ничего не возвращает.
    Перебирает ключевые слова, отправляет запросы к hh.ru, чтобы получить подходящие вакансии.
    Полученные вакансии сохраняет в словарь, затем записывает в .csv-файл."""

    conf = config.Config()
    print(conf.schedule)
    
    request_endpoint = "https://api.hh.ru/vacancies/"
    request_head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    file_name = f'../data/raw/{vacancy_group[0]}.csv'
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = [
            'keywords_group', 'keyword', 'id', 'position', 'professional_roles', 'city', 'company', 'department',
            'url', 'schedule_name', 'work_format', 'working_hours', 'work_schedule_by_days',
            'experience_name', 'employment_name', 'company_url', 'salary_from', 'salary_to',
            'salary_gross', 'salary_currency', 'requirement', 'responsibility', 'internship',
            'company_trusted', 'has_test', 'normalized_salary'
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists: writer.writeheader()

        for vacancy_name in vacancy_group:
            request_page = 0
            all_pages = 1

            while request_page < all_pages:
                request_parameters = f"&search_field=name&responses_count_enabled=true&per_page=100&schedule={conf.schedule}&area={conf.area_id}&page={request_page}"
                request = f"{request_endpoint}?text={vacancy_name}{request_parameters}"

                response = httpx.get(request, headers=request_head)
                data = response.json()

                print(data)

                if "pages" in data:
                    all_pages = data["pages"]

                for item in data['items']:
                    vacancy = {
                        'keywords_group': vacancy_group[0],
                        'keyword': vacancy_name,
                        'id': item.get('id'),
                        'position': item.get('name'),
                        'city': item['area']['name'] if item.get('area') else None,
                        'company': item['employer']['name'],
                        'department': item['department']['name'] if item.get('department') else None,
                        'url': item.get('alternate_url'),
                        'schedule_name': item['schedule']['name'] if item.get('schedule') else None,
                        'work_format': ', '.join([wf['name'] for wf in item.get('work_format', [])]),
                        'working_hours': ', '.join([wh['name'] for wh in item.get('working_hours', [])]),
                        'work_schedule_by_days': ', '.join([wsbd['name'] for wsbd in item.get('work_schedule_by_days', [])]),
                        'professional_roles': ', '.join([pr['name'] for pr in item.get('professional_roles', [])]),
                        'experience_name': item['experience']['name'] if item.get('experience') else None,
                        'employment_name': item['employment']['name'] if item.get('employment') else None,
                        'company_url': item['employer']['alternate_url'],
                        'salary_from': item['salary']['from'] if item.get('salary') else None,
                        'salary_to': item['salary']['to'] if item.get('salary') else None,
                        'salary_gross': item['salary']['gross'] if item.get('salary') else None,
                        'salary_currency': item['salary']['currency'] if item.get('salary') else None,
                        'requirement': str(item['snippet']['requirement']).replace("<highlighttext>", "").replace("</highlighttext>", "") if item.get('snippet') else None,
                        'responsibility': str(item['snippet']['responsibility']).replace("<highlighttext>", "").replace("</highlighttext>", "") if item.get('snippet') else None,
                        'internship': item.get('internship', False),
                        'company_trusted': item['employer']['trusted'],
                        'has_test': item.get('has_test', False),
                    }
                    vacancy['normalized_salary'] = normalize_salary(vacancy)
                    writer.writerow(vacancy)

                request_page += 1
            
            print(f"+ {vacancy_name}")

def normalize_salary(vacancy):
    """Функция принимает словарь, в котором собраны поля из вакансии с hh.ru
    Возвращает нормализованную зарплату.
    Как происходит нормализация:
    Если зарплата не указана, пропуск.
    Если работодатель указал только минимальную зарплату, принимает ее за рабочую.
    Если указал только максимальную - принимает за рабочую ее.
    Если указана и минимальная, и максимальная зарплаты, принимается средне-арифметическое от них"""

    if vacancy.get("salary_currency") != "RUR": return None

    salary_from = vacancy.get("salary_from", 0)
    salary_to = vacancy.get("salary_to", 0)

    salary = (salary_from + salary_to) / 2 if salary_from and salary_to else salary_from or salary_to

    return salary * 1000 if salary < 1000 else salary

def clean_vacancies_directory():
    """Функция ничего не принимает и ничего не возвращает.
    Вызывается, чтобы очистить директории /data/raw и /data/processed от всех .csv- и .xlsx-файлов."""
    directories = ['../data/raw', '../data/processed']
    for file in directories:
        file = str(os.listdir(file)).strip("[]'")
        for filename in file:
            if filename.endswith('.csv') or filename.endswith('.xlsx'):
                file_path = os.path.join(directories, filename)
                os.remove(file_path)

def combine_files():
    """Функция ничего не принимает и ничего не возвращает
    Она находит все .csv-файлы в директории /data/raw и объединяет их в один .csv-файл.
    Затем она конвертирует тот же файл в .xlsx-формат"""

    csv_files = ["../data/raw/" + files for files in os.listdir("../data/raw/") if files.endswith(".csv")]
    combined_csv = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)
    combined_csv.to_csv("../data/processed/_combined.csv", index=False, encoding="utf-8-sig")
    combined_csv.to_excel("../data/processed/_combined.xlsx", index=False)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Ошибка {e}")
