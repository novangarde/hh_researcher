# hh_researcher

Скрипт предназначен для парсинга вакансий с сайта Head Hunter (hh.ru) и анализа зарплат. Он использует API hh.ru для сбора данных по заданным ключевым словам, группирует вакансии по специализациям и сохраняет результаты в формате .csv и .xlsx.

<ins>Основные функции скрипта:</ins>

* <ins>Сбор данных:</ins> Скрипт отправляет запросы к API, чтобы получить вакансии, соответствующие указанным критериям.
* <ins>Группировка:</ins> Вакансии группируются по специализациям для удобства анализа.
* <ins>Анализ зарплат:</ins> Скрипт рассчитывает статистику по зарплатам для каждой группы вакансий, включая:
  * Минимальная зарплата
  * Максимальная зарплата
  * Среднеарифметическая зарплата
  * Медианная зарплата
  * Мода
  * Матожидание

Эти данные помогают пользователям лучше понять рынок труда и принимать обоснованные решения при поиске работы или найме сотрудников.

Для получения данных используется метод [get_vacancies](https://api.hh.ru/openapi/redoc#tag/Poisk-vakansij/operation/get-vacancies) сайта hh.ru

## Быстрое начало

0. Клонируйте проект

``` Bash
git clone git@github.com:novangarde/hh_researcher.git
```

1. Обновите список пакетов:

```Bash
sudo apt update
```

2. Установите интерпретатор Python3, менеджер пакетов pip и инструмент для создания изолированных виртуальных окружений Virtualenv:

```Bash
sudo apt install python3 python3-pip python3-venv
```

3. Создайте виртуальное окружение:

```Bash
python3 -m venv <название> # пример: python3 -m venv test
```

4. Активируйте виртуальное окружение:

```Bash
source ./<название>/bin/activate # пример: source ./test/bin/activate
```

5. Установите зависимости из файла requirements.txt:

```Bash
pip install -r requirements.txt
```

6. Запустите скрипт, передав ему в качестве аргумента название вакансии в кавычках:

```Bash
python3 researcher.py <название+искомой+вакансии> # пример: python3 researcher.py "Data Scientist"
```

7. Собранные данные о вакансиях вы найдете в следующих директориях:
* `data/raw` - для сырых данных
* `data/processed` - для обработанных

## Парсинг по списку

Вы также можете передать в качестве аргумента название .txt-файла, в котором хранится список искомых вакансий.

Тогда скрипт построчно прочитает файл, осуществит поиск каждой вакансии из файла и сохранит в директории `./vacancies` по файлу для каждой вакансии с соответствующими названиями.

### Пример

1. Создайте в корневой директории проекта файл `example.txt` следующего содержания:
    Data+Analyst
    Data+Engineer
    Data+Scientist

2. Запустите скрипт, передав в него название файла в качестве аргумента:

```Bash
python3 parser.py example.txt
```

3.Дождитесь выполнения скрипта и перейдите в директорию `./vacancies`, здесь должны находиться три файла:
    *Data+Analyst.csv
    *Data+Engineer.csv
    *Data+Scientist.csv

### Правила форматирования .txt-файла

* Располагайте по одному названию вакансии на строке
* Не заканчивайте строку знаками препинания
* Не используйте маркировку
* Не используйте спецсимволы
* На каждой строке должно быть только название вакансии
* Вместо пробелов слова должны соединяться "+"

## Расчеты

### Нормализация зарплат

Скрипт рассчитывает средне-арифметическую зарплату, медиану, моду, максимальное и минимальное значение. Прежде чем рассчитать все эти показатели, данные о зарплате в вакансиях нужно нормализовать, потому что они не всегда публикуются в корректном виде.

__Во-первых__, могут попадаться данные в разных валютах. Сейчас скрипт отбрасывает все значения, кроме рублевых.
__Во-вторых__, работодатели не всегда указывают минимальную и максимальную зарплату. Часто бывает либо одно, либо другое, но порой данных о зарплате нет вовсе. Поэтому для расчетов мы выбираем следующую стратегию:

1. Если есть только минимальная зарплата, считаем, что это зарплата, которую платят на этой вакансии.
2. Если есть только максимальная, считаем, что это зарплата, которую платят на этой вакансии.
3. Если есть и максимальная, и минимальная зарплаты, суммируем их и делим на 2, вычисляя средне-арифметическое значение. Считаем, что это та зарплата, которую платят на этой вакансии.

__В-третьих__, в некоторых вакансиях зарплаты указаны на три разряда ниже, чем на самом деле, то есть, вероятнее всего, подразумевается зарплата от 100 000 до 120 000 рублей, а в вакансии указано от 100 до 120, три разряда отбросили. В таких случаях беру на себя смелость умножить зарплату на 1000 в целях нормализации статистики.

Минимальную и максимальную зарплаты высчитываем по пиковым значениям.
