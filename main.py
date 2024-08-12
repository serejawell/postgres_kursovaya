from src.config import config_parser
from src.db_manager import DBManager
from src.parser import employer_parser


def main():
    """
    Главная функция прогрммы, которая выполняет следующие функции:
    1. Читает конфигурационный файл и создает объект DBManager.
    2. Создает базу данных и таблицы.
    3. Парсит информацию о работодателях и вакансиях из API HeadHunter.
    4. Вставляет полученные данные в базу данных.
    5. Предлагает пользователю выбрать действие из консольного меню.
    """
    config = config_parser("database.ini")
    dbmanager = DBManager(config)
    dbmanager.create_db()
    dbmanager.create_tables()
    empoloyers = employer_parser()
    dbmanager.insert_values(empoloyers)

    while True:
        # Выводим меню для пользователя
        print(f'\nЗдравствуйте!\nВыберите действие: \n'
              f'1. Список всех компаний и количество вакансий у каждой компании\n'
              f'2. Cписок всех вакансий с указанием названия компании и вакансии, зарплаты и ссылки на вакансию\n'
              f'3. Средняя зарплата по вакансиям\n'
              f'4. Список всех вакансий, у которых зарплата выше средней по всем вакансиям\n'
              f'5. Список всех вакансий, в названии которых содержатся запрашиваемое слово\n'
              f'6. Выход\n')
        try:
            # Ввод действия пользователем
            choose: int = int(input("Введите запрос: "))
            # Выполнение действия в зависимости от выбора пользователя
            if 1 <= choose <= 6:
                if choose == 1:
                    print(dbmanager.get_companies_and_vacancies_count())
                elif choose == 2:
                    print(dbmanager.get_all_vacancies())
                elif choose == 3:
                    print(dbmanager.get_avg_salary())
                elif choose == 4:
                    print(dbmanager.get_vacancies_with_higher_salary())
                elif choose == 5:
                    user_input = input("Введите слово для поиска вакансий: ").lower()
                    print(dbmanager.get_vacancies_with_keyword(user_input))
                elif choose == 6:
                    break
            else:
                print("Ошибка: Неверный выбор. Пожалуйста, выберите число от 1 до 6.")
        except ValueError:
            print("Ошибка: Неверный ввод. Пожалуйста, введите целое число.")

    # Закрываем соединение с базой данных
    dbmanager.close_connection()


if __name__ == '__main__':
    main()