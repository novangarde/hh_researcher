import httpx
import csv
import os
import time
import pandas as pd
from src.files_handler import Files_operations

class Parser:
    def __init__(self, vacancy_input, config, ps):
        """Конструктор"""
        self.__vacancy_input = vacancy_input
        self.config = config
        self.ps = ps
        self.fo = Files_operations()
        self.vacancies_list = []

    def collect_vacancies(self):
        self.vacancies_list = self.get_vacancies_list()
        for vacancy_group in self.vacancies_list:
            print("\nГруппа вакансий: "+vacancy_group[0])
            self.parse_vacancies_from_hh(vacancy_group)

    def get_vacancies_list(self):
        """Метод принимает пользовательский аргумент: ключевое слово, несколько ключевых слов,
        либо название файла с ключевыми словами.
        Возвращает список списков ключевых слов, по которым будет осуществляться поиск.
        Списки ключевых слов находятся внутри списка, потому что делятся по группам.
        Это необходимо для того, чтобы реализовать функционал поиска вакансии по синонимам"""
        
        vacancies = self.vacancies_list

        if self.vacancy_input.endswith(".txt"):
            with open(self.vacancy_input, "r", encoding='utf-8') as file:
                for line in file:
                    keywords = [vac.replace(" ", "+") for vac in line.strip("[]\n").split(", ")]
                    vacancies.append(keywords)
        elif self.vacancy_input.startswith("["):
            vacancies = [[
                vac.replace(" ", "+") for vac in self.vacancy_input.strip("[]\n").split(", ")
            ]]
        else:
            vacancies = [[self.vacancy_input]]

        return vacancies
    
    def normalize_salary(self, vacancy):
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
    
    def parse_vacancies_from_hh(self, vacancy_group):
        """Функция принимает список ключевых слов для поиска вакансий, объединенных в группу.
        Все эти ключевые слова - синонимы одной нужной вакансии.
        Названием группы синонимов считаем синоним, расположенный по индексу 0.
        Функция ничего не возвращает.
        Перебирает ключевые слова, отправляет запросы к hh.ru, чтобы получить подходящие вакансии.
        Полученные вакансии сохраняет в словарь, затем записывает в .csv-файл."""
        
        request_endpoint = "https://api.hh.ru/vacancies/"
        request_head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        experience = "&experience="+self.config.experience if self.config.experience in ['noExperience', 'between1And3', 'between3And6', 'moreThan6'] else ""
        print(f"Experience: {experience}")
        employment = "&employment="+self.config.employment if self.config.employment in ['full', 'part', 'project', 'volunteer', 'probation'] else ""
        print(f"Employment: {employment}")
        schedule = "&schedule="+self.config.schedule if self.config.schedule in ['fullDay', 'shift', 'flexible', 'remote', 'flyInFlyOut'] else ""
        print(f"Schedule: {schedule}")
        area = self.config.area_id
        print(f"Area: {area}")

        file_name = f'./data/raw/{vacancy_group[0]}.csv'
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

                    request = f'{request_endpoint}?text={vacancy_name}&search_field=name&page={request_page}&per_page=100&responses_count_enabled=true&area={area}{experience}{employment}{schedule}'
                    response = httpx.get(request, headers=request_head)

                    if response.status_code != 200:
                        raise Exception(f"{response.status_code}: {response.text}")

                    data = response.json()

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
                            'company_url': item['employer'].get('alternate_url') if item.get('employer') else None,
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
                        vacancy['normalized_salary'] = self.normalize_salary(vacancy)
                        writer.writerow(vacancy)

                    request_page += 1
                
                print(f"+ {vacancy_name}")
                time.sleep(1/30)

    @property
    def vacancy_input(self):
        return self.__vacancy_input
