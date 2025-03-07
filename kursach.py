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
        self.game_over = False
        self.master = master
        self.master.title("Эндшпиль: Король и пешки")

        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack(side=tk.RIGHT)  # Canvas справа от кнопки

        self.reset_button = tk.Button(master, text="Сбросить игру", command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=20)  # Кнопка слева от доски

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

        def get_random_empty_position(for_pawn=False, is_white=False):
            """Выбирает случайную пустую клетку на доске"""
            while True:
                row = random.randint(0, 7)
                col = random.randint(0, 7)
                if for_pawn:
                    if is_white and row == 0:  # Запрещаем спавн белых пешек в верхней строке
                        continue
                    if not is_white and row == 7:  # Запрещаем спавн черных пешек в нижней строке
                        continue
                if (row, col) not in positions:
                    positions.add((row, col))
                    return row, col

        # Белые фигуры
        self.wk_pos = get_random_empty_position()  # Белый король
        self.wp1_pos = get_random_empty_position(for_pawn=True, is_white=True)  # Первая белая пешка
        self.wp2_pos = get_random_empty_position(for_pawn=True, is_white=True)  # Вторая белая пешка

        # Черные фигуры
        self.bk_pos = get_random_empty_position()  # Черный король
        self.bp_pos = get_random_empty_position(for_pawn=True, is_white=False)  # Черная пешка

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
                    # Определяем цвет фигуры
                    if piece in ("P", "K", "Q"):  # Белые фигуры
                        color = "blue"
                    elif piece in ("p", "k", "q"):  # Черные фигуры
                        color = "black"
                    
                    x, y = col * 50 + 25, row * 50 + 25
                    self.canvas.create_text(x, y, text=piece, font=("Arial", 24), fill=color, tags="piece")

    def is_king_captured(self, player):
        """Проверяет, захвачен ли король указанного игрока"""
        if player == 1:  # Черный король
            for row in range(8):
                for col in range(8):
                    if self.board[row][col] == 'K':  # Если на доске есть черный король
                        print("Король черных на доске")  # Отладочная информация
                        return False  # Король еще на доске, значит не захвачен
        elif player == 2:  # Белый король
            for row in range(8):
                for col in range(8):
                    if self.board[row][col] == 'k':  # Если на доске есть белый король
                        print("Король белых на доске")  # Отладочная информация
                        return False  # Король еще на доске, значит не захвачен
        print("Король захвачен!")  # Отладочная информация
        return True  # Если короля нет на доске, значит он захвачен


    def on_click(self, event):
        """Обрабатываем клик по доске"""
        if self.game_over:
            return  # Если игра завершена, не обрабатываем клик

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

            # Проверяем, не потерял ли игрок своего короля
            if self.is_king_captured(1):  # Проверка на захват черного короля
                self.game_over = True
                self.winner_label.config(text="Черные победили!")  # Сообщение о победе
                self.restart_button.pack()
                self.resize_and_center(640, 690)
                print("Черные победили!")  # Отладочная информация
                return

            # Если все нормально — ходит ИИ
            self.ai_move()

        elif clicked_piece and clicked_piece.isupper():  
            # Если кликнули на свою фигуру — выбираем её
            self.selected_piece = (row, col)




    
    def move_piece(self, from_pos, to_pos):
        """Перемещает фигуру и сразу проверяет победу"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]

        if self.is_valid_move(piece, from_row, from_col, to_row, to_col):
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            if piece == "P" and to_row == 0:
                self.board[to_row][to_col] = "Q"  # Белая пешка → Белый ферзь
            elif piece == "p" and to_row == 7:
                self.board[to_row][to_col] = "q"  # Черная пешка → Черный ферзь
            self.draw_pieces()

            # Проверяем, не закончилась ли игра
            if self.check_victory():
                return





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

        # Ферзь – ходит как король, но по вертикали, горизонтали и диагоналям на любое количество клеток
        if piece in ("Q", "q"):
            # Проверяем движение по горизонтали или вертикали
            if from_row == to_row:  # Горизонталь
                for col in range(min(from_col, to_col) + 1, max(from_col, to_col)):
                    if self.board[from_row][col] is not None:
                        return False  # Если на пути есть фигуры — ход невозможен
                return True
            elif from_col == to_col:  # Вертикаль
                for row in range(min(from_row, to_row) + 1, max(from_row, to_row)):
                    if self.board[row][from_col] is not None:
                        return False  # Если на пути есть фигуры — ход невозможен
                return True
            # Проверяем движение по диагонали
            elif abs(from_row - to_row) == abs(from_col - to_col):
                row_step = 1 if to_row > from_row else -1
                col_step = 1 if to_col > from_col else -1
                row, col = from_row + row_step, from_col + col_step
                while row != to_row and col != to_col:
                    if self.board[row][col] is not None:
                        return False  # Если на пути есть фигуры — ход невозможен
                    row += row_step
                    col += col_step
                return True

        return False



    
    def reset_game(self):
        """Сбрасывает игру, создавая новую доску"""
        self.board = [[None for _ in range(8)] for _ in range(8)]  # Игровое поле
        self.selected_piece = None
        self.game_over = False  # Сбрасываем флаг окончания игры
        self.init_board()

    def show_victory_message(self, message):
        """Показывает всплывающее окно с сообщением о победе и перезапускает игру"""
        self.game_over = True  # Игра завершена
        messagebox.showinfo("Победа!", message)
        self.reset_game()  # Сброс игры после победы
    
    def check_victory(self):
        """Проверяет, остался ли на доске хотя бы один король"""
        white_king_alive = False
        black_king_alive = False

        for row in self.board:
            for piece in row:
                if piece == "K":
                    white_king_alive = True
                elif piece == "k":
                    black_king_alive = True

        if not white_king_alive:
            messagebox.showinfo("Игра окончена", "Черные победили!")
            self.game_over = True
            self.reset_game()
            return True
        elif not black_king_alive:
            messagebox.showinfo("Игра окончена", "Белые победили!")
            self.game_over = True
            self.reset_game()
            return True

        return False

    def ai_move(self):
        """ИИ делает ход, следуя приоритетам атаки и продвижения"""
        if self.game_over:
            return

        # Список возможных ходов для каждой фигуры
        attack_moves = []  # Ходы с атакой
        promote_moves = []  # Ходы для продвижения пешек
        king_attack_moves = []  # Ходы с атакой для короля
        queen_attack_moves = []  # Ходы с атакой для ферзя
        queen_moves = []  # Ходы для ферзя

        # Ищем ходы для короля с рубкой (приоритетные ходы)
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == "k":  # Черный король
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if 0 <= row + dr < 8 and 0 <= col + dc < 8:
                                target = self.board[row + dr][col + dc]
                                # Король может съесть фигуру противника (Пешка, Король или Ферзь)
                                if target in ("P", "K", "Q", "p", "q"):  # Король может атаковать ферзя
                                    king_attack_moves.append(((row, col), (row + dr, col + dc)))

        # Если есть ходы с атакой для короля, ИИ будет атаковать с королем (приоритет королю)
        if king_attack_moves:
            move = random.choice(king_attack_moves)
            self.move_piece(move[0], move[1])
            self.check_victory()  # Проверка на победу после хода
            return

        # Ищем ходы для ферзя (если он есть)
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == "q":  # Черный ферзь
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move(piece, row, col, to_row, to_col):
                                target = self.board[to_row][to_col]
                                # Ферзь может атаковать или двигаться
                                if target in ("P", "K", "Q", "p", "q"):  # Если фигура на целевой клетке противник
                                    queen_attack_moves.append(((row, col), (to_row, to_col)))
                                elif target is None:  # Если клетка пуста — обычный ход
                                    queen_moves.append(((row, col), (to_row, to_col)))

        # Если есть ходы с атакой для ферзя, ИИ будет атаковать с ферзем
        if queen_attack_moves:
            move = random.choice(queen_attack_moves)
            self.move_piece(move[0], move[1])
            self.check_victory()  # Проверка на победу после хода
            return

        # Если ферзь может двигаться, но не атакует — ИИ будет двигаться ферзем
        if queen_moves:
            move = random.choice(queen_moves)
            self.move_piece(move[0], move[1])
            self.check_victory()  # Проверка на победу после хода
            return

        # Ищем ходы для атакующих пешек
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == "p":  # Черная пешка
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move(piece, row, col, to_row, to_col):
                                target = self.board[to_row][to_col]
                                if target in ("P", "K", "Q", "p", "q"):  # Если враг (пешка или король или ферзь)
                                    attack_moves.append(((row, col), (to_row, to_col)))

        # Если есть атакующие ходы для пешек
        if attack_moves:
            move = random.choice(attack_moves)
            self.move_piece(move[0], move[1])
            self.check_victory()  # Проверка на победу после хода
            return

        # Если нет атакующих ходов, ищем ходы для продвижения пешек
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == "p":  # Черная пешка
                    # Если пешка может двигаться вперед
                    if row < 7 and self.board[row + 1][col] is None:
                        promote_moves.append(((row, col), (row + 1, col)))
                    # Пешка может бить по диагонали
                    if col > 0 and row < 7 and self.board[row + 1][col - 1] in ("P", "K", "Q"):
                        promote_moves.append(((row, col), (row + 1, col - 1)))
                    if col < 7 and row < 7 and self.board[row + 1][col + 1] in ("P", "K", "Q"):
                        promote_moves.append(((row, col), (row + 1, col + 1)))

        # Если есть ходы для продвижения пешек, ИИ продвигает одну пешку
        if promote_moves:
            move = random.choice(promote_moves)
            self.move_piece(move[0], move[1])
            self.check_victory()  # Проверка на победу после хода
            return

        # Когда нет атакующих ходов и ходов для продвижения пешек, ИИ ищет ход для короля
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == "k":  # Черный король
                    possible_moves = []
                    # Пробуем все 8 возможных направлений для короля
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if 0 <= row + dr < 8 and 0 <= col + dc < 8:
                                target = self.board[row + dr][col + dc]
                                # Если клетка пуста или противник — ходим
                                if target is None or target in ("P", "K", "Q", "p", "q"):
                                    possible_moves.append(((row, col), (row + dr, col + dc)))

                    # Если есть возможные ходы для короля, делаем случайный ход
                    if possible_moves:
                        move = random.choice(possible_moves)
                        self.move_piece(move[0], move[1])
                        self.check_victory()  # Проверка на победу после хода
                        return












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
