import sqlite3

from fake_useragent import UserAgent
from prettytable import PrettyTable
from selectolax.parser import HTMLParser

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Scraping Setup
def get_html(url: str) -> HTMLParser:
    options = Options()
    options.add_argument('--headless')
    options.add_argument(f'user-agent={UserAgent().random}')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    html = HTMLParser(driver.page_source)

    return html


# Scraping Table
def parse_table(html: HTMLParser) -> list:
    table_rows = html.css_first('table.ParseTransform__table_noHeader').css_first('tbody').css('tr')
    data = []
    for row in table_rows[2:]:
        columns = row.css('td')
        cnt = 0
        rem = []
        for column in columns:
            rem.append(column.text())
            cnt += 1
            if cnt == 14:
                data.append(rem[:5])

    return data


# Print Pretty Table
def print_table(data: list) -> PrettyTable:
    t = PrettyTable(
        ['Наименование направления (2023 Год)', 'Кафедра', 'Основной конкурс', 'Средний Балл', 'Платная Основа']
    )
    for i in range(len(data)):
        t.add_row(data[i])

    return t


# Save to Database
def save_db(data: list) -> None:
    with sqlite3.connect('bmstu.db') as con:
        cur = con.cursor()

        cur.execute("""DROP TABLE IF EXISTS majors""")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS majors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            main_competition INTEGER,
            mean_mark INTEGER,
            money_mark INTEGER
            )
            """
        )

        for item in data:
            cur.execute(
                """INSERT INTO majors(name, department, main_competition, mean_mark, money_mark) VALUES(?, ?, ?, ?, ?)
                """, item
            )

        con.commit()


# Main
def main():
    url = 'https://bmstu.ru/bachelor/previous_points'
    html = get_html(url)
    data = parse_table(html)
    save_db(data)
    print(print_table(data))


if __name__ == '__main__':
    main()
