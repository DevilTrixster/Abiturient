import sys
import os
import pyodbc
import re
import hashlib  # Добавлен импорт для хеширования паролей
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ============================================
# КОНСТАНТЫ РОЛЕЙ ДОСТУПА
# ============================================
USER_ROLES = {
    'USER': 'Пользователь',  # Только просмотр
    'OPERATOR': 'Оператор',  # Добавление/редактирование данных
    'ADMIN': 'Администратор'  # Полный доступ + настройки системы
}


class LoginDialog(QDialog):
    """Диалог входа в систему с аутентификацией"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в систему: Зачисления абитуриентов СмолГУ")
        self.setFixedSize(600, 500)
        self.role = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setWindowIcon(QIcon('logo.png'))

        # Добавляем фото в диалог авторизации
        photo_label = QLabel()
        photo_pixmap = QPixmap('logo.png')

        if not photo_pixmap.isNull():
            photo_pixmap = photo_pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
            photo_label.setPixmap(photo_pixmap)
            photo_label.setFixedSize(100, 100)
            photo_label.setStyleSheet("border: 2px solid #3498db; border-radius: 5px; margin-bottom: 10px;")
        else:
            photo_label.setText("Лого")
            photo_label.setFixedSize(100, 100)
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            photo_label.setStyleSheet("""
                        border: 2px solid #3498db; 
                        border-radius: 5px; 
                        background-color: #192140; 
                        color: #3498db; 
                        font-weight: bold;
                        margin-bottom: 10px;
                    """)

        layout.addWidget(photo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Заголовок
        title = QLabel("🔐 Авторизация в системе")
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            margin: 20px;
            color: #2c3e50;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Выбор роли
        role_group = QGroupBox("Выберите роль для входа")
        role_layout = QVBoxLayout(role_group)

        self.admin_radio = QRadioButton("Администратор (полный доступ)")
        self.admin_radio.setChecked(True)
        self.operator_radio = QRadioButton("Оператор (ввод и редактирование данных)")
        self.user_radio = QRadioButton("Пользователь (только просмотр)")

        role_layout.addWidget(self.admin_radio)
        role_layout.addWidget(self.operator_radio)
        role_layout.addWidget(self.user_radio)
        layout.addWidget(role_group)

        # Поля ввода
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Логин:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)
        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()

        self.login_btn = QPushButton("Войти в систему")
        self.login_btn.clicked.connect(self.authenticate)
        self.login_btn.setDefault(True)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: 192140;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        self.manuals_btn = QPushButton("📖 Руководства")
        self.manuals_btn.clicked.connect(self.show_manuals_menu)

        self.exit_btn = QPushButton("Выход")
        self.exit_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.manuals_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.exit_btn)
        layout.addLayout(button_layout)

        # Подсказка
        hint_label = QLabel("Подсказка: admin / admin123, operator / operator123, user / user123")
        hint_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic; margin-top: 10px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)

        # Статус
        self.status_label = QLabel("Введите учетные данные для выбранной роли")
        self.status_label.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self):
        """Аутентификация пользователя"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.status_label.setText("Ошибка: Заполните все поля!")
            self.status_label.setStyleSheet("color: red;")
            return

        # Проверка учетных данных в зависимости от выбранной роли
        if self.admin_radio.isChecked():
            # Администратор
            if username == "admin" and self.hash_password(password) == self.hash_password("admin123"):
                self.role = 'ADMIN'
                self.accept()
            else:
                self.status_label.setText("Неверные учетные данные администратора")
                self.status_label.setStyleSheet("color: red;")

        elif self.operator_radio.isChecked():
            # Оператор
            if username == "operator" and self.hash_password(password) == self.hash_password("operator123"):
                self.role = 'OPERATOR'
                self.accept()
            else:
                self.status_label.setText("Неверные учетные данные оператора")
                self.status_label.setStyleSheet("color: red;")

        else:  # Пользователь
            if username == "user" and self.hash_password(password) == self.hash_password("user123"):
                self.role = 'USER'
                self.accept()
            else:
                self.status_label.setText("Неверные учетные данные пользователя")
                self.status_label.setStyleSheet("color: red;")

    def show_manuals_menu(self):
        """Показать меню руководств"""
        menu = QMenu(self)

        admin_action = QAction("📕 Руководство администратора", self)
        admin_action.triggered.connect(lambda: self.show_manual('ADMIN'))

        operator_action = QAction("📗 Руководство оператора", self)
        operator_action.triggered.connect(lambda: self.show_manual('OPERATOR'))

        user_action = QAction("📘 Руководство пользователя", self)
        user_action.triggered.connect(lambda: self.show_manual('USER'))

        menu.addAction(admin_action)
        menu.addAction(operator_action)
        menu.addAction(user_action)

        menu.exec(self.manuals_btn.mapToGlobal(self.manuals_btn.rect().bottomLeft()))

    def show_manual(self, role):
        """Показать руководство для роли"""
        # Создаем временный объект для получения руководства
        temp_dialog = RoleSelectionDialog()
        manual_content = temp_dialog.get_manual_content(role)
        manual_title = f"Руководство {USER_ROLES[role]}"

        dialog = QDialog(self)
        dialog.setWindowTitle(manual_title)
        dialog.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Текст руководства
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(manual_content)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: 192140;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        layout.addWidget(text_edit)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.setLayout(layout)
        dialog.exec()


class RoleSelectionDialog(QDialog):
    """Диалог выбора роли пользователя с доступом к руководствам"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Выбор роли пользователя")
        self.setFixedSize(550, 450)
        self.selected_role = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Вход в систему зачисления абитуриентов")
        title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            margin: 10px;
            color: #2c3e50;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Описание
        desc = QLabel("Выберите вашу роль для доступа к системе:")
        desc.setStyleSheet("font-size: 12px; color: #666; margin: 10px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        # Фрейм с кнопками ролей
        roles_frame = QFrame()
        roles_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        roles_layout = QVBoxLayout(roles_frame)

        # Кнопка Пользователь
        self.user_btn = QPushButton("👤  ПОЛЬЗОВАТЕЛЬ")
        self.user_btn.setToolTip("Только просмотр информации и отчетов")
        self.user_btn.clicked.connect(lambda: self.select_role('USER'))

        # Кнопка Оператор
        self.operator_btn = QPushButton("👷  ОПЕРАТОР")
        self.operator_btn.setToolTip("Ввод и редактирование данных абитуриентов")
        self.operator_btn.clicked.connect(lambda: self.select_role('OPERATOR'))

        # Кнопка Администратор
        self.admin_btn = QPushButton("🔧  АДМИНИСТРАТОР")
        self.admin_btn.setToolTip("Полный доступ к системе и настройкам")
        self.admin_btn.clicked.connect(lambda: self.select_role('ADMIN'))

        # Настройка стилей кнопок
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                margin: 8px;
                border: 2px solid transparent;
            }
            QPushButton:hover {
                border: 2px solid #3498db;
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
        """

        self.user_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #3498db;
                color: 192140;
            }
        """)

        self.operator_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #2ecc71;
                color: 192140;
            }
        """)

        self.admin_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #e74c3c;
                color: 192140;
            }
        """)

        roles_layout.addWidget(self.user_btn)
        roles_layout.addWidget(self.operator_btn)
        roles_layout.addWidget(self.admin_btn)

        layout.addWidget(roles_frame)

        # Кнопки руководств
        manuals_frame = QFrame()
        manuals_frame.setFrameStyle(QFrame.Shape.NoFrame)
        manuals_layout = QHBoxLayout(manuals_frame)

        self.user_manual_btn = QPushButton("📘 Руководство пользователя")
        self.user_manual_btn.clicked.connect(lambda: self.show_manual('USER'))
        self.user_manual_btn.setStyleSheet("""
            QPushButton {
                background-color: #192140;
                padding: 8px;
                border-radius: 5px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #192140;
            }
        """)

        self.operator_manual_btn = QPushButton("📗 Руководство оператора")
        self.operator_manual_btn.clicked.connect(lambda: self.show_manual('OPERATOR'))
        self.operator_manual_btn.setStyleSheet(self.user_manual_btn.styleSheet())

        self.admin_manual_btn = QPushButton("📕 Руководство администратора")
        self.admin_manual_btn.clicked.connect(lambda: self.show_manual('ADMIN'))
        self.admin_manual_btn.setStyleSheet(self.user_manual_btn.styleSheet())

        manuals_layout.addWidget(self.user_manual_btn)
        manuals_layout.addWidget(self.operator_manual_btn)
        manuals_layout.addWidget(self.admin_manual_btn)

        layout.addWidget(manuals_frame)
        layout.addStretch()

        self.setLayout(layout)

    def select_role(self, role):
        """Выбор роли"""
        self.selected_role = role
        self.accept()

    def show_manual(self, role):
        """Показать руководство для выбранной роли"""
        manual_content = self.get_manual_content(role)
        manual_title = f"Руководство {USER_ROLES[role]}"

        dialog = QDialog(self)
        dialog.setWindowTitle(manual_title)
        dialog.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Текст руководства
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(manual_content)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: 192140;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        layout.addWidget(text_edit)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.setLayout(layout)
        dialog.exec()

    def get_manual_content(self, role):
        """Получить содержимое руководства для роли"""
        if role == 'USER':
            return self.get_user_manual()
        elif role == 'OPERATOR':
            return self.get_operator_manual()
        else:  # ADMIN
            return self.get_admin_manual()

    def get_user_manual(self):
        """Руководство пользователя"""
        return """
        <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                📘 Руководство пользователя системы зачисления абитуриентов
            </h1>

            <h2 style="color: #34495e;">🎯 Назначение системы</h2>
            <p>Система предназначена для <strong>просмотра информации</strong> о процессе зачисления абитуриентов в учебное заведение.</p>

            <h2 style="color: #34495e;">👤 Права доступа пользователя:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db;">
                <h3 style="color: #27ae60;">✅ Разрешенные действия:</h3>
                <ul>
                    <li>📊 <strong>Просмотр списка всех абитуриентов</strong></li>
                    <li>🔍 <strong>Поиск по базе данных</strong> (по ФИО, баллам, статусу)</li>
                    <li>📈 <strong>Просмотр отчетов и статистики</strong></li>
                    <li>🎓 <strong>Просмотр списков зачисленных/незачисленных</strong></li>
                    <li>📋 <strong>Просмотр кандидатов на собеседование</strong></li>
                </ul>

                <h3 style="color: #e74c3c;">🚫 Запрещенные действия:</h3>
                <ul>
                    <li>❌ Добавление новых абитуриентов</li>
                    <li>❌ Редактирование данных абитуриентов</li>
                    <li>❌ Удаление записей из базы данных</li>
                    <li>❌ Изменение настроек системы (проходной балл, количество мест)</li>
                    <li>❌ Выполнение отбора абитуриентов</li>
                    <li>❌ Настройка подключения к базе данных</li>
                </ul>
            </div>

            <h2 style="color: #34495e;">📋 Основные разделы системы:</h2>
            <ol>
                <li><strong>Вкладка "Абитуриенты"</strong> - полный список абитуриентов с возможностью фильтрации</li>
                <li><strong>Вкладка "Отбор"</strong> - результаты автоматического отбора и статистика</li>
                <li><strong>Вкладка "Отчеты"</strong> - сводные данные и аналитика</li>
            </ol>

            <h2 style="color: #34495e;">💡 Советы по использованию:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px;">
                <ul>
                    <li>Используйте <strong>поле поиска</strong> для быстрого нахождения абитуриентов</li>
                    <li>Дважды щелкните по строке в таблице для просмотра детальной информации</li>
                    <li>Обращайте внимание на цветовые индикаторы статусов:
                        <ul>
                            <li><span style="color: #27ae60; font-weight: bold;">Зеленый</span> - Зачислен</li>
                            <li><span style="color: #f39c12; font-weight: bold;">Оранжевый</span> - На собеседовании</li>
                            <li><span style="color: #e74c3c; font-weight: bold;">Красный</span> - Не прошел</li>
                        </ul>
                    </li>
                </ul>
            </div>

            <h2 style="color: #34495e;">🆘 Техническая поддержка:</h2>
            <p>При возникновении проблем:</p>
            <ol>
                <li>Проверьте подключение к базе данных</li>
                <li>Обратитесь к администратору системы</li>
                <li>Сообщите о проблеме в техническую поддержку</li>
            </ol>

            <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #7f8c8d;">
                <p><strong>Версия системы:</strong> 2.0 (с ролевой системой)</p>
                <p><strong>Дата составления:</strong> """ + datetime.now().strftime("%d.%m.%Y") + """</p>
            </div>
        </div>
        """

    def get_operator_manual(self):
        """Руководство оператора"""
        return """
        <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #2ecc71; padding-bottom: 10px;">
                📗 Руководство оператора системы зачисления абитуриентов
            </h1>

            <h2 style="color: #34495e;">🎯 Назначение системы</h2>
            <p>Система предназначена для <strong>ввода и редактирования данных</strong> абитуриентов, проведения собеседований и работы с кандидатами.</p>

            <h2 style="color: #34495e;">👷 Права доступа оператора:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px; border-left: 4px solid #2ecc71;">
                <h3 style="color: #27ae60;">✅ Разрешенные действия:</h3>
                <ul>
                    <li>✅ <strong>Все права пользователя</strong> (просмотр, поиск, отчеты)</li>
                    <li>➕ <strong>Добавление новых абитуриентов</strong> в систему</li>
                    <li>✏️ <strong>Редактирование данных</strong> существующих абитуриентов</li>
                    <li>🗑️ <strong>Удаление абитуриентов</strong> (с подтверждением)</li>
                    <li>📋 <strong>Проведение собеседований</strong> с кандидатами</li>
                    <li>🎯 <strong>Выполнение автоматического отбора</strong> абитуриентов</li>
                    <li>💾 <strong>Создание резервных копий</strong> данных</li>
                </ul>

                <h3 style="color: #e74c3c;">🚫 Запрещенные действия:</h3>
                <ul>
                    <li>❌ Изменение настроек системы (проходной балл, количество мест)</li>
                    <li>❌ Настройка подключения к базе данных</li>
                    <li>❌ Создание/удаление баз данных</li>
                    <li>❌ Изменение структуры базы данных</li>
                </ul>
            </div>

            <h2 style="color: #34495e;">📋 Пошаговое руководство:</h2>

            <h3 style="color: #2980b9;">1. Добавление нового абитуриента:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <ol>
                    <li>Перейдите на вкладку <strong>"Абитуриенты"</strong></li>
                    <li>Заполните все обязательные поля формы:
                        <ul>
                            <li><strong>ФИО</strong> - полностью (обязательное поле)</li>
                            <li><strong>Email</strong> - корректный email адрес (обязательное поле)</li>
                            <li><strong>Баллы по экзаменам</strong> (от 0 до 100)</li>
                            <li><strong>Телефон</strong> в формате 8-920-345-32-38</li>
                            <li><strong>Дата рождения</strong> в формате ГГГГ-ММ-ДД</li>
                            <li><strong>Готовность к договору</strong> (платное обучение)</li>
                        </ul>
                    </li>
                    <li>Нажмите кнопку <strong style="color: #27ae60;">"➕ Добавить"</strong></li>
                    <li>Проверьте, что абитуриент появился в таблице</li>
                </ol>
            </div>

            <h3 style="color: #2980b9;">2. Редактирование данных абитуриента:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <ol>
                    <li>Дважды щелкните по абитуриенту в таблице</li>
                    <li>Данные автоматически загрузятся в форму</li>
                    <li>Внесите необходимые изменения</li>
                    <li>Нажмите кнопку <strong style="color: #3498db;">"✏️ Обновить"</strong></li>
                    <li>Проверьте обновление данных в таблице</li>
                </ol>
            </div>

            <h3 style="color: #2980b9;">3. Удаление абитуриента:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <ol>
                    <li>Выберите абитуриента в таблице (двойной щелчок)</li>
                    <li>Нажмите кнопку <strong style="color: #e74c3c;">"🗑️ Удалить"</strong></li>
                    <li>Подтвердите удаление в диалоговом окне</li>
                    <li>Абитуриент будет удален из всех связанных таблиц</li>
                </ol>
            </div>

            <h3 style="color: #2980b9;">4. Проведение собеседования:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <ol>
                    <li>После автоматического отбора перейдите на вкладку <strong>"Отбор"</strong></li>
                    <li>Нажмите кнопку <strong>"📋 Список на собеседование"</strong></li>
                    <li>В диалоговом окне отметьте кандидатов для зачисления</li>
                    <li>Добавьте комментарии с указанием причины решения</li>
                    <li>Нажмите <strong style="color: #27ae60;">"✅ Принять решения"</strong></li>
                    <li>Система автоматически распределит кандидатов на бюджетные/платные места</li>
                </ol>
            </div>

            <h3 style="color: #2980b9;">5. Выполнение автоматического отбора:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <ol>
                    <li>Убедитесь, что все абитуриенты внесены в систему</li>
                    <li>На вкладке <strong>"Отбор"</strong> нажмите <strong>"🎯 Выполнить отбор"</strong></li>
                    <li>Система автоматически:
                        <ul>
                            <li>Отсортирует абитуриентов по баллам</li>
                            <li>Распределит бюджетные места</li>
                            <li>Распределит платные места</li>
                            <li>Определит кандидатов на собеседование</li>
                            <li>Обновит статусы всех абитуриентов</li>
                        </ul>
                    </li>
                </ol>
            </div>

            <h2 style="color: #34495e;">⚠️ Важные замечания:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px; border: 1px solid #ffeaa7;">
                <ul>
                    <li>При добавлении абитуриента система автоматически вычисляет общий балл</li>
                    <li>Телефон автоматически форматируется в стандартный формат</li>
                    <li>Статус абитуриента устанавливается при отборе автоматически</li>
                    <li>Все изменения логируются в системе</li>
                    <li>Резервные копии создаются с временной меткой в имени файла</li>
                    <li>При удалении абитуриента удаляются все связанные записи</li>
                </ul>
            </div>

            <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #7f8c8d;">
                <p><strong>Версия системы:</strong> 2.0 (с ролевой системой)</p>
                <p><strong>Дата составления:</strong> """ + datetime.now().strftime("%d.%m.%Y") + """</p>
            </div>
        </div>
        """

    def get_admin_manual(self):
        """Руководство администратора"""
        return """
        <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 10px;">
                📕 Руководство администратора системы зачисления абитуриентов
            </h1>

            <h2 style="color: #34495e;">🎯 Назначение системы</h2>
            <p>Полное администрирование системы зачисления абитуриентов, включая настройку подключений, управление базой данных и конфигурацию системы.</p>

            <h2 style="color: #34495e;">🔧 Права доступа администратора:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px; border-left: 4px solid #e74c3c;">
                <h3 style="color: #27ae60;">✅ Полный доступ ко всем функциям:</h3>
                <ul>
                    <li>✅ <strong>Все права оператора и пользователя</strong></li>
                    <li>⚙️ <strong>Настройка параметров системы</strong> (проходной балл, количество мест)</li>
                    <li>🔌 <strong>Настройка подключения к базе данных</strong></li>
                    <li>🗄️ <strong>Создание и восстановление резервных копий</strong></li>
                    <li>🏗️ <strong>Создание/удаление базы данных</strong></li>
                    <li>📊 <strong>Полный доступ к отчетам и статистике</strong></li>
                    <li>🔐 <strong>Управление доступом к системе</strong></li>
                </ul>
            </div>

            <h2 style="color: #34495e;">📋 Пошаговое руководство:</h2>

            <h3 style="color: #c0392b;">1. Начальная настройка системы:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <h4 style="color: #e74c3c;">Создание новой базы данных:</h4>
                <ol>
                    <li>В диалоге подключения выберите <strong>"Создать новую базу данных"</strong></li>
                    <li>Укажите параметры подключения:
                        <ul>
                            <li><strong>Имя сервера</strong> (например: DESKTOP-9DIC6CU\SQLEXPRESS)</li>
                            <li><strong>Название базы данных</strong></li>
                            <li><strong>Тип аутентификации</strong> (Windows или SQL Server)</li>
                            <li>При использовании SQL Server - логин и пароль</li>
                        </ul>
                    </li>
                    <li>Нажмите <strong>"Создать базу данных"</strong></li>
                    <li>Система автоматически создаст:
                        <ul>
                            <li>Базу данных с указанным именем</li>
                            <li>Все необходимые таблицы (applicants, settings, selected_applicants)</li>
                            <li>Настройки по умолчанию</li>
                        </ul>
                    </li>
                </ol>

                <h4 style="color: #e74c3c;">Подключение к существующей базе:</h4>
                <ol>
                    <li>Выберите <strong>"Открыть существующую базу данных"</strong></li>
                    <li>Укажите параметры подключения</li>
                    <li>Нажмите <strong>"Тестировать подключение"</strong></li>
                    <li>При успешном тесте нажмите <strong>"Подключиться"</strong></li>
                </ol>
            </div>

            <h3 style="color: #c0392b;">2. Настройка параметров отбора:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <ol>
                    <li>Перейдите на вкладку <strong>"Отбор"</strong></li>
                    <li>Установите необходимые значения:
                        <ul>
                            <li><strong>Проходной балл</strong> - минимальный суммарный балл для зачисления</li>
                            <li><strong>Бюджетные места</strong> - количество бюджетных мест</li>
                            <li><strong>Платные места</strong> - количество платных мест</li>
                        </ul>
                    </li>
                    <li>Изменения сохраняются автоматически в базу данных</li>
                </ol>
            </div>

            <h3 style="color: #c0392b;">3. Управление базой данных:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <h4 style="color: #e74c3c;">Создание резервной копии:</h4>
                <ol>
                    <li>Меню <strong>Сервис → Создать резервную копию</strong></li>
                    <li>Или кнопка на вкладке <strong>"Отчеты"</strong></li>
                    <li>Файл сохраняется в формате SQL с временной меткой</li>
                    <li>Содержит данные всех таблиц и настроек</li>
                </ol>

                <h4 style="color: #e74c3c;">Смена подключения:</h4>
                <ol>
                    <li>Меню <strong>Сервис → Настройки подключения</strong></li>
                    <li>Укажите новые параметры подключения</li>
                    <li>Приложение переподключится к новой базе</li>
                </ol>
            </div>

            <h3 style="color: #c0392b;">4. Выполнение отбора:</h3>
            <div style="background: #192140; padding: 10px; border-radius: 5px; margin-left: 20px;">
                <ol>
                    <li>Убедитесь, что все абитуриенты внесены в систему</li>
                    <li>На вкладке <strong>"Отбор"</strong> нажмите <strong>"🎯 Выполнить отбор"</strong></li>
                    <li>Система автоматически выполнит отбор по алгоритму:
                        <ul>
                            <li><strong>Приоритет 1:</strong> Абитуриенты без договора с баллом > проходного → Бюджет</li>
                            <li><strong>Приоритет 2:</strong> Абитуриенты с договором с баллом > проходного → Бюджет (если есть места)</li>
                            <li><strong>Приоритет 3:</strong> Абитуриенты с договором с баллом = проходному → Платное</li>
                            <li><strong>Приоритет 4:</strong> Абитуриенты без договора с баллом = проходному → Собеседование</li>
                            <li><strong>Приоритет 5:</strong> Абитуриенты с договором с баллом < проходного → Платное (если есть места)</li>
                        </ul>
                    </li>
                </ol>
            </div>

            <h2 style="color: #34495e;">🔐 Требования к правам доступа SQL Server:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px; border: 1px solid #ffeaa7;">
                <p>Для создания баз данных требуются следующие права на SQL Server:</p>
                <ul>
                    <li><code>CREATE DATABASE</code> - создание баз данных</li>
                    <li><code>ALTER DATABASE</code> - изменение баз данных</li>
                    <li><code>DROP DATABASE</code> - удаление баз данных</li>
                    <li>Роль <code>dbcreator</code> - роль создателя баз данных</li>
                    <li>При использовании Windows аутентификации - права администратора</li>
                </ul>
                <p><strong>Решение проблем с правами:</strong></p>
                <ol>
                    <li>Используйте учетную запись администратора SQL Server</li>
                    <li>Попросите администратора выдать права CREATE DATABASE</li>
                    <li>Используйте существующую базу данных с готовыми таблицами</li>
                </ol>
            </div>

            <h2 style="color: #34495e;">⚙️ Техническая информация о системе:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px;">
                <ul>
                    <li><strong>СУБД:</strong> Microsoft SQL Server</li>
                    <li><strong>ODBC Driver:</strong> 17 for SQL Server</li>
                    <li><strong>Основные таблицы:</strong>
                        <ul>
                            <li><code>applicants</code> - данные абитуриентов</li>
                            <li><code>settings</code> - настройки системы</li>
                            <li><code>selected_applicants</code> - результаты отбора</li>
                        </ul>
                    </li>
                    <li><strong>Период хранения данных:</strong> бессрочно</li>
                    <li><strong>Формат резервных копий:</strong> SQL-скрипты</li>
                </ul>
            </div>

            <h2 style="color: #34495e;">📞 Контакты для технической поддержки:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px;">
                <ul>
                    <li><strong>Разработчик системы:</strong> [Ваши контакты]</li>
                    <li><strong>Администратор БД:</strong> [Контакты администратора]</li>
                    <li><strong>Техническая поддержка:</strong> [Контакты поддержки]</li>
                    <li><strong>Аварийные ситуации:</strong> [Экстренные контакты]</li>
                </ul>
            </div>

            <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #7f8c8d;">
                <p><strong>Версия системы:</strong> 2.0 (с ролевой системой)</p>
                <p><strong>Дата составления:</strong> """ + datetime.now().strftime("%d.%m.%Y") + """</p>
                <p><strong>Дата последнего обновления:</strong> """ + datetime.now().strftime("%d.%m.%Y") + """</p>
            </div>
        </div>
        """


class DatabaseConnectionDialog(QDialog):
    """Диалог для настройки подключения к базе данных с выбором создания/открытия"""

    def __init__(self, parent=None, user_role='USER'):
        super().__init__(parent)
        self.user_role = user_role
        role_name = USER_ROLES.get(user_role, 'Неизвестно')
        self.setWindowTitle(f"Настройка подключения к базе данных СмолГУ: [{role_name}]")
        self.setFixedSize(700, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setWindowIcon(QIcon('logo.png'))

        # Добавляем фото в диалог подключения к БД
        photo_label = QLabel()
        photo_pixmap = QPixmap('logo.png')

        if not photo_pixmap.isNull():
            photo_pixmap = photo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
            photo_label.setPixmap(photo_pixmap)
            photo_label.setFixedSize(80, 80)
            photo_label.setStyleSheet("border: 2px solid #3498db; border-radius: 5px; margin-bottom: 10px;")
        else:
            photo_label.setText("Лого")
            photo_label.setFixedSize(80, 80)
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            photo_label.setStyleSheet("""
                       border: 2px solid #3498db; 
                       border-radius: 5px; 
                       background-color: #192140; 
                       color: #3498db; 
                       font-weight: bold;
                       margin-bottom: 10px;
                   """)

        layout.addWidget(photo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Отображение текущей роли
        role_label = QLabel(f"Роль: {USER_ROLES.get(self.user_role, 'Неизвестно')}")
        role_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            padding: 8px;
            background-color: #192140;
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(role_label)

        # Для пользователя ограничиваем доступ
        if self.user_role == 'USER':
            message = QLabel("⚠️ Для роли 'Пользователь' доступно только подключение к существующей базе данных")
            message.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold; padding: 20px;")
            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(message)

        # Заголовок
        title = QLabel("Настройки подключения к SQL Server")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Радио-кнопки для выбора действия (только для ADMIN)
        if self.user_role == 'ADMIN':
            action_group = QGroupBox("Выберите действие")
            action_layout = QVBoxLayout(action_group)

            self.open_db_radio = QRadioButton("Открыть существующую базу данных")
            self.open_db_radio.setChecked(True)
            self.create_db_radio = QRadioButton("Создать новую базу данных")

            self.open_db_radio.toggled.connect(self.toggle_action_type)
            self.create_db_radio.toggled.connect(self.toggle_action_type)

            action_layout.addWidget(self.open_db_radio)
            action_layout.addWidget(self.create_db_radio)

            layout.addWidget(action_group)
        else:
            # Для USER и OPERATOR - только открытие существующей БД
            self.open_db_radio = QRadioButton("Открыть существующую базу данных")
            self.open_db_radio.setChecked(True)
            self.open_db_radio.toggled.connect(self.toggle_action_type)

            self.create_db_radio = QRadioButton("Создать новую базу данных")
            self.create_db_radio.setEnabled(False)
            self.create_db_radio.toggled.connect(self.toggle_action_type)

            if self.user_role == 'OPERATOR':
                self.create_db_radio.setToolTip("Недоступно для роли Оператор. Обратитесь к администратору.")

        # Поля ввода
        form_layout = QFormLayout()

        self.server_input = QLineEdit("INFOLORD\\SQLEXPRESS")
        self.database_input = QLineEdit("AdmissionDB")
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Сервер:", self.server_input)
        form_layout.addRow("База данных:", self.database_input)

        # Для USER и OPERATOR скрываем поля аутентификации (используем Windows аутентификацию)
        if self.user_role == 'ADMIN':
            form_layout.addRow("Имя пользователя:", self.username_input)
            form_layout.addRow("Пароль:", self.password_input)

        layout.addLayout(form_layout)

        # Радио-кнопки для типа аутентификации (только для ADMIN)
        if self.user_role == 'ADMIN':
            auth_group = QGroupBox("Тип аутентификации")
            auth_layout = QVBoxLayout(auth_group)

            self.windows_auth_radio = QRadioButton("Аутентификация Windows")
            self.windows_auth_radio.setChecked(True)
            self.sql_auth_radio = QRadioButton("Аутентификация SQL Server")

            self.windows_auth_radio.toggled.connect(self.toggle_auth_type)
            self.sql_auth_radio.toggled.connect(self.toggle_auth_type)

            auth_layout.addWidget(self.windows_auth_radio)
            auth_layout.addWidget(self.sql_auth_radio)

            layout.addWidget(auth_group)
        else:
            # Для USER и OPERATOR используем только Windows аутентификацию
            self.windows_auth_radio = QRadioButton("Аутентификация Windows (используется по умолчанию)")
            self.windows_auth_radio.setChecked(True)
            self.windows_auth_radio.setEnabled(False)
            layout.addWidget(self.windows_auth_radio)

        # Кнопки тестирования и сохранения
        button_layout = QHBoxLayout()

        self.test_btn = QPushButton("Тестировать подключение")
        self.test_btn.clicked.connect(self.test_connection)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: 192140;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)

        # Кнопка создания БД (только для ADMIN)
        if self.user_role == 'ADMIN':
            self.create_btn = QPushButton("Создать базу данных")
            self.create_btn.clicked.connect(self.create_database)
            self.create_btn.setEnabled(False)
            self.create_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: 192140;
                    padding: 8px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)

        self.save_btn = QPushButton("Подключиться")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: 192140;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: 192140;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)

        button_layout.addWidget(self.test_btn)
        if self.user_role == 'ADMIN':
            button_layout.addWidget(self.create_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # Статус
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.toggle_action_type()
        if self.user_role == 'ADMIN':
            self.toggle_auth_type()

    def toggle_action_type(self):
        """Переключение типа действия"""
        if hasattr(self, 'create_btn') and self.create_db_radio.isChecked():
            self.create_btn.setEnabled(True)
            self.test_btn.setEnabled(False)
            self.status_label.setText("Режим создания новой базы данных")
        else:
            if hasattr(self, 'create_btn'):
                self.create_btn.setEnabled(False)
            self.test_btn.setEnabled(True)
            self.status_label.setText("Режим открытия существующей базы данных")

    def toggle_auth_type(self):
        """Переключение типа аутентификации (только для ADMIN)"""
        if self.user_role == 'ADMIN' and hasattr(self, 'sql_auth_radio'):
            if self.sql_auth_radio.isChecked():
                self.username_input.setEnabled(True)
                self.password_input.setEnabled(True)
            else:
                self.username_input.setEnabled(False)
                self.password_input.setEnabled(False)

    def test_connection(self):
        """Тестирование подключения к существующей базе данных"""
        try:
            conn_str = self.build_connection_string()
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Проверка существования базы данных
            cursor.execute("SELECT name FROM sys.databases WHERE name = ?",
                           self.database_input.text())
            db_exists = cursor.fetchone()

            if not db_exists:
                self.status_label.setText(f"База данных '{self.database_input.text()}' не найдена!")
                self.status_label.setStyleSheet("color: red;")
                conn.close()
                return False
            else:
                # Проверка существования таблиц
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_type = 'BASE TABLE'
                """)
                table_count = cursor.fetchone()[0]

                if table_count == 0:
                    self.status_label.setText(f"База '{self.database_input.text()}' пуста. Создайте таблицы.")
                    self.status_label.setStyleSheet("color: oangre;")
                else:
                    self.status_label.setText(f"Подключение успешно! Таблиц: {table_count}")
                    self.status_label.setStyleSheet("color: green;")

            conn.close()
            return True

        except Exception as e:
            self.status_label.setText(f"Ошибка подключения: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            return False

    def create_database(self):
        """Создание новой базы данных (только для ADMIN)"""
        try:
            db_name = self.database_input.text().strip()
            if not db_name:
                self.status_label.setText("Введите имя базы данных!")
                self.status_label.setStyleSheet("color: red;")
                return

            # Сначала подключаемся к master для создания БД
            master_conn_str = self.build_master_connection_string()

            try:
                conn = pyodbc.connect(master_conn_str, autocommit=True)
            except Exception as conn_error:
                self.status_label.setText(f"Ошибка подключения к master: {str(conn_error)}")
                self.status_label.setStyleSheet("color: red;")
                return

            cursor = conn.cursor()

            try:
                # Проверяем, существует ли уже база данных
                cursor.execute("SELECT name FROM sys.databases WHERE name = ?", db_name)
                db_exists = cursor.fetchone()

                if db_exists:
                    reply = QMessageBox.question(self, "База данных существует",
                                                 f"База данных '{db_name}' уже существует.\n"
                                                 f"Использовать существующую базу?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                    if reply == QMessageBox.StandardButton.Yes:
                        conn.close()
                        self.status_label.setText(f"Будет использована существующая база '{db_name}'")
                        self.status_label.setStyleSheet("color: green;")
                        return
                    else:
                        # Предлагаем пересоздать базу
                        reply2 = QMessageBox.question(self, "Пересоздать базу",
                                                      f"Удалить базу '{db_name}' и создать новую?\n"
                                                      f"Все данные будут потеряны!",
                                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                        if reply2 == QMessageBox.StandardButton.Yes:
                            try:
                                # Закрываем все соединения с базой
                                cursor.execute(f"""
                                    USE master;
                                    ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                                    DROP DATABASE [{db_name}];
                                """)
                                self.status_label.setText(f"База '{db_name}' удалена. Создаем новую...")
                                self.status_label.setStyleSheet("color: orange;")
                                QApplication.processEvents()  # Обновляем интерфейс
                            except Exception as drop_error:
                                self.status_label.setText(f"Ошибка удаления базы: {str(drop_error)}")
                                self.status_label.setStyleSheet("color: red;")
                                conn.close()
                                return
                        else:
                            conn.close()
                            return

                # Создаем новую базу данных
                self.status_label.setText(f"Создаем базу '{db_name}'...")
                self.status_label.setStyleSheet("color: orange;")
                QApplication.processEvents()  # Обновляем интерфейс

                # Простая команда создания базы
                cursor.execute(f"CREATE DATABASE [{db_name}]")

                self.status_label.setText(f"База '{db_name}' создана. Создаем таблицы...")
                self.status_label.setStyleSheet("color: orange;")
                QApplication.processEvents()  # Обновляем интерфейс

                conn.close()

                # Теперь подключаемся к новой базе и создаем таблицы
                db_conn_str = self.build_connection_string()

                # Даем SQL Server время на создание базы
                import time
                time.sleep(1)

                try:
                    db_conn = pyodbc.connect(db_conn_str, autocommit=True)
                except Exception as db_conn_error:
                    # Если не удалось подключиться сразу, ждем еще
                    time.sleep(2)
                    db_conn = pyodbc.connect(db_conn_str, autocommit=True)

                db_cursor = db_conn.cursor()

                # Создаем таблицы
                tables_sql = [
                    """
                    CREATE TABLE applicants (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        full_name NVARCHAR(100) NOT NULL,
                        birth_date DATE,
                        contact_phone NVARCHAR(20),
                        email NVARCHAR(100),
                        exam1_score INT DEFAULT 0,
                        exam2_score INT DEFAULT 0,
                        exam3_score INT DEFAULT 0,
                        total_score INT DEFAULT 0,
                        contract_willing BIT DEFAULT 0,
                        admission_status NVARCHAR(50) DEFAULT 'Не рассмотрено',
                        registration_date DATETIME DEFAULT GETDATE()
                    )
                    """,
                    """
                    CREATE TABLE settings (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        setting_name NVARCHAR(100) NOT NULL,
                        setting_value NVARCHAR(255),
                        description NVARCHAR(255)
                    )
                    """,
                    """
                    CREATE TABLE selected_applicants (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        applicant_id INT FOREIGN KEY REFERENCES applicants(id),
                        selection_date DATETIME DEFAULT GETDATE(),
                        selection_type NVARCHAR(50),
                        selection_reason NVARCHAR(255)
                    )
                    """
                ]

                for sql in tables_sql:
                    try:
                        db_cursor.execute(sql)
                    except Exception as table_error:
                        self.status_label.setText(f"Ошибка создания таблицы: {str(table_error)}")
                        self.status_label.setStyleSheet("color: red;")
                        db_conn.close()
                        return

                # Вставка настроек по умолчанию
                settings_sql = [
                    ("passing_score", "150", "Проходной балл для зачисления"),
                    ("budget_seats", "5", "Количество бюджетных мест"),
                    ("paid_seats", "5", "Количество платных мест")
                ]

                for name, value, desc in settings_sql:
                    try:
                        db_cursor.execute("""
                            INSERT INTO settings (setting_name, setting_value, description)
                            VALUES (?, ?, ?)
                        """, name, value, desc)
                    except Exception as insert_error:
                        self.status_label.setText(f"Ошибка вставки настроек: {str(insert_error)}")
                        self.status_label.setStyleSheet("color: red;")
                        db_conn.close()
                        return

                db_conn.commit()
                db_conn.close()

                self.status_label.setText(f"База данных '{db_name}' успешно создана со всеми таблицами!")
                self.status_label.setStyleSheet("color: green;")

                # Переключаемся в режим открытия
                self.open_db_radio.setChecked(True)
                self.toggle_action_type()

            except pyodbc.Error as e:
                error_msg = str(e)
                if 'CREATE DATABASE permission denied' in error_msg:
                    self.status_label.setText("Ошибка: Нет прав на создание базы данных!")
                    self.status_label.setStyleSheet("color: red;")
                    QMessageBox.critical(self, "Ошибка прав доступа",
                                         "У вашей учетной записи нет прав на создание баз данных.\n"
                                         "Обратитесь к администратору SQL Server или:\n"
                                         "1. Используйте аутентификацию SQL Server с учетной записью администратора\n"
                                         "2. Попросите администратора выдать права CREATE DATABASE")
                elif 'already exists' in error_msg.lower():
                    self.status_label.setText(f"База данных '{db_name}' уже существует")
                    self.status_label.setStyleSheet("color: orange;")
                else:
                    self.status_label.setText(f"Ошибка SQL: {error_msg}")
                    self.status_label.setStyleSheet("color: red;")

            except Exception as e:
                self.status_label.setText(f"Неизвестная ошибка: {str(e)}")
                self.status_label.setStyleSheet("color: red;")

            finally:
                if 'conn' in locals():
                    try:
                        conn.close()
                    except:
                        pass

        except Exception as e:
            self.status_label.setText(f"Ошибка создания базы данных: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def build_master_connection_string(self):
        """Создание строки подключения к базе master"""
        server = self.server_input.text()

        if self.user_role == 'USER' or self.user_role == 'OPERATOR' or \
                (self.user_role == 'ADMIN' and hasattr(self,
                                                       'windows_auth_radio') and self.windows_auth_radio.isChecked()):
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"
        else:
            username = self.username_input.text()
            password = self.password_input.text()
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=master;UID={username};PWD={password};"

    def build_connection_string(self):
        """Создание строки подключения"""
        server = self.server_input.text()
        database = self.database_input.text()

        if self.user_role == 'USER' or self.user_role == 'OPERATOR' or \
                (self.user_role == 'ADMIN' and hasattr(self,
                                                       'windows_auth_radio') and self.windows_auth_radio.isChecked()):
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            username = self.username_input.text()
            password = self.password_input.text()
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

    def get_connection_string(self):
        """Получение строки подключения"""
        return self.build_connection_string()

    def get_database_name(self):
        """Получение имени базы данных"""
        return self.database_input.text()


class InterviewDialog(QDialog):
    """Диалог для собеседования с возможностью зачисления"""

    def __init__(self, parent=None, applicants=None):
        super().__init__(parent)
        self.applicants = applicants or []
        self.results = {}
        self.setWindowTitle("Собеседование - Решение о зачислении")
        self.setGeometry(300, 200, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("📋 Решение о зачислении на собеседовании")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Таблица с кандидатами
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ФИО", "Баллы", "Общий балл", "Договор", "Зачислить", "Комментарий"
        ])
        self.table.setRowCount(len(self.applicants))

        for row_idx, applicant in enumerate(self.applicants):
            # ФИО
            self.table.setItem(row_idx, 0, QTableWidgetItem(applicant[0]))

            # Баллы
            scores = f"{applicant[5]}/{applicant[6]}/{applicant[7]}"
            self.table.setItem(row_idx, 1, QTableWidgetItem(scores))

            # Общий балл
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(applicant[1])))

            # Договор
            contract_text = "Да" if applicant[8] == 1 else "Нет"
            self.table.setItem(row_idx, 3, QTableWidgetItem(contract_text))

            # Checkbox для зачисления
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row_idx, 4, checkbox_widget)

            # Поле для комментария
            comment_edit = QLineEdit()
            comment_edit.setPlaceholderText("Причина решения...")
            self.table.setCellWidget(row_idx, 5, comment_edit)

            # Сохраняем ссылки
            applicant_id = applicant[9] if len(applicant) > 9 else None
            self.results[row_idx] = {
                'id': applicant_id,
                'checkbox': checkbox,
                'comment': comment_edit,
                'name': applicant[0],
                'score': applicant[1],
                'contract': applicant[8]
            }

        layout.addWidget(self.table)

        # Кнопки
        button_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("✓ Зачислить всех")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: 192140;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        self.deselect_all_btn = QPushButton("✗ Отклонить всех")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: 192140;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        self.ok_btn = QPushButton("✅ Принять решения")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: 192140;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: 192140;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)

        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.deselect_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def select_all(self):
        """Выбрать всех кандидатов"""
        for row_idx in self.results:
            self.results[row_idx]['checkbox'].setChecked(True)

    def deselect_all(self):
        """Отклонить всех кандидатов"""
        for row_idx in self.results:
            self.results[row_idx]['checkbox'].setChecked(False)

    def get_results(self):
        """Получить результаты решения"""
        results = []
        for row_idx, data in self.results.items():
            results.append({
                'id': data['id'],
                'name': data['name'],
                'score': data['score'],
                'contract': data['contract'],
                'accepted': data['checkbox'].isChecked(),
                'comment': data['comment'].text()
            })
        return results


class ApplicantSystem(QMainWindow):
    def __init__(self, connection_string, database_name, user_role='USER'):
        super().__init__()
        self.connection_string = connection_string
        self.database_name = database_name
        self.user_role = user_role
        self.connection = None
        self.current_applicant_id = None
        self.passing_score = 150
        self.budget_seats = 5
        self.paid_seats = 5

        # Устанавливаем иконку окна (если файл существует)
        if os.path.exists('icon.png'):
            self.setWindowIcon(QIcon('icon.png'))

        self.setup_database()
        self.setup_ui()
        self.load_applicants()
        self.update_window_title()
        self.apply_role_restrictions()
        self.apply_user_permissions()

    def apply_user_permissions(self):
        """Применение ограничений для пользователя (только просмотр)"""
        if self.user_role == 'USER':
            # Блокируем поля ввода
            self.name_input.setReadOnly(True)
            self.birth_input.setReadOnly(True)
            self.phone_input.setReadOnly(True)
            self.email_input.setReadOnly(True)
            self.exam1_input.setReadOnly(True)
            self.exam2_input.setReadOnly(True)
            self.exam3_input.setReadOnly(True)
            self.contract_combo.setEnabled(False)

            # Блокируем кнопки
            self.add_btn.setEnabled(False)
            self.update_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

            # Блокируем элементы управления отбором
            if hasattr(self, 'select_btn'):
                self.select_btn.setEnabled(False)
            if hasattr(self, 'interview_btn'):
                self.interview_btn.setEnabled(False)
            if hasattr(self, 'passing_score_input'):
                self.passing_score_input.setReadOnly(True)
            if hasattr(self, 'budget_seats_input'):
                self.budget_seats_input.setReadOnly(True)
            if hasattr(self, 'paid_seats_input'):
                self.paid_seats_input.setReadOnly(True)

            # Блокируем кнопку резервного копирования
            if hasattr(self, 'backup_btn'):
                self.backup_btn.setEnabled(False)

            # Изменяем обработчик двойного клика для показа информации, а не редактирования
            self.applicants_table.doubleClicked.disconnect(self.load_applicant_data)
            self.applicants_table.doubleClicked.connect(self.load_applicant_data_view)

    def load_applicant_data_view(self, index):
        """Загрузка данных абитуриента только для просмотра (для пользователя)"""
        row = index.row()
        applicant_id_item = self.applicants_table.item(row, 0)
        if not applicant_id_item:
            return

        applicant_id = applicant_id_item.text()

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT full_name, birth_date, contact_phone, email,
                       exam1_score, exam2_score, exam3_score, total_score,
                       CASE WHEN contract_willing = 1 THEN 'Да' ELSE 'Нет' END,
                       admission_status
                FROM applicants WHERE id = ?
            """, applicant_id)

            data = cursor.fetchone()
            if data:
                info_text = f"📋 Данные абитуриента #{applicant_id}\n"
                info_text += "=" * 40 + "\n"
                info_text += f"ФИО: {data[0] or 'Не указано'}\n"
                info_text += f"Дата рождения: {data[1] or 'Не указано'}\n"
                info_text += f"Телефон: {data[2] or 'Не указано'}\n"
                info_text += f"Email: {data[3] or 'Не указано'}\n"
                info_text += f"Баллы: {data[4]}/{data[5]}/{data[6]}\n"
                info_text += f"Общий балл: {data[7]}\n"
                info_text += f"Договор: {data[8]}\n"
                info_text += f"Статус: {data[9]}\n"

                QMessageBox.information(self, "Просмотр данных абитуриента", info_text)

        except Exception as e:
            print(f"Ошибка загрузки данных абитуриента: {str(e)}")

    def setup_database(self):
        """Настройка подключения к базе данных"""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            self.load_settings()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения",
                                 f"Не удалось подключиться к базе данных:\n{str(e)}")

    def load_settings(self):
        """Загрузка настроек из базы данных"""
        try:
            cursor = self.connection.cursor()

            # Проходной балл
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'passing_score'")
            result = cursor.fetchone()
            if result:
                self.passing_score = int(result[0])

            # Бюджетные места
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'budget_seats'")
            result = cursor.fetchone()
            if result:
                self.budget_seats = int(result[0])

            # Платные места
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'paid_seats'")
            result = cursor.fetchone()
            if result:
                self.paid_seats = int(result[0])

        except Exception as e:
            print(f"Ошибка загрузки настроек: {str(e)}")

    def save_settings(self):
        """Сохранение настроек в базу данных"""
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                UPDATE settings 
                SET setting_value = ?
                WHERE setting_name = 'passing_score'
            """, self.passing_score)

            cursor.execute("""
                UPDATE settings 
                SET setting_value = ?
                WHERE setting_name = 'budget_seats'
            """, self.budget_seats)

            cursor.execute("""
                UPDATE settings 
                SET setting_value = ?
                WHERE setting_name = 'paid_seats'
            """, self.paid_seats)

            self.connection.commit()
        except Exception as e:
            print(f"Ошибка сохранения настроек: {str(e)}")

    def apply_role_restrictions(self):
        """Применение ограничений в зависимости от роли пользователя"""
        role_name = USER_ROLES.get(self.user_role, 'Неизвестно')

        # Обновляем заголовок окна с указанием роли
        self.setWindowTitle(f"🎓 Система зачисления абитуриентов [{role_name}]")

        # Показываем сообщение о текущей роли в статусной строке
        self.status_bar.showMessage(f"Роль: {role_name} | База данных: {self.database_name}", 5000)

    def format_phone_number(self, phone):
        """Форматирование номера телефона в формат 8-920-345-32-38"""
        if not phone:
            return phone

        # Удаляем все нецифровые символы
        digits = re.sub(r'\D', '', phone)

        if len(digits) == 11 and digits.startswith('8'):
            formatted = f"{digits[0]}-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:]}"
            return formatted
        elif len(digits) == 11 and digits.startswith('7'):
            # Если начинается с 7, меняем на 8
            formatted = f"8-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:]}"
            return formatted
        return phone

    def update_window_title(self):
        """Обновление заголовка окна"""
        role_name = USER_ROLES.get(self.user_role, 'Неизвестно')
        window_title = f"🎓 Система зачисления абитуриентов группы {self.database_name} [{role_name}]"
        self.setWindowTitle(window_title)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setGeometry(100, 100, 1400, 800)

        # Добавляем код для установки иконки приложения
        self.setWindowIcon(QIcon('logo.png'))

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)

        # Создаем горизонтальный layout для заголовка и фото
        header_layout = QHBoxLayout()

        # Добавляем фото в левом верхнем углу
        photo_label = QLabel()
        photo_pixmap = QPixmap('logo.png')  # Предполагаем, что файл называется logo.png

        # Проверяем, существует ли файл с фото
        if not photo_pixmap.isNull():
            # Масштабируем фото до нужного размера (например, 80x80)
            photo_pixmap = photo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
            photo_label.setPixmap(photo_pixmap)
            photo_label.setFixedSize(80, 80)
            photo_label.setStyleSheet("border: 2px solid #3498db; border-radius: 5px;")
        else:
            # Если фото не найдено, отображаем заглушку
            photo_label.setText("Лого")
            photo_label.setFixedSize(80, 80)
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            photo_label.setStyleSheet("""
                    border: 2px solid #3498db; 
                    border-radius: 5px; 
                    background-color: #192140; 
                    color: #3498db; 
                    font-weight: bold;
                """)

        # Добавляем фото в header_layout слева
        header_layout.addWidget(photo_label)
        header_layout.addSpacing(20)  # Добавляем отступ между фото и заголовком

        # Заголовок с указанием роли (переносим его в header_layout)
        role_name = USER_ROLES.get(self.user_role, 'Неизвестно')
        role_color = "#3498db" if self.user_role == 'USER' else "#2ecc71" if self.user_role == 'OPERATOR' else "#e74c3c"

        header_text = f"Система зачисления абитуриентов группы СмолГУ: {self.database_name}"
        header = QLabel(header_text)
        header.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background: linear-gradient(90deg, {role_color}, #2c3e50);
                color: 192140;
                border-radius: 10px;
                margin-bottom: 20px;
            """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавляем заголовок в header_layout с растяжением
        header_layout.addWidget(header, 1)

        # Добавляем header_layout в основной layout
        main_layout.addLayout(header_layout)

        # Создание вкладок
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background: 192140;
                }
                QTabBar::tab {
                    background: #192140;
                    padding: 10px 20px;
                    margin-right: 2px;
                    border-radius: 5px;
                }
                QTabBar::tab:selected {
                    background: #3498db;
                    color: 192140;
                }
            """)

        # Вкладка управления абитуриентами
        self.setup_applicants_tab(tab_widget)

        # Вкладка отбора (скрываем для пользователя)
        if self.user_role != 'USER':
            self.setup_selection_tab(tab_widget)

        # Вкладка отчетов
        self.setup_reports_tab(tab_widget)

        main_layout.addWidget(tab_widget)

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        role_name = USER_ROLES.get(self.user_role, 'Неизвестно')
        self.status_bar.showMessage(f"Роль: {role_name} | База данных: {self.database_name}")

        # Меню
        self.setup_menu()

    def setup_applicants_tab(self, tab_widget):
        """Настройка вкладки управления абитуриентами"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Панель поиска
        search_frame = QGroupBox("Поиск")
        search_layout = QHBoxLayout(search_frame)

        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.filter_applicants)
        search_layout.addWidget(self.search_input)

        search_layout.addStretch()
        layout.addWidget(search_frame)

        # Основной контент вкладки
        content_layout = QHBoxLayout()

        # Левая панель - форма ввода
        input_frame = QGroupBox("Данные абитуриента")
        input_frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        input_layout = QFormLayout(input_frame)

        # Поля ввода
        self.name_input = QLineEdit()
        self.birth_input = QLineEdit()
        self.birth_input.setPlaceholderText("ГГГГ-ММ-ДД")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("8-920-345-32-38")
        self.email_input = QLineEdit()

        self.exam1_input = QSpinBox()
        self.exam1_input.setRange(0, 100)
        self.exam2_input = QSpinBox()
        self.exam2_input.setRange(0, 100)
        self.exam3_input = QSpinBox()
        self.exam3_input.setRange(0, 100)

        self.contract_combo = QComboBox()
        self.contract_combo.addItems(["Нет", "Да"])

        # Добавление полей в форму
        input_layout.addRow("ФИО:", self.name_input)
        input_layout.addRow("Дата рождения:", self.birth_input)
        input_layout.addRow("Телефон:", self.phone_input)
        input_layout.addRow("Email:", self.email_input)
        input_layout.addRow("Экзамен 1:", self.exam1_input)
        input_layout.addRow("Экзамен 2:", self.exam2_input)
        input_layout.addRow("Экзамен 3:", self.exam3_input)
        input_layout.addRow("Договорная основа (платное обучение):", self.contract_combo)

        # Кнопки управления
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.clicked.connect(self.add_applicant)
        self.add_btn.setStyleSheet(self.get_button_style("#2ecc71"))

        self.update_btn = QPushButton("✏️ Обновить")
        self.update_btn.clicked.connect(self.update_applicant)
        self.update_btn.setStyleSheet(self.get_button_style("#3498db"))

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.clicked.connect(self.delete_applicant)
        self.delete_btn.setStyleSheet(self.get_button_style("#e74c3c"))

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.delete_btn)

        input_layout.addRow(button_layout)

        content_layout.addWidget(input_frame, 1)

        # Правая панель - таблица абитуриентов
        table_frame = QGroupBox("База абитуриентов")
        table_frame.setStyleSheet(input_frame.styleSheet())
        table_layout = QVBoxLayout(table_frame)

        # Таблица
        self.applicants_table = QTableWidget()
        self.applicants_table.setColumnCount(8)
        self.applicants_table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Баллы", "Общий", "Статус", "Договор", "Телефон", "Email"
        ])

        self.applicants_table.setSortingEnabled(False)
        self.applicants_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.applicants_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.applicants_table.doubleClicked.connect(self.load_applicant_data)

        # Настройка колонок
        header = self.applicants_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        table_layout.addWidget(self.applicants_table)
        content_layout.addWidget(table_frame, 2)

        layout.addLayout(content_layout)

        tab_widget.addTab(tab, "👥 Абитуриенты")

    def setup_selection_tab(self, tab_widget):
        """Настройка вкладки отбора"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Панель управления отбором
        control_frame = QGroupBox("Управление отбором")
        control_layout = QVBoxLayout(control_frame)

        # Проходной балл
        passing_layout = QHBoxLayout()
        passing_layout.addWidget(QLabel("Проходной балл:"))
        self.passing_score_input = QSpinBox()
        self.passing_score_input.setRange(0, 300)
        self.passing_score_input.setValue(self.passing_score)
        self.passing_score_input.valueChanged.connect(self.update_passing_score)
        passing_layout.addWidget(self.passing_score_input)
        passing_layout.addStretch()
        control_layout.addLayout(passing_layout)

        # Количество бюджетных мест
        budget_layout = QHBoxLayout()
        budget_layout.addWidget(QLabel("Бюджетные места:"))
        self.budget_seats_input = QSpinBox()
        self.budget_seats_input.setRange(1, 1000)
        self.budget_seats_input.setValue(self.budget_seats)
        self.budget_seats_input.valueChanged.connect(self.update_budget_seats)
        budget_layout.addWidget(self.budget_seats_input)
        budget_layout.addStretch()
        control_layout.addLayout(budget_layout)

        # Количество платных мест
        paid_layout = QHBoxLayout()
        paid_layout.addWidget(QLabel("Платные места:"))
        self.paid_seats_input = QSpinBox()
        self.paid_seats_input.setRange(1, 1000)
        self.paid_seats_input.setValue(self.paid_seats)
        self.paid_seats_input.valueChanged.connect(self.update_paid_seats)
        paid_layout.addWidget(self.paid_seats_input)
        paid_layout.addStretch()
        control_layout.addLayout(paid_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        self.select_btn = QPushButton("🎯 Выполнить отбор")
        self.select_btn.clicked.connect(self.perform_selection)
        self.select_btn.setStyleSheet(self.get_button_style("#e67e22", "16px"))

        self.interview_btn = QPushButton("📋 Список на собеседование")
        self.interview_btn.clicked.connect(self.show_interview_list)
        self.interview_btn.setStyleSheet(self.get_button_style("#f39c12"))

        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.interview_btn)

        control_layout.addLayout(button_layout)

        layout.addWidget(control_frame)

        # Вкладки результатов
        results_tabs = QTabWidget()

        # Зачисленные
        enrolled_tab = QWidget()
        enrolled_layout = QVBoxLayout(enrolled_tab)

        self.enrolled_text = QTextEdit()
        self.enrolled_text.setReadOnly(True)
        enrolled_layout.addWidget(self.enrolled_text)

        results_tabs.addTab(enrolled_tab, "🎓 Зачисленные")

        # На собеседование
        interview_tab = QWidget()
        interview_layout = QVBoxLayout(interview_tab)

        self.interview_text = QTextEdit()
        self.interview_text.setReadOnly(True)
        interview_layout.addWidget(self.interview_text)

        results_tabs.addTab(interview_tab, "💼 На собеседование")

        # Все кандидаты
        all_tab = QWidget()
        all_layout = QVBoxLayout(all_tab)

        self.all_text = QTextEdit()
        self.all_text.setReadOnly(True)
        all_layout.addWidget(self.all_text)

        results_tabs.addTab(all_tab, "📊 Все абитуриенты")

        layout.addWidget(results_tabs, 1)

        tab_widget.addTab(tab, "🎯 Отбор")

    def update_passing_score(self):
        """Обновление проходного балла"""
        self.passing_score = self.passing_score_input.value()
        self.save_settings()

    def update_budget_seats(self):
        """Обновление количества бюджетных мест"""
        self.budget_seats = self.budget_seats_input.value()
        self.save_settings()

    def update_paid_seats(self):
        """Обновление количества платных мест"""
        self.paid_seats = self.paid_seats_input.value()
        self.save_settings()

    def setup_reports_tab(self, tab_widget):
        """Настройка вкладки отчетов"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Кнопки
        button_layout = QHBoxLayout()

        self.backup_btn = QPushButton("💾 Резервная копия")
        self.backup_btn.clicked.connect(self.create_backup)
        self.backup_btn.setStyleSheet(self.get_button_style("#7f8c8d", "14px"))

        button_layout.addWidget(self.backup_btn)
        button_layout.addStretch()

        # Область отчета
        self.report_area = QTextEdit()
        self.report_area.setReadOnly(True)
        self.report_area.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New';
                font-size: 16px;
                background: 192140;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        layout.addLayout(button_layout)
        layout.addWidget(self.report_area, 1)

        tab_widget.addTab(tab, "📈 Отчеты")

    def setup_menu(self):
        """Настройка меню с учетом роли пользователя"""
        menubar = self.menuBar()

        # Меню Сервис
        service_menu = menubar.addMenu("⚙️ Сервис")

        # Настройки подключения - только для администратора
        conn_action = QAction("Настройки подключения", self)
        conn_action.triggered.connect(self.show_connection_dialog)
        conn_action.setEnabled(self.user_role == 'ADMIN')
        conn_action.setVisible(self.user_role == 'ADMIN')
        service_menu.addAction(conn_action)

        # Создать резервную копию - для администратора и оператора
        backup_action = QAction("Создать резервную копию", self)
        backup_action.triggered.connect(self.create_backup)
        backup_action.setEnabled(self.user_role in ['ADMIN', 'OPERATOR'])
        backup_action.setVisible(self.user_role in ['ADMIN', 'OPERATOR'])
        service_menu.addAction(backup_action)

        # Руководства
        manuals_menu = service_menu.addMenu("📖 Руководства")

        user_manual_action = QAction("📘 Руководство пользователя", self)
        user_manual_action.triggered.connect(lambda: self.show_manual('USER'))
        manuals_menu.addAction(user_manual_action)

        operator_manual_action = QAction("📗 Руководство оператора", self)
        operator_manual_action.triggered.connect(lambda: self.show_manual('OPERATOR'))
        operator_manual_action.setVisible(self.user_role in ['OPERATOR', 'ADMIN'])
        manuals_menu.addAction(operator_manual_action)

        admin_manual_action = QAction("📕 Руководство администратора", self)
        admin_manual_action.triggered.connect(lambda: self.show_manual('ADMIN'))
        admin_manual_action.setVisible(self.user_role == 'ADMIN')
        manuals_menu.addAction(admin_manual_action)

        service_menu.addSeparator()

        # Информация о текущей роли
        role_action = QAction(f"Текущая роль: {USER_ROLES[self.user_role]}", self)
        role_action.setEnabled(False)
        service_menu.addAction(role_action)

        service_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        service_menu.addAction(exit_action)

        # Меню справка
        help_menu = menubar.addMenu("❓ Справка")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_manual(self, role):
        """Показать руководство для роли"""
        role_dialog = RoleSelectionDialog(self)
        manual_content = role_dialog.get_manual_content(role)
        manual_title = f"Руководство {USER_ROLES[role]}"

        dialog = QDialog(self)
        dialog.setWindowTitle(manual_title)
        dialog.setGeometry(200, 200, 900, 700)

        layout = QVBoxLayout()

        # Текст руководства
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(manual_content)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: 192140;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        layout.addWidget(text_edit)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.setLayout(layout)
        dialog.exec()

    def show_about(self):
        """Показать информацию о программе"""
        role_dialog = RoleSelectionDialog(self)

        about_text = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h1 style="color: #2c3e50;">🎓 Система зачисления абитуриентов</h1>

            <h2 style="color: #34495e;">Информация о системе:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px;">
                <p><strong>Версия:</strong> 2.0 (с ролевой системой доступа)</p>
                <p><strong>Текущая роль:</strong> {USER_ROLES[self.user_role]}</p>
                <p><strong>База данных:</strong> {self.database_name}</p>
                <p><strong>Проходной балл:</strong> {self.passing_score}</p>
                <p><strong>Бюджетные места:</strong> {self.budget_seats}</p>
                <p><strong>Платные места:</strong> {self.paid_seats}</p>
                <p><strong>Разработчик:</strong> Система автоматизации зачисления</p>
            </div>

            <h2 style="color: #34495e;">Права доступа текущей роли:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px;">
        """

        if self.user_role == 'USER':
            about_text += """
                <h3 style="color: #3498db;">👤 Пользователь (только просмотр):</h3>
                <ul>
                    <li>✅ Просмотр списка абитуриентов</li>
                    <li>✅ Поиск по базе данных</li>
                    <li>✅ Просмотр отчетов и статистики</li>
                    <li>✅ Просмотр результатов отбора</li>
                    <li>❌ Редактирование данных</li>
                    <li>❌ Изменение настроек</li>
                </ul>
            """
        elif self.user_role == 'OPERATOR':
            about_text += """
                <h3 style="color: #2ecc71;">👷 Оператор (ввод и редактирование):</h3>
                <ul>
                    <li>✅ Все права пользователя</li>
                    <li>✅ Добавление новых абитуриентов</li>
                    <li>✅ Редактирование данных</li>
                    <li>✅ Удаление абитуриентов</li>
                    <li>✅ Проведение собеседований</li>
                    <li>✅ Создание резервных копий</li>
                    <li>❌ Изменение настроек системы</li>
                    <li>❌ Настройка подключения к БД</li>
                </ul>
            """
        else:  # ADMIN
            about_text += """
                <h3 style="color: #e74c3c;">🔧 Администратор (полный доступ):</h3>
                <ul>
                    <li>✅ Все права оператора</li>
                    <li>✅ Настройка параметров системы</li>
                    <li>✅ Настройка подключения к БД</li>
                    <li>✅ Создание/удаление баз данных</li>
                    <li>✅ Управление резервными копиями</li>
                    <li>✅ Полный доступ к отчетам</li>
                </ul>
            """

        about_text += """
            </div>

            <h2 style="color: #34495e;">Техническая информация:</h2>
            <div style="background: #192140; padding: 15px; border-radius: 5px; font-size: 12px;">
                <p><strong>СУБД:</strong> Microsoft SQL Server</p>
                <p><strong>ODBC Driver:</strong> 17 for SQL Server</p>
                <p><strong>Интерфейс:</strong> PyQt6</p>
                <p><strong>Язык программирования:</strong> Python</p>
                <p><strong>Дата сборки:</strong> """ + datetime.now().strftime("%d.%m.%Y") + """</p>
            </div>
        </div>
        """

        dialog = QDialog(self)
        dialog.setWindowTitle("О программе")
        dialog.setGeometry(300, 200, 600, 500)

        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(about_text)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: 192140;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        layout.addWidget(text_edit)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.setLayout(layout)
        dialog.exec()

    def get_button_style(self, color, font_size="14px"):
        """Получение стиля для кнопки"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: 192140;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: {font_size};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 30)};
            }}
        """

    def darken_color(self, color, percent=20):
        """Затемнение цвета"""
        import colorsys
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        hls = colorsys.rgb_to_hls(*[x / 255.0 for x in rgb])
        darkened = colorsys.hls_to_rgb(hls[0], max(0, hls[1] * (1 - percent / 100)), hls[2])
        return '#{:02x}{:02x}{:02x}'.format(*[int(x * 255) for x in darkened])

    def filter_applicants(self):
        """Фильтрация таблицы абитуриентов"""
        search_text = self.search_input.text().lower()

        for row in range(self.applicants_table.rowCount()):
            show_row = False

            if not search_text:
                show_row = True
            else:
                for col in range(self.applicants_table.columnCount()):
                    item = self.applicants_table.item(row, col)
                    if item and search_text in item.text().lower():
                        show_row = True
                        break

            self.applicants_table.setRowHidden(row, not show_row)

    def load_applicants(self):
        """Загрузка абитуриентов в таблицу"""
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, full_name, 
                       exam1_score, exam2_score, exam3_score,
                       total_score, admission_status,
                       CASE WHEN contract_willing = 1 THEN 'Да' ELSE 'Нет' END as contract,
                       contact_phone, email
                FROM applicants
                ORDER BY total_score DESC, id ASC
            """)

            data = cursor.fetchall()
            self.applicants_table.setRowCount(len(data))

            for row_idx, row_data in enumerate(data):
                # ID
                self.applicants_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))

                # ФИО
                self.applicants_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))

                # Баллы
                scores = f"{row_data[2]}/{row_data[3]}/{row_data[4]}"
                self.applicants_table.setItem(row_idx, 2, QTableWidgetItem(scores))

                # Общий балл
                self.applicants_table.setItem(row_idx, 3, QTableWidgetItem(str(row_data[5])))

                # Статус
                status_item = QTableWidgetItem(str(row_data[6]))

                # Выделение цветом по статусу
                if row_data[6] == 'Зачислен':
                    status_item.setBackground(QColor(46, 204, 113))
                    status_item.setForeground(QColor(255, 255, 255))
                elif row_data[6] == 'На собеседование':
                    status_item.setBackground(QColor(241, 196, 15))
                    status_item.setForeground(QColor(0, 0, 0))
                elif row_data[6] == 'Не прошел':
                    status_item.setBackground(QColor(231, 76, 60))
                    status_item.setForeground(QColor(255, 255, 255))

                self.applicants_table.setItem(row_idx, 4, status_item)

                # Договор
                self.applicants_table.setItem(row_idx, 5, QTableWidgetItem(str(row_data[7])))

                # Телефон
                phone = str(row_data[8]) if row_data[8] else ""
                formatted_phone = self.format_phone_number(phone)
                self.applicants_table.setItem(row_idx, 6, QTableWidgetItem(formatted_phone))

                # Email
                self.applicants_table.setItem(row_idx, 7, QTableWidgetItem(str(row_data[9])))

            self.update_reports()

        except Exception as e:
            print(f"Ошибка загрузки данных: {str(e)}")

    def load_applicant_data(self, index):
        """Загрузка данных выбранного абитуриента"""
        row = index.row()
        applicant_id = self.applicants_table.item(row, 0).text()

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT full_name, birth_date, contact_phone, email,
                       exam1_score, exam2_score, exam3_score,
                       contract_willing
                FROM applicants WHERE id = ?
            """, applicant_id)

            data = cursor.fetchone()
            if data:
                self.current_applicant_id = applicant_id

                self.name_input.setText(data[0] or "")
                self.birth_input.setText(str(data[1]) if data[1] else "")

                phone = data[2] or ""
                formatted_phone = self.format_phone_number(phone)
                self.phone_input.setText(formatted_phone)

                self.email_input.setText(data[3] or "")
                self.exam1_input.setValue(data[4] or 0)
                self.exam2_input.setValue(data[5] or 0)
                self.exam3_input.setValue(data[6] or 0)
                self.contract_combo.setCurrentText("Да" if data[7] == 1 else "Нет")

        except Exception as e:
            print(f"Ошибка загрузки данных абитуриента: {str(e)}")

    def validate_input(self):
        """Валидация введенных данных"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Внимание", "Поле 'ФИО' обязательно для заполнения")
            return False

        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Внимание", "Поле 'Email' обязательно для заполнения")
            return False

        try:
            for score in [self.exam1_input.value(), self.exam2_input.value(), self.exam3_input.value()]:
                if score < 0 or score > 100:
                    QMessageBox.warning(self, "Внимание", "Баллы должны быть в диапазоне 0-100")
                    return False
        except:
            return False

        return True

    def add_applicant(self):
        """Добавление нового абитуриента"""
        # Проверка прав доступа
        if self.user_role == 'USER':
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав на добавление абитуриентов.\n"
                                "Обратитесь к оператору или администратору.")
            return

        if not self.validate_input():
            return

        try:
            cursor = self.connection.cursor()

            query = """
            INSERT INTO applicants 
            (full_name, birth_date, contact_phone, email, 
             exam1_score, exam2_score, exam3_score, total_score, contract_willing)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            total_score = (self.exam1_input.value() +
                           self.exam2_input.value() +
                           self.exam3_input.value())

            contract_willing = 1 if self.contract_combo.currentText() == "Да" else 0

            # Форматируем телефон перед сохранением
            phone = self.format_phone_number(self.phone_input.text().strip())

            cursor.execute(query, (
                self.name_input.text().strip(),
                self.birth_input.text().strip() if self.birth_input.text().strip() else None,
                phone,
                self.email_input.text().strip(),
                self.exam1_input.value(),
                self.exam2_input.value(),
                self.exam3_input.value(),
                total_score,
                contract_willing
            ))

            self.connection.commit()
            self.load_applicants()
            self.clear_form()

            self.status_bar.showMessage("Абитуриент успешно добавлен", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")

    def update_applicant(self):
        """Обновление данных абитуриента"""
        # Проверка прав доступа
        if self.user_role == 'USER':
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав на редактирование данных абитуриентов.\n"
                                "Обратитесь к оператору или администратору.")
            return

        if not self.current_applicant_id:
            QMessageBox.warning(self, "Внимание", "Выберите абитуриента для обновления")
            return

        if not self.validate_input():
            return

        try:
            cursor = self.connection.cursor()

            query = """
            UPDATE applicants 
            SET full_name = ?, birth_date = ?, contact_phone = ?, email = ?,
                exam1_score = ?, exam2_score = ?, exam3_score = ?,
                total_score = ?, contract_willing = ?
            WHERE id = ?
            """

            total_score = (self.exam1_input.value() +
                           self.exam2_input.value() +
                           self.exam3_input.value())

            contract_willing = 1 if self.contract_combo.currentText() == "Да" else 0

            phone = self.format_phone_number(self.phone_input.text().strip())

            cursor.execute(query, (
                self.name_input.text().strip(),
                self.birth_input.text().strip() if self.birth_input.text().strip() else None,
                phone,
                self.email_input.text().strip(),
                self.exam1_input.value(),
                self.exam2_input.value(),
                self.exam3_input.value(),
                total_score,
                contract_willing,
                self.current_applicant_id
            ))

            self.connection.commit()
            self.load_applicants()

            self.status_bar.showMessage("Данные успешно обновлены", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")

    def delete_applicant(self):
        """Удаление абитуриента"""
        # Проверка прав доступа
        if self.user_role == 'USER':
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав на удаление абитуриентов.\n"
                                "Обратитесь к оператору или администратору.")
            return

        if not self.current_applicant_id:
            QMessageBox.warning(self, "Внимание", "Выберите абитуриента для удаления")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите удалить абитуриента?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        try:
            cursor = self.connection.cursor()

            cursor.execute("DELETE FROM selected_applicants WHERE applicant_id = ?",
                           self.current_applicant_id)
            cursor.execute("DELETE FROM applicants WHERE id = ?",
                           self.current_applicant_id)

            self.connection.commit()
            self.load_applicants()
            self.clear_form()

            self.status_bar.showMessage("Абитуриент успешно удален", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")

    def perform_selection(self):
        """Выполнение отбора абитуриентов с учетом бюджетных и платных мест"""
        # Проверка прав доступа
        if self.user_role == 'USER':
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав на выполнение отбора абитуриентов.\n"
                                "Обратитесь к оператору или администратору.")
            return

        try:
            budget_seats = self.budget_seats
            paid_seats = self.paid_seats
            passing_score = self.passing_score

            cursor = self.connection.cursor()

            # Очистка предыдущих результатов отбора
            cursor.execute("DELETE FROM selected_applicants")

            # Сброс статусов всех абитуриентов
            cursor.execute("UPDATE applicants SET admission_status = 'Не рассмотрено'")

            # Получаем всех абитуриентов без договора, отсортированных по баллам
            cursor.execute("""
                SELECT id, full_name, total_score, contract_willing
                FROM applicants
                WHERE total_score >= ? AND contract_willing = 0
                ORDER BY total_score DESC
            """, passing_score)

            applicants_without_contract = cursor.fetchall()

            # Получаем всех абитуриентов с договором, отсортированных по баллам
            cursor.execute("""
                SELECT id, full_name, total_score, contract_willing
                FROM applicants
                WHERE total_score > ? AND contract_willing = 1
                ORDER BY total_score DESC
            """, passing_score)

            applicants_with_contract_above = cursor.fetchall()

            # Получаем абитуриентов с договором, у которых балл равен проходному
            cursor.execute("""
                SELECT id, full_name, total_score, contract_willing
                FROM applicants
                WHERE total_score = ? AND contract_willing = 1
                ORDER BY id ASC
            """, passing_score)

            applicants_with_contract_equal = cursor.fetchall()

            # Зачисляем на бюджетные места
            enrolled_budget = []

            # Сначала зачисляем без договора с баллом > проходного
            for i, applicant in enumerate(applicants_without_contract):
                if applicant[2] > passing_score and len(enrolled_budget) < budget_seats:
                    cursor.execute("""
                        UPDATE applicants 
                        SET admission_status = 'Зачислен'
                        WHERE id = ?
                    """, applicant[0])

                    cursor.execute("""
                        INSERT INTO selected_applicants (applicant_id, selection_type, selection_reason)
                        VALUES (?, 'Зачислен на бюджет', 'Балл выше проходного без договора')
                    """, applicant[0])

                    enrolled_budget.append(applicant[0])

            # Если остались бюджетные места, зачисляем абитуриентов с договором с баллом СТРОГО больше проходного
            remaining_budget = budget_seats - len(enrolled_budget)
            if remaining_budget > 0:
                for i, applicant in enumerate(applicants_with_contract_above):
                    if i < remaining_budget:
                        cursor.execute("""
                            UPDATE applicants 
                            SET admission_status = 'Зачислен',
                                contract_willing = 0
                            WHERE id = ?
                        """, applicant[0])

                        cursor.execute("""
                            INSERT INTO selected_applicants (applicant_id, selection_type, selection_reason)
                            VALUES (?, 'Зачислен на бюджет', 'Балл выше проходного с договором')
                        """, applicant[0])

                        enrolled_budget.append(applicant[0])

            # Обрабатываем абитуриентов без договора, у которых балл РАВЕН проходному
            for applicant in applicants_without_contract:
                if applicant[2] == passing_score:
                    cursor.execute("""
                        UPDATE applicants 
                        SET admission_status = 'На собеседование'
                        WHERE id = ?
                    """, applicant[0])

            # Зачисляем на платные места
            enrolled_paid = []

            # Сначала те, у кого балл равен проходному и есть договор
            for applicant in applicants_with_contract_equal:
                if applicant[0] not in enrolled_budget and len(enrolled_paid) < paid_seats:
                    cursor.execute("""
                        UPDATE applicants 
                        SET admission_status = 'Зачислен',
                            contract_willing = 1
                        WHERE id = ?
                    """, applicant[0])

                    cursor.execute("""
                        INSERT INTO selected_applicants (applicant_id, selection_type, selection_reason)
                        VALUES (?, 'Зачислен на платное', 'Балл равен проходному с договором')
                    """, applicant[0])

                    enrolled_paid.append(applicant[0])

            # Те, кто не набрал проходной балл, но готов на договор
            cursor.execute("""
                SELECT id, full_name, total_score
                FROM applicants
                WHERE total_score < ? AND contract_willing = 1
                ORDER BY total_score DESC
            """, passing_score)

            low_score_applicants = cursor.fetchall()

            for applicant in low_score_applicants:
                if applicant[0] not in enrolled_budget and applicant[0] not in enrolled_paid and len(
                        enrolled_paid) < paid_seats:
                    cursor.execute("""
                        UPDATE applicants 
                        SET admission_status = 'Зачислен',
                            contract_willing = 1
                        WHERE id = ?
                    """, applicant[0])

                    cursor.execute("""
                        INSERT INTO selected_applicants (applicant_id, selection_type, selection_reason)
                        VALUES (?, 'Зачислен на платное', 'Ниже проходного балла, но готов на договор')
                    """, applicant[0])

                    enrolled_paid.append(applicant[0])

            # Остальные - не зачислены
            cursor.execute("""
                UPDATE applicants 
                SET admission_status = 'Не прошел'
                WHERE admission_status = 'Не рассмотрено'
            """)

            self.connection.commit()
            self.load_applicants()
            self.update_reports()

            QMessageBox.information(self, "Успех",
                                    f"Отбор завершен.\n"
                                    f"Проходной балл: {passing_score}\n"
                                    f"Бюджетные места: {budget_seats} (зачислено: {len(enrolled_budget)})\n"
                                    f"Платные места: {paid_seats} (зачислено: {len(enrolled_paid)})")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отборе: {str(e)}")

    def show_interview_list(self):
        """Показать список кандидатов на собеседование с возможностью зачисления"""
        # Проверка прав доступа
        if self.user_role == 'USER':
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав на проведение собеседований.\n"
                                "Обратитесь к оператору или администратору.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT a.full_name, a.total_score, a.birth_date, 
                       a.contact_phone, a.email, a.exam1_score,
                       a.exam2_score, a.exam3_score, a.contract_willing, a.id
                FROM applicants a
                WHERE a.admission_status = 'На собеседование'
                ORDER BY a.total_score DESC, a.full_name
            """)

            candidates = cursor.fetchall()

            if not candidates:
                QMessageBox.information(self, "Информация", "Кандидаты на собеседование не найдены")
                return

            dialog = InterviewDialog(self, candidates)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                results = dialog.get_results()

                cursor.execute(
                    "SELECT COUNT(*) FROM applicants WHERE admission_status = 'Зачислен' AND contract_willing = 0")
                budget_enrolled = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM applicants WHERE admission_status = 'Зачислен' AND contract_willing = 1")
                paid_enrolled = cursor.fetchone()[0]

                remaining_budget = self.budget_seats - budget_enrolled
                remaining_paid = self.paid_seats - paid_enrolled

                accepted_count = 0
                budget_count = 0
                paid_count = 0

                for result in results:
                    if result['accepted']:
                        accepted_count += 1

                        if remaining_budget > 0:
                            cursor.execute("""
                                UPDATE applicants 
                                SET admission_status = 'Зачислен',
                                    contract_willing = 0
                                WHERE id = ?
                            """, result['id'])

                            cursor.execute("""
                                INSERT INTO selected_applicants (applicant_id, selection_type, selection_reason)
                                VALUES (?, 'Зачислен на бюджет через собеседование', ?)
                            """, result['id'], result['comment'] or 'Положительное решение на собеседовании (бюджет)')

                            remaining_budget -= 1
                            budget_count += 1

                        elif remaining_paid > 0:
                            cursor.execute("""
                                UPDATE applicants 
                                SET admission_status = 'Зачислен',
                                    contract_willing = 1
                                WHERE id = ?
                            """, result['id'])

                            cursor.execute("""
                                INSERT INTO selected_applicants (applicant_id, selection_type, selection_reason)
                                VALUES (?, 'Зачислен на платное через собеседование', ?)
                            """, result['id'], result['comment'] or 'Положительное решение на собеседовании (платное)')

                            remaining_paid -= 1
                            paid_count += 1

                        else:
                            QMessageBox.warning(self, "Внимание",
                                                f"Для {result['name']} нет свободных мест! (ни бюджетных, ни платных)")
                    else:
                        cursor.execute("""
                            UPDATE applicants 
                            SET admission_status = 'Не прошел'
                            WHERE id = ?
                        """, result['id'])

                        cursor.execute("""
                            INSERT INTO selected_applicants (applicant_id, selection_type, selection_reason)
                            VALUES (?, 'Отклонен на собеседовании', ?)
                        """, result['id'], result['comment'] or 'Отрицательное решение на собеседовании')

                self.connection.commit()
                self.load_applicants()
                self.update_reports()

                message = f"Решения по собеседованию применены!\n"
                message += f"Зачислено на бюджет: {budget_count}\n"
                message += f"Зачислено на платное: {paid_count}\n"
                message += f"Отклонено: {len(results) - accepted_count}"

                QMessageBox.information(self, "Успех", message)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")

    def update_reports(self):
        """Обновление отчетов"""
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()

            # Зачисленные
            cursor.execute("""
                SELECT a.full_name, a.total_score, s.selection_date, s.selection_reason,
                       CASE WHEN a.contract_willing = 1 THEN 'Да' ELSE 'Нет' END as contract
                FROM applicants a
                LEFT JOIN selected_applicants s ON a.id = s.applicant_id
                WHERE a.admission_status = 'Зачислен'
                ORDER BY a.total_score DESC
            """)

            enrolled = cursor.fetchall()

            # На собеседование
            cursor.execute("""
                SELECT full_name, total_score, contact_phone, email,
                       exam1_score, exam2_score, exam3_score
                FROM applicants
                WHERE admission_status = 'На собеседование'
                ORDER BY total_score DESC
            """)

            interview = cursor.fetchall()

            # Все абитуриенты
            cursor.execute("""
                SELECT full_name, total_score, admission_status, 
                       CASE WHEN contract_willing = 1 THEN 'Да' ELSE 'Нет' END,
                       exam1_score, exam2_score, exam3_score
                FROM applicants
                ORDER BY total_score DESC
            """)

            all_applicants = cursor.fetchall()

            # Формирование отчетов
            enrolled_text = f"🎓 ЗАЧИСЛЕННЫЕ АБИТУРИЕНТЫ\n"
            enrolled_text += f"Проходной балл: {self.passing_score}\n"
            enrolled_text += f"Бюджетные места: {self.budget_seats}, Платные места: {self.paid_seats}\n"
            enrolled_text += "=" * 80 + "\n\n"

            for i, (name, score, date, reason, contract) in enumerate(enrolled, 1):
                enrolled_text += f"{i}. {name} - {score} баллов\n"
                enrolled_text += f"   Причина: {reason or 'Нет данных'}\n"
                enrolled_text += f"   Договор: {contract}\n"
                if date:
                    enrolled_text += f"   Дата: {date.strftime('%d.%m.%Y')}\n"
                enrolled_text += "\n"

            # Статистика
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN admission_status = 'Зачислен' AND contract_willing = 0 THEN 1 ELSE 0 END) as budget_enrolled,
                    SUM(CASE WHEN admission_status = 'Зачислен' AND contract_willing = 1 THEN 1 ELSE 0 END) as paid_enrolled,
                    SUM(CASE WHEN admission_status = 'На собеседование' THEN 1 ELSE 0 END) as interview_count,
                    SUM(CASE WHEN admission_status = 'Не прошел' THEN 1 ELSE 0 END) as failed_count
                FROM applicants
            """)

            stats = cursor.fetchone()

            enrolled_text += f"\n📊 СТАТИСТИКА ЗАЧИСЛЕНИЯ:\n"
            enrolled_text += f"   • Зачислено на бюджет: {stats[0] or 0}\n"
            enrolled_text += f"   • Зачислено на платное: {stats[1] or 0}\n"
            enrolled_text += f"   • На собеседовании: {stats[2] or 0}\n"
            enrolled_text += f"   • Не прошли: {stats[3] or 0}\n"

            # Отчет на собеседование
            interview_text = "💼 КАНДИДАТЫ НА СОБЕСЕДОВАНИЕ\n"
            interview_text += "=" * 60 + "\n\n"

            for i, (name, score, phone, email, exam1, exam2, exam3) in enumerate(interview, 1):
                interview_text += f"{i}. {name} - {score} баллов\n"
                interview_text += f"   Телефон: {phone}\n"
                interview_text += f"   Email: {email}\n"
                interview_text += f"   Баллы: {exam1}/{exam2}/{exam3}\n\n"

            if not interview:
                interview_text += "Кандидаты на собеседование отсутствуют\n"

            # Все абитуриенты
            all_text = "📊 ВСЕ АБИТУРИЕНТЫ:\n"
            all_text += "=" * 60 + "\n\n"

            for i, (name, score, status, contract, exam1, exam2, exam3) in enumerate(all_applicants, 1):
                status_icon = "✅" if status == 'Зачислен' else "🤝" if status == 'На собеседование' else "❌" if status == 'Не прошел' else "⏳"
                contract_icon = "💼" if contract == 'Да' else ""

                all_text += f"{i}. {name} - {score} баллов {status_icon} {contract_icon}\n"
                all_text += f"   Статус: {status}\n"
                all_text += f"   Экзамены: {exam1}/{exam2}/{exam3}\n\n"

            self.enrolled_text.setText(enrolled_text)
            self.interview_text.setText(interview_text)
            self.all_text.setText(all_text)

            # Общий отчет
            total_report = f"""
📈 СТАТИСТИКА СИСТЕМЫ
{'=' * 50}
База данных: {self.database_name}
Проходной балл: {self.passing_score}
Бюджетные места: {self.budget_seats}
Платные места: {self.paid_seats}
Всего абитуриентов: {len(all_applicants)}
Зачислено на бюджет: {stats[0] or 0}
Зачислено на платное: {stats[1] or 0}
На собеседовании: {stats[2] or 0}
Не прошли: {stats[3] or 0}
Готовы к договору: {len([a for a in all_applicants if a[3] == 'Да'])}
Текущая роль: {USER_ROLES[self.user_role]}

🏆 ТОП ПО БАЛЛАМ:
"""
            for i, (name, score, _, _, exam1, exam2, exam3) in enumerate(all_applicants[:5], 1):
                total_report += f"{i}. {name} - {score} баллов ({exam1}/{exam2}/{exam3})\n"

            total_report += f"""
📋 УСЛОВИЯ ЗАЧИСЛЕНИЯ:
1. Набрал > {self.passing_score} баллов и НЕ готов на договор → Зачислен на бюджет (приоритет)
2. Набрал > {self.passing_score} баллов и готов на договор → Зачислен на бюджет (второстепенный приоритет)
3. Набрал < {self.passing_score} баллов, но готов на договор → Зачислен на платное (если есть места)
4. Набрал = {self.passing_score} баллов и НЕ готов на договор → В список на собеседование
5. Набрал = {self.passing_score} баллов и готов на договор → Зачислен на платное
6. Набрал < {self.passing_score} баллов и НЕ готов на договор → Не зачислен
"""

            self.report_area.setText(total_report)

        except Exception as e:
            print(f"Ошибка обновления отчетов: {str(e)}")

    def create_backup(self):
        """Создание резервной копии базы данных"""
        # Проверка прав доступа
        if self.user_role == 'USER':
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав на создание резервных копий.\n"
                                "Обратитесь к оператору или администратору.")
            return

        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT * FROM applicants")
            applicants = cursor.fetchall()

            cursor.execute("SELECT * FROM selected_applicants")
            selected = cursor.fetchall()

            cursor.execute("SELECT * FROM settings")
            settings = cursor.fetchall()

            backup_file = f"backup_admission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("-- Резервная копия системы зачисления абитуриентов\n")
                f.write(f"-- Дата создания: {datetime.now()}\n")
                f.write(f"-- База данных: {self.database_name}\n")
                f.write(f"-- Проходной балл: {self.passing_score}\n")
                f.write(f"-- Бюджетные места: {self.budget_seats}\n")
                f.write(f"-- Платные места: {self.paid_seats}\n")
                f.write(f"-- Роль пользователя: {USER_ROLES[self.user_role]}\n\n")

                f.write("-- Данные абитуриентов\n")
                for row in applicants:
                    f.write(str(row) + "\n")

                f.write("\n-- Данные отбора\n")
                for row in selected:
                    f.write(str(row) + "\n")

                f.write("\n-- Настройки\n")
                for row in settings:
                    f.write(str(row) + "\n")

            self.status_bar.showMessage(f"Резервная копия создана: {backup_file}", 5000)
            QMessageBox.information(self, "Успех", f"Резервная копия создана:\n{backup_file}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании резервной копии: {str(e)}")

    def show_connection_dialog(self):
        """Показать диалог настройки подключения"""
        # Проверка прав доступа
        if self.user_role != 'ADMIN':
            QMessageBox.warning(self, "Доступ запрещен",
                                "У вас нет прав на настройку подключения к базе данных.\n"
                                "Обратитесь к администратору системы.")
            return

        dialog = DatabaseConnectionDialog(self, self.user_role)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_conn_str = dialog.get_connection_string()
            new_db_name = dialog.get_database_name()
            try:
                self.connection = pyodbc.connect(new_conn_str)
                self.connection_string = new_conn_str
                self.database_name = new_db_name

                # Обновляем интерфейс
                self.update_window_title()
                self.load_settings()
                self.load_applicants()

                # Обновляем заголовок в интерфейсе
                for i in range(self.centralWidget().layout().count()):
                    widget = self.centralWidget().layout().itemAt(i).widget()
                    if isinstance(widget, QLabel) and "Система зачисления" in widget.text():
                        role_name = USER_ROLES.get(self.user_role, 'Неизвестно')
                        role_color = "#3498db" if self.user_role == 'USER' else "#2ecc71" if self.user_role == 'OPERATOR' else "#e74c3c"
                        widget.setText(f"🎓 Система зачисления абитуриентов группы {self.database_name}")
                        widget.setStyleSheet(f"""
                            font-size: 24px;
                            font-weight: bold;
                            color: #2c3e50;
                            padding: 20px;
                            background: linear-gradient(90deg, {role_color}, #2c3e50);
                            color: 192140;
                            border-radius: 10px;
                            margin-bottom: 20px;
                        """)
                        break

                self.status_bar.showMessage(f"Роль: {USER_ROLES[self.user_role]} | База данных: {self.database_name}")
                QMessageBox.information(self, "Успех", f"Подключение к базе данных '{self.database_name}' успешно!")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться: {str(e)}")

    def clear_form(self):
        """Очистка формы ввода"""
        self.current_applicant_id = None
        self.name_input.clear()
        self.birth_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.exam1_input.setValue(0)
        self.exam2_input.setValue(0)
        self.exam3_input.setValue(0)
        self.contract_combo.setCurrentText("Нет")

    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        if self.connection:
            self.connection.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Сначала авторизация пользователя
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        selected_role = login_dialog.role

        if selected_role:
            # Показ диалога подключения к базе данных
            conn_dialog = DatabaseConnectionDialog(user_role=selected_role)
            if conn_dialog.exec() == QDialog.DialogCode.Accepted:
                connection_string = conn_dialog.get_connection_string()
                database_name = conn_dialog.get_database_name()

                # Запуск основного приложения с выбранной ролью
                window = ApplicantSystem(connection_string, database_name, selected_role)
                window.show()

                sys.exit(app.exec())
            else:
                sys.exit(0)
        else:
            sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()