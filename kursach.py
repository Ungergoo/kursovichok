import tkinter as tk
from tkinter import messagebox
import hashlib
import json
import os
import random

# Файл базы данных
DB_FILE = "users.json"


# ===================== Функции работы с пользователями =====================

def hash_password(password):
    """Шифруем пароль"""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    """Загружаем пользователей из файла"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    """Сохраняем пользователей в файл"""
    with open(DB_FILE, "w") as f:
        json.dump(users, f)


def register():
    """Регистрация пользователя"""
    username = entry_username.get()
    password = entry_password.get()
    users = load_users()

    if username in users:
        messagebox.showerror("Ошибка", "Пользователь уже существует!")
        return

    users[username] = hash_password(password)
    save_users(users)
    messagebox.showinfo("Успех", "Регистрация успешна! Теперь войдите.")


def login():
    """Авторизация пользователя"""
    username = entry_username.get()
    password = entry_password.get()
    users = load_users()

    if username in users and users[username] == hash_password(password):
        messagebox.showinfo("Успех", "Вход выполнен!")
        root.destroy()  # Закрываем окно авторизации
        start_game()  # Запускаем игру
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль!")


# ===================== Игровая логика =====================

class ChessGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Эндшпиль: Король и пешки")

        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()
        self.board = [[None for _ in range(8)] for _ in range(8)]  # Игровое поле

        self.selected_piece = None  # Храним выбранную фигуру (row, col)
        self.init_board()

        self.canvas.bind("<Button-1>", self.on_click)  # Обрабатываем клики мыши

    def init_board(self):
        """Создаем шахматную доску и случайную расстановку фигур"""
        colors = ["white", "gray"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(col * 50, row * 50, (col + 1) * 50, (row + 1) * 50, fill=color)

        # Генерируем случайные позиции для фигур
        positions = set()

        def get_random_empty_position():
            """Выбирает случайную пустую клетку на доске"""
            while True:
                pos = (random.randint(0, 7), random.randint(0, 7))
                if pos not in positions:
                    positions.add(pos)
                    return pos

        # Белые фигуры
        self.wk_pos = get_random_empty_position()  # Белый король
        self.wp1_pos = get_random_empty_position()  # Первая белая пешка
        self.wp2_pos = get_random_empty_position()  # Вторая белая пешка

        # Черные фигуры
        self.bk_pos = get_random_empty_position()  # Черный король
        self.bp_pos = get_random_empty_position()  # Черная пешка

        # Устанавливаем фигуры на доску
        self.board[self.wk_pos[0]][self.wk_pos[1]] = "K"
        self.board[self.wp1_pos[0]][self.wp1_pos[1]] = "P"
        self.board[self.wp2_pos[0]][self.wp2_pos[1]] = "P"
        self.board[self.bk_pos[0]][self.bk_pos[1]] = "k"
        self.board[self.bp_pos[0]][self.bp_pos[1]] = "p"

        self.draw_pieces()

    def draw_pieces(self):
        """Рисуем фигуры на доске"""
        self.canvas.delete("piece")  # Удаляем старые фигуры
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    x, y = col * 50 + 25, row * 50 + 25
                    color = "black" if piece in ("p", "k") else "blue"
                    self.canvas.create_text(x, y, text=piece, font=("Arial", 24), fill=color, tags="piece")

    def on_click(self, event):
        """Обрабатываем клик по доске"""
        col = event.x // 50
        row = event.y // 50
        clicked_piece = self.board[row][col]

        if self.selected_piece:
            from_row, from_col = self.selected_piece

            # Если выбрали другую свою фигуру — просто переключаем выбор
            if clicked_piece and clicked_piece.isupper():
                self.selected_piece = (row, col)
                return  

            # Если ходить нельзя, НЕ пропускаем ход — просто сбрасываем выбор
            if not self.is_valid_move(self.board[from_row][from_col], from_row, from_col, row, col):
                self.selected_piece = None
                return

            # Если ход допустим — делаем его
            self.move_piece(self.selected_piece, (row, col))
            self.selected_piece = None
            self.ai_move()  # После хода игрока ходит ИИ

        elif clicked_piece and clicked_piece.isupper():  
            # Если кликнули на свою фигуру — выбираем её
            self.selected_piece = (row, col)

    def move_piece(self, from_pos, to_pos):
        """Перемещаем фигуру, если ход допустим"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]

        if self.is_valid_move(piece, from_row, from_col, to_row, to_col):
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            self.draw_pieces()

    def is_valid_move(self, piece, from_row, from_col, to_row, to_col):
        """Проверяет, допустим ли ход"""
        target_piece = self.board[to_row][to_col]

        # Нельзя ходить на свою фигуру
        if target_piece and (piece.isupper() == target_piece.isupper()):
            return False  

        # Король – ходит на 1 клетку во всех направлениях
        if piece in ("K", "k"):
            return abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1

        # Белая пешка – ходит вперед, бьет по диагонали
        if piece == "P":
            if from_col == to_col and from_row - to_row == 1 and target_piece is None:
                return True  # Обычный ход вперед
            if abs(from_col - to_col) == 1 and from_row - to_row == 1 and target_piece in ("p", "k"):
                return True  # Бьёт фигуру противника по диагонали

        # Черная пешка – ходит вперед, бьет по диагонали
        if piece == "p":
            if from_col == to_col and to_row - from_row == 1 and target_piece is None:
                return True  # Обычный ход вперед
            if abs(from_col - to_col) == 1 and to_row - from_row == 1 and target_piece in ("P", "K"):
                return True  # Бьёт фигуру противника по диагонали

        return False
    def show_victory_message(self, message):
        """Показывает всплывающее окно с сообщением о победе и перезапускает игру"""
        messagebox.showinfo("Победа!", message)
        self.master.quit()
    def check_victory(self):
        """Проверка победы: если нет короля одного из игроков — игра закончена"""
        black_king_found = False
        white_king_found = False

        # Проходим по всему полю и ищем королей
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == "k":  # Черный король
                    black_king_found = True
                if self.board[row][col] == "K":  # Белый король
                    white_king_found = True

        # Проверка победы
        if not black_king_found:
            self.show_victory_message("Белый игрок победил!")
            return "White"
        elif not white_king_found:
            self.show_victory_message("Черный игрок победил!")
            return "Black"
        
        return None  # Игра продолжается
    
    def ai_move(self):
        """ИИ делает ход, следуя приоритетам атаки и продвижения"""
        # Дальше идет логика хода ИИ, как было описано выше
        # Сначала ищем возможные ходы для атаки королем
        possible_moves = []

        for row in range(8):
            for col in range(8):
                if self.board[row][col] == "k":  # Черный король
                    # Пробуем все 8 возможных направлений для короля
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if 0 <= row + dr < 8 and 0 <= col + dc < 8:
                                target = self.board[row + dr][col + dc]
                                # Если на клетке фигура противника (пешка или король) — атакуем
                                if target in ("P", "K"):
                                    self.move_piece((row, col), (row + dr, col + dc))
                                    # Проверим победу после хода
                                    winner = self.check_victory()
                                    if winner:
                                        return  # Игра завершена, ИИ не делает ход дальше
                                    return  # После атаки сразу выходим из функции

        # Теперь ищем возможные ходы для атаки пешками
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == "p":  # Черная пешка
                    # Проверяем, может ли пешка бить белую фигуру
                    if row < 7:
                        # Бьет по диагонали влево
                        if col > 0 and self.board[row + 1][col - 1] in ("P", "K"):
                            self.move_piece((row, col), (row + 1, col - 1))
                            # Проверим победу после хода
                            winner = self.check_victory()
                            if winner:
                                return  # Игра завершена, ИИ не делает ход дальше
                            return  # После атаки сразу выходим из функции
                        # Бьет по диагонали вправо
                        if col < 7 and self.board[row + 1][col + 1] in ("P", "K"):
                            self.move_piece((row, col), (row + 1, col + 1))
                            # Проверим победу после хода
                            winner = self.check_victory()
                            if winner:
                                return  # Игра завершена, ИИ не делает ход дальше
                            return  # После атаки сразу выходим из функции

        # После атакуемых ходов ищем ходы для продвижения пешек
        possible_moves = []
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == "p":
                    # Ход вперед (без атаки)
                    if row < 7 and self.board[row + 1][col] is None:
                        possible_moves.append(((row, col), (row + 1, col)))
                    # Бьет по диагонали
                    if col > 0 and row < 7 and self.board[row + 1][col - 1] in ("P", "K"):
                        possible_moves.append(((row, col), (row + 1, col - 1)))
                    if col < 7 and row < 7 and self.board[row + 1][col + 1] in ("P", "K"):
                        possible_moves.append(((row, col), (row + 1, col + 1)))

        # Если есть возможные ходы для пешек, делаем случайный
        if possible_moves:
            move = random.choice(possible_moves)
            self.move_piece(move[0], move[1])
            # Проверим победу после хода
            winner = self.check_victory()
            if winner:
                return  # Игра завершена, ИИ не делает ход дальше

        # Когда все пешки не могут двигаться, ищем ход для короля
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == "k":  # Черный король
                    possible_moves = []
                    # Пробуем все 8 возможных направлений для короля
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if 0 <= row + dr < 8 and 0 <= col + dc < 8:
                                target = self.board[row + dr][col + dc]
                                # Если клетка пуста — просто ходим
                                if target is None:
                                    possible_moves.append(((row, col), (row + dr, col + dc)))

                    # Если есть возможные ходы для короля, делаем случайный ход
                    if possible_moves:
                        move = random.choice(possible_moves)
                        self.move_piece(move[0], move[1])
                        # Проверим победу после хода
                        winner = self.check_victory()
                        if winner:
                            return  # Игра завершена, ИИ не делает ход дальше


def start_game():
    """Запуск игры"""
    game_window = tk.Tk()
    ChessGame(game_window)
    game_window.mainloop()


# ===================== Интерфейс авторизации =====================

root = tk.Tk()
root.title("Авторизация")

tk.Label(root, text="Логин:").grid(row=0, column=0)
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1)

tk.Label(root, text="Пароль:").grid(row=1, column=0)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1)

btn_register = tk.Button(root, text="Регистрация", command=register)
btn_register.grid(row=2, column=0)

btn_login = tk.Button(root, text="Вход", command=login)
btn_login.grid(row=2, column=1)

root.mainloop()
