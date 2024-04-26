import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, \
    QTableWidgetItem, QComboBox, QMessageBox, QHeaderView, QSizePolicy, QTabWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# noinspection PyUnresolvedReferences
class BudgetApp(QWidget):
    def __init__(self):
        super().__init__()

        # Inicjalizacja interfejsu użytkownika
        self.cursor = None
        self.conn = None
        self.plot_layout = None
        self.canvas = None
        self.figure = None
        self.table_budget = None
        self.label_report = None
        self.button_generate_report = None
        self.tab_report = None
        self.button_remove_selected = None
        self.button_add_expense = None
        self.edit_expense_description = None
        self.edit_expense = None
        self.combo_expense_category = None
        self.label_expense_category = None
        self.label_expense_description = None
        self.label_expense_amount = None
        self.tab_expense = None
        self.button_remove_selected_income = None
        self.current_chart = None
        self.button_add_income = None
        self.edit_income_description = None
        self.edit_income = None
        self.combo_income_category = None
        self.label_income_category = None
        self.label_income_description = None
        self.label_income_amount = None
        self.tab_income = None
        self.tab_widget = None
        self.label_result = None
        self.init_ui()

        # Inicjalizacja bazy danych
        self.init_database()

        # Wczytaj dane przy starcie
        self.load_data()

        # Rysuj wykresy po wczytaniu danych
        self.draw_charts()

    def setup_table(self):
        # Konfiguracja tabeli
        self.table_budget.setColumnCount(7)
        self.table_budget.setHorizontalHeaderLabels(
            ['ID', 'Opis', 'Kwota', 'Opis Wydatku', 'Opis Przychodu', 'Kategoria Wydatku', 'Kategoria Przychodu'])

        # Ustawienia dotyczące zmiany rozmiarów kolumn
        header = self.table_budget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # Dostosuj rozmiar kolumny 'ID' do zawartości
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Rozciągnij kolumnę 'Opis' na całą dostępną przestrzeń
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Dostosuj rozmiar kolumny 'Kwota' do zawartości
        header.setSectionResizeMode(3,
                                    QHeaderView.Stretch)  # Rozciągnij kolumnę 'Opis Wydatku' na całą dostępną
        # przestrzeń
        header.setSectionResizeMode(4,
                                    QHeaderView.Stretch)  # Rozciągnij kolumnę 'Opis Przychodu' na całą dostępną
        # przestrzeń
        header.setSectionResizeMode(5,
                                    QHeaderView.Stretch)  # Rozciągnij kolumnę 'Kategoria Wydatku' na całą dostępną
        # przestrzeń
        header.setSectionResizeMode(6,
                                    QHeaderView.Stretch)  # Rozciągnij kolumnę 'Kategoria Przychodu' na całą dostępną
        # przestrzeń

        # Ustaw stałą wysokość tabeli
        self.table_budget.setFixedHeight(200)  # Ustaw dowolną stałą wysokość

        # Ustaw, aby tabela dostosowywała się do zmian szerokości okna, ale miała stałą wysokość
        self.table_budget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def init_ui(self):
        # Tworzenie widżetów interfejsu użytkownika
        self.label_result = QLabel('Saldo: 0.0')

        # Utwórz zakładki
        self.tab_widget = QTabWidget()

        # Zakładka Przychody
        self.tab_income = QWidget()
        self.label_income_amount = QLabel('Kwota:')
        self.label_income_description = QLabel('Opis:')
        self.label_income_category = QLabel('Kategoria:')
        self.combo_income_category = QComboBox()
        self.combo_income_category.addItems(['Praca', 'Pozyczka', 'Inne'])
        self.edit_income = QLineEdit()
        self.edit_income_description = QLineEdit()
        self.button_add_income = QPushButton('Dodaj przychód')
        layout_income = QVBoxLayout()
        layout_income.addWidget(self.label_income_amount)
        layout_income.addWidget(self.edit_income)
        layout_income.addWidget(self.label_income_description)
        layout_income.addWidget(self.edit_income_description)
        layout_income.addWidget(self.label_income_category)
        layout_income.addWidget(self.combo_income_category)
        layout_income.addWidget(self.button_add_income)
        widget_income = QWidget()
        widget_income.setLayout(layout_income)
        self.tab_widget.addTab(widget_income, 'Przychody')

        # Add the "Usuń zaznaczone" button for Przychody
        self.button_remove_selected_income = QPushButton('Usuń zaznaczone')
        layout_income.addWidget(self.button_remove_selected_income)
        # noinspection PyUnresolvedReferences
        self.button_remove_selected_income.clicked.connect(self.remove_selected_income)

        # Zakładka Wydatki
        self.tab_expense = QWidget()
        self.label_expense_amount = QLabel('Kwota:')
        self.label_expense_description = QLabel('Opis:')
        self.label_expense_category = QLabel('Kategoria:')
        self.combo_expense_category = QComboBox()
        self.combo_expense_category.addItems(['Jedzenie', 'Transport', 'Rozrywka', 'Inne'])
        self.edit_expense = QLineEdit()
        self.edit_expense_description = QLineEdit()
        self.button_add_expense = QPushButton('Dodaj wydatek')
        self.button_remove_selected = QPushButton('Usuń zaznaczone')
        layout_expense = QVBoxLayout()
        layout_expense.addWidget(self.label_expense_amount)
        layout_expense.addWidget(self.edit_expense)
        layout_expense.addWidget(self.label_expense_description)
        layout_expense.addWidget(self.edit_expense_description)
        layout_expense.addWidget(self.label_expense_category)
        layout_expense.addWidget(self.combo_expense_category)
        layout_expense.addWidget(self.button_add_expense)
        layout_expense.addWidget(self.button_remove_selected)
        widget_expense = QWidget()
        widget_expense.setLayout(layout_expense)
        self.tab_widget.addTab(widget_expense, 'Wydatki')

        # Zakładka Raport
        self.tab_report = QWidget()
        self.button_generate_report = QPushButton('Generuj raport')
        self.label_report = QLabel('Raport:')
        layout_report = QVBoxLayout()
        layout_report.addWidget(self.button_generate_report)
        layout_report.addWidget(self.label_report)
        widget_report = QWidget()
        widget_report.setLayout(layout_report)
        self.tab_widget.addTab(widget_report, 'Raport')
        # noinspection PyUnresolvedReferences
        self.button_generate_report.clicked.connect(self.generate_report)

        # Tworzenie tabeli
        self.table_budget = QTableWidget()
        self.setup_table()

        # Dodanie tabeli do głównego układu
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label_result)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.table_budget)

        # Inicjalizacja obszaru do rysowania wykresów
        self.figure = Figure(figsize=(10, 5), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.plot_layout = QVBoxLayout()  # Zmieniona nazwa zmiennej na self.plot_layout
        self.plot_layout.addWidget(self.canvas)
        self.plot_layout.addStretch(1)
        main_layout.addLayout(self.plot_layout)  # Teraz dodajemy plot_layout do main_layout

        # Ustawienie układu dla okna głównego
        self.setLayout(main_layout)

        # Podłączenie przycisków do funkcji obsługujących zdarzenia
        # noinspection PyUnresolvedReferences
        self.button_add_income.clicked.connect(self.add_income)
        self.button_add_expense.clicked.connect(self.add_expense)
        self.button_remove_selected.clicked.connect(self.remove_selected)
        self.button_generate_report.clicked.connect(self.generate_report)

        # Ustawienie funkcji obsługującej zmianę zakładki
        self.tab_widget.currentChanged.connect(self.tab_changed)

    def init_database(self):
        # Inicjalizacja bazy danych SQLite
        try:
            self.conn = sqlite3.connect('budget_data.db')
            self.cursor = self.conn.cursor()

            # Tworzenie tabeli, jeśli nie istnieje
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS budget (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    amount REAL,
                    expense_description TEXT,
                    income_description TEXT,
                    expense_category TEXT,
                    income_category TEXT
                )
            ''')
            self.conn.commit()
        except Exception as e:
            self.show_error_message(f"Błąd inicjalizacji bazy danych: {e}")

    def load_data(self):
        # Wczytywanie danych z bazy danych i aktualizacja tabeli
        try:
            if self.tab_widget.currentIndex() == 0:
                # Zakładka Przychody
                category_column = 'income_category'
                amount_condition = 'amount > 0'
            elif self.tab_widget.currentIndex() == 1:
                # Zakładka Wydatki
                category_column = 'expense_category'
                amount_condition = 'amount < 0'
            else:
                # Inne zakładki
                category_column = None
                amount_condition = None

            self.table_budget.setRowCount(0)

            if category_column:
                query = f'SELECT * FROM budget ' \
                        f'WHERE {amount_condition} AND {category_column} IS NOT NULL AND {category_column} != ""'
                self.cursor.execute(query)
            else:
                self.cursor.execute('SELECT * FROM budget')

            rows = self.cursor.fetchall()

            for row in rows:
                row_position = self.table_budget.rowCount()
                self.table_budget.insertRow(row_position)

                # Ensure the row has at least 7 elements before accessing them
                if len(row) >= 7:
                    self.table_budget.setItem(row_position, 0, QTableWidgetItem(str(row[0])))
                    self.table_budget.setItem(row_position, 1, QTableWidgetItem(row[1]))
                    self.table_budget.setItem(row_position, 2, QTableWidgetItem(str(row[2])))
                    self.table_budget.setItem(row_position, 3, QTableWidgetItem(row[3]))
                    self.table_budget.setItem(row_position, 4, QTableWidgetItem(row[4]))
                    self.table_budget.setItem(row_position, 5, QTableWidgetItem(row[5]))
                    self.table_budget.setItem(row_position, 6, QTableWidgetItem(row[6]))
                else:
                    # Handle the case where the row doesn't have enough elements
                    print(f"Skipping row {row[0]} due to insufficient data.")

            # Po wczytywaniu danych, oblicz saldo
            self.calculate_balance()
        except Exception as e:
            self.show_error_message(f"Błąd wczytywania danych: {e}")

    def tab_changed(self):
        # Obsługa zmiany zakładki - wczytaj dane dla aktualnej zakładki
        self.load_data()
        self.draw_charts()

    def add_income(self):
        income_amount_str = self.edit_income.text()
        income_amount = self.validate_amount(income_amount_str)

        if income_amount is not None:
            income_description = self.edit_income_description.text()
            income_category = self.combo_income_category.currentText()

            self.cursor.execute(
                'INSERT INTO budget (description, amount, expense_description, income_description, expense_category, '
                'income_category) VALUES (?, ?, ?, ?, ?, ?)',
                ("Przychód", income_amount, "", income_description, "", income_category))
            self.conn.commit()

            # Aktualizacja tabeli, czyszczenie pól tekstowych, obliczanie salda i rysowanie wykresów
            self.load_data()
            self.edit_income.clear()
            self.edit_income_description.clear()

            # Dodaj aktualizację wykresów
            self.draw_charts()

    def add_expense(self):
        expense_amount_str = self.edit_expense.text()
        expense_amount = self.validate_amount(expense_amount_str)

        if expense_amount is not None:
            expense_description = self.edit_expense_description.text()
            expense_category = self.combo_expense_category.currentText()

            self.cursor.execute(
                'INSERT INTO budget (description, amount, expense_description, income_description,'
                ' expense_category, income_category) VALUES (?, ?, ?, ?, ?, ?)',
                ("Wydatek", -expense_amount, expense_description, "", expense_category, ""))
            self.conn.commit()

            # Aktualizacja tabeli, czyszczenie pól tekstowych, obliczanie salda i rysowanie wykresów
            self.load_data()
            self.edit_expense.clear()
            self.edit_expense_description.clear()

            # Dodaj aktualizację wykresów
            self.draw_charts()

    def remove_selected(self):
        # Usuwanie zaznaczonych wpisów z bazy danych
        selected_rows = set(item.row() for item in self.table_budget.selectedItems())
        for row in selected_rows:
            item_id = int(self.table_budget.item(row, 0).text())
            self.cursor.execute('DELETE FROM budget WHERE id = ?', (item_id,))

        # Aktualizacja identyfikatorów po usunięciu
        self.update_ids()

        self.conn.commit()

        # Aktualizacja tabeli i obliczanie salda
        self.load_data()

    def remove_selected_income(self):
        # Usuwanie zaznaczonych wpisów dotyczących przychodów z bazy danych
        selected_rows = set(item.row() for item in self.table_budget.selectedItems())
        for row in selected_rows:
            item_id = int(self.table_budget.item(row, 0).text())
            self.cursor.execute('DELETE FROM budget WHERE id = ?', (item_id,))

        # Aktualizacja identyfikatorów po usunięciu
        self.update_ids()

        self.conn.commit()

        # Aktualizacja tabeli i obliczanie salda
        self.load_data()

    def update_ids(self):
        # Aktualizuj identyfikatory w bazie danych
        try:
            self.cursor.execute('UPDATE budget SET id = id - 1 WHERE id > 1')
            self.conn.commit()
        except Exception as e:
            self.show_error_message(f"Błąd aktualizacji identyfikatorów: {e}")

    def calculate_balance(self):
        # Obliczanie salda na podstawie wpisów w tabeli
        total_balance = 0.0

        for row in range(self.table_budget.rowCount()):
            item = self.table_budget.item(row, 2)

            if item is not None:
                total_balance += float(item.text())

        self.label_result.setText(f'Suma: {total_balance}')

    def draw_charts(self):
        # Usuń poprzednie dane z obszaru rysowania
        self.figure.clear()

        # Pobierz aktualne dane do wykresów
        income_categories, income_values = self.get_chart_data('income')
        expense_categories, expense_values = self.get_chart_data('expense')

        # Sprawdź aktualną zakładkę
        current_index = self.tab_widget.currentIndex()

        # Rysuj wykresy związane z aktualną zakładką
        if current_index == 0:  # Zakładka Przychody
            self.current_chart = self.figure.add_subplot(111)
            self.current_chart.pie(income_values, labels=income_categories, autopct='%1.1f%%', startangle=90)
            self.current_chart.set_title('Przychody')
            self.current_chart.axis('equal')

        elif current_index == 1:  # Zakładka Wydatki
            self.current_chart = self.figure.add_subplot(111)
            self.current_chart.pie(expense_values, labels=expense_categories, autopct='%1.1f%%', startangle=90)
            self.current_chart.set_title('Wydatki')
            self.current_chart.axis('equal')

        elif current_index == 2:  # Zakładka Raport
            # Rysuj dwa wykresy kołowe
            ax1 = self.figure.add_subplot(121)
            ax1.pie(income_values, labels=income_categories, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Przychody')
            ax1.axis('equal')

            ax2 = self.figure.add_subplot(122)
            ax2.pie(expense_values, labels=expense_categories, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Wydatki')
            ax2.axis('equal')

        # Odśwież obszar rysowania
        self.canvas.draw()

    def get_chart_data(self, category_type):
        # Pobierz dane procentowe do wykresu dla przychodów lub wydatków
        total_amount = 0.0
        category_totals = {}

        for row in range(self.table_budget.rowCount()):
            amount = float(self.table_budget.item(row, 2).text())
            category = self.table_budget.item(row, 6).text() if category_type == 'income' else self.table_budget.item(
                row, 5).text()

            if (category_type == 'income' and amount > 0) or (category_type == 'expense' and amount < 0):
                total_amount += amount
                category_totals[category] = category_totals.get(category, 0) + amount

        # Oblicz dane procentowe
        categories = list(category_totals.keys())
        values = [category_totals[category] / total_amount * 100 for category in categories]
        return categories, values

    def generate_report(self):
        try:
            total_income = 0.0
            total_expense = 0.0
            income_category_totals = {}
            expense_category_totals = {}

            for row in range(self.table_budget.rowCount()):
                amount = float(self.table_budget.item(row, 2).text())
                category_income = self.table_budget.item(row, 6).text()  # Kategoria Przychodu
                category_expense = self.table_budget.item(row, 5).text()  # Kategoria Wydatku
                description_income = self.table_budget.item(row, 4).text()  # Opis Przychodu
                description_expense = self.table_budget.item(row, 3).text()  # Opis Wydatku

                if amount > 0:
                    total_income += amount
                    income_category_totals[category_income] = income_category_totals.get(category_income, [])
                    income_category_totals[category_income].append(
                        {"description": description_income, "amount": amount})
                elif amount < 0:
                    total_expense += abs(amount)  # Uwzględnij kwotę bezwzględną dla wydatków
                    expense_category_totals[category_expense] = expense_category_totals.get(category_expense, [])
                    expense_category_totals[category_expense].append(
                        {"description": description_expense, "amount": abs(amount)})

            total_balance = total_income - total_expense  # Oblicz saldo jako różnicę między przychodami a wydatkami

            report_text = f"Przychody: {total_income}\nWydatki: {total_expense}\nSaldo: {total_balance}"

            # Raport z podziałem na kategorie
            report_text += "\n\nRaport z podziałem na kategorie:\n"
            report_text += "\nKategorie przychodów:\n"
            for category, items in income_category_totals.items():
                report_text += f"{category}:\n"
                for item in items:
                    report_text += f"    Opis: {item['description']}, Kwota: {item['amount']}\n"

            report_text += "\nKategorie wydatków:\n"
            for category, items in expense_category_totals.items():
                report_text += f"{category}:\n"
                for item in items:
                    report_text += f"    Opis: {item['description']}, Kwota: {item['amount']}\n"

            # Wyświetlenie raportu w polu tekstowym
            self.label_report.setText(f'Raport:\n{report_text}')

            # Dodaj aktualizację wykresów po wygenerowaniu raportu
            self.draw_charts()

        except Exception as e:
            self.show_error_message(f"Błąd generowania raportu: {e}")

    def calculate_category_expenses(self, category):
        category_expenses = {}

        for row in range(self.table_budget.rowCount()):
            amount = float(self.table_budget.item(row, 2).text())
            desc = self.table_budget.item(row, 3).text()  # Opis Wydatku
            row_category = self.table_budget.item(row, 5).text()  # Kategoria Wydatku

            if amount < 0 and row_category == category:
                category_expenses[desc] = category_expenses.get(desc, 0) + amount

        return category_expenses

    def validate_amount(self, amount_str):
        try:
            amount = float(amount_str)
            return amount
        except ValueError:
            self.show_error_message("Błąd: Wprowadzono nieprawidłową kwotę.")
            return None

    @staticmethod
    def show_error_message(message):
        # Wyświetl okno dialogowe z komunikatem błędu
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Błąd")
        msg_box.setText(message)
        msg_box.exec_()

    def closeEvent(self, event):
        # Zapisywanie danych przed zamknięciem aplikacji
        try:
            self.conn.commit()
            event.accept()
        except Exception as e:
            self.show_error_message(f"Błąd zapisu danych przed zamknięciem: {e}")
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BudgetApp()
    window.setWindowTitle('Aplikacja do Zarządzania Budżetem')
    window.show()
    sys.exit(app.exec_())
