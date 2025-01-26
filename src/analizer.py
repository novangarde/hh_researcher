import sys
import os
import pandas as pd

def main():
    calculate_stats()

def calculate_stats():
    # Читаем данные из файла combined.csv
    df = pd.read_csv("./vacancies/_combined.csv")

    # Убираем строки с отсутствующими значениями в normalized_salary
    df = df[df['normalized_salary'].notna()]

    # Группируем по keywords и вычисляем статистики
    report = df.groupby('keywords_group').agg(
        count=('keywords_group', 'size'),  # Количество вакансий
        mean_salary=('normalized_salary', 'mean'),  # Средняя зарплата
        median_salary=('normalized_salary', 'median'),  # Медиана зарплаты
        mode_salary=('normalized_salary', lambda x: x.mode()[0] if not x.mode().empty else None),  # Мода
        min_salary=('normalized_salary', 'min'),  # Минимальная зарплата
        max_salary=('normalized_salary', 'max')   # Максимальная зарплата
    ).reset_index()

    # Теперь добавим расчет математического ожидания с учетом вероятностей для каждой группы
    expected_salaries = []

    for group in report['keywords_group']:
        group_salaries = df[df['keywords_group'] == group]['normalized_salary']
        salary_counts = group_salaries.value_counts()
        
        total_count = salary_counts.sum()
        probabilities = salary_counts / total_count
        
        expected_salary = (salary_counts.index * probabilities).sum()
        expected_salaries.append(expected_salary)

    report['expected_salary'] = expected_salaries

    # Сохраняем результаты в файл report.xlsx
    report.to_excel("./stats.xlsx", index=False)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Ошибка {e}")
