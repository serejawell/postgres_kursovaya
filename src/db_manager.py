import psycopg2
from src.utils import filter_salary


class DBManager:
    """
    Класс для управления базой данных.
    """

    def __init__(self, config: dict, dbname: str = 'hh_info') -> None:
        """
        Инициализирует объект DBManager.
        """
        self.config = config
        self.dbname = dbname
        self.conn = None

    def create_db(self):
        """
        Создание базы данных.
        """
        try:
            connection = psycopg2.connect(**self.config)
            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute(f'DROP DATABASE IF EXISTS {self.dbname}')
                cursor.execute(f'CREATE DATABASE {self.dbname}')

        except (Exception, psycopg2.DatabaseError) as e:
            return f"Произошла ошибка {e}"

    def create_tables(self):
        """
        Создание таблиц в базе данных.
        """
        try:
            self.config['dbname'] = self.dbname
            self.conn = psycopg2.connect(**self.config)
            self.conn.autocommit = True
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE employers (
                       company_id serial PRIMARY KEY,
                       company_name varchar(50) NOT NULL,
                       company_url varchar (100) NOT NULL);
                    """)
                cursor.execute("""
                    CREATE TABLE vacancies (
                        vacancy_id serial PRIMARY KEY,
                        company_id int REFERENCES employers (company_id) NOT NULL,
                        title_vacancy varchar(200) NOT NULL,
                        salary int,
                        link varchar(200) NOT NULL,
                        description text,
                        experience varchar(150));
                    """)
            self.conn.commit()

        except (Exception, psycopg2.DatabaseError) as e:
            return f"Произошла ошибка {e}"

    def insert_values(self, employers_info):
        """
        Вставляет данные о работодателях и вакансиях в базу данных.
        """
        try:
            with self.conn.cursor() as cursor:
                for employer in employers_info:
                    cursor.execute('INSERT INTO employers (company_name, company_url)'
                                   'VALUES (%s, %s)'
                                   'returning company_id',
                                   (employer["company"].get("name"),
                                    employer["company"].get("company_url")))

                    company_id = cursor.fetchone()[0]

                    for vacancy in employer["vacancies"]:
                        salary = filter_salary(vacancy["salary"])
                        cursor.execute('INSERT INTO vacancies'
                                       '(vacancy_id, company_id, title_vacancy, salary, link, description, experience)'
                                       'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                                       (vacancy["id"], company_id, vacancy["name"], salary, vacancy["alternate_url"], vacancy["snippet"].get("responsibility"),
                                        vacancy["experience"].get("name")))
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as e:
            return f"Произошла ошибка {e}"

    def get_companies_and_vacancies_count(self) -> list | str:
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('SELECT company_name, COUNT(vacancy_id) '
                               'FROM employers '
                               'JOIN vacancies USING (company_id) '
                               'GROUP BY company_name;')

                data = cursor.fetchall()
            return data
        except (Exception, psycopg2.DatabaseError) as e:
            return f"Произошла ошибка {e}"

    def get_all_vacancies(self) -> list | str:
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('SELECT title_vacancy, company_name, salary, link '
                               'FROM vacancies '
                               'JOIN employers USING (company_id)')

                data = cursor.fetchall()
            return data
        except (Exception, psycopg2.DatabaseError) as e:
            return f"Произошла ошибка {e}"

    def get_avg_salary(self) -> list | str:
        """
        Получает среднюю зарплату по вакансиям.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('SELECT company_name, round(AVG(salary)) AS average_salary '
                               'FROM employers '
                               'JOIN vacancies USING (company_id) '
                               'GROUP BY company_name;')

                data = cursor.fetchall()
            return data
        except (Exception, psycopg2.DatabaseError) as e:
            return f"Произошла ошибка {e}"

    def get_vacancies_with_higher_salary(self) -> list | str:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('SELECT * '
                               'FROM vacancies '
                               'WHERE salary > (SELECT AVG(salary) FROM vacancies);')

                data = cursor.fetchall()
            return data
        except (Exception, psycopg2.DatabaseError) as e:
            return f"Произошла ошибка {e}"

    def get_vacancies_with_keyword(self, keyword: str) -> list | str:
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"""
                                SELECT * 
                                FROM vacancies
                                WHERE lower(title_vacancy) LIKE '%{keyword}'
                                OR lower(title_vacancy) LIKE '%{keyword}%'
                                OR lower(title_vacancy) LIKE '{keyword}%'""")

                data = cursor.fetchall()
            return data
        except (Exception, psycopg2.DatabaseError) as e:
            return f"Произошла ошибка {e}"

    def close_connection(self) -> None:
        """
        Закрывает соединение с базой данных.
        """
        if self.conn:
            self.conn.close()