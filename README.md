# hh_researcher

Скрипт для парсинга вакансий с Head Hunter (hh.ru) и анализа зарплат по разным вакансиям. Парсер собирает вакансии по заданным ключевым словам, сохраняет в .csv и .xslx, рассчитывает статистику зарплат по рынку для каждой роли: минимальная, максимальная, средне-арифметическая, медианная зарплата, мода, матожидание.

Для получения данных используется метод [get_vacancies](https://api.hh.ru/openapi/redoc#tag/Poisk-vakansij/operation/get-vacancies) сайта hh.ru

Возможен парсинг сразу по списку вакансий. Подробнее в разделе "Парсинг по списку"

## Быстрое начало

1. Установите зависимости из requirements.txt

```Bash
pip -r requirements.txt
```

2.Запустите скрипт, передав ему в качестве аргумента название вакансии (пробелы заменить на "+")

```Bash
python3 parser.py <название+искомой+вакансии>
```

3.Список вакансий сохранится в директории `./vacancies` с назавнием, соответствующим поисковому запросу. К примеру, если вы искали вакансии `backend+developer`, полученный файл будет выглядеть так:

```Bash
./vacancies/backend+developer.csv
```

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
