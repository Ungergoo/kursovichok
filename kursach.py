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
        """Создаем шахматную доску и добавляем координаты за ее пределами"""
        cell_size = 50  # Размер клетки
        board_size = 8 * cell_size  # Размер доски
        offset = 20  # Отступ для координат

        # Увеличиваем размер холста, чтобы вместить координаты
        self.canvas.config(width=board_size + offset, height=board_size + offset)

        colors = ["white", "gray"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(
                    col * cell_size + offset, row * cell_size,
                    (col + 1) * cell_size + offset, (row + 1) * cell_size,
                    fill=color
                )

        # Добавляем координаты (цифры 1-8 слева)
        for row in range(8):
            self.canvas.create_text(
                offset // 2, row * cell_size + cell_size // 2,
                text=str(8 - row), font=("Arial", 14, "bold")
            )

        # Добавляем координаты (буквы A-H снизу)
        for col in range(8):
            self.canvas.create_text(
                col * cell_size + offset + cell_size // 2, board_size + offset // 2,
                text=chr(65 + col), font=("Arial", 14, "bold")
            )




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
        """Рисуем фигуры на доске с использованием изображений"""
        self.canvas.delete("piece")  # Удаляем старые фигуры

        # Загружаем изображения для фигур
        self.images = {
            "wK": tk.PhotoImage(file="w_king.png"),
            "bK": tk.PhotoImage(file="b_king.png"),
            "wQ": tk.PhotoImage(file="w_queen.png"),
            "bQ": tk.PhotoImage(file="b_queen.png"),
            "wP": tk.PhotoImage(file="w_pawn.png"),
            "bP": tk.PhotoImage(file="b_pawn.png")
        }

        # Размер клетки на доске
        cell_size = 50

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    # Определяем, какое изображение использовать в зависимости от фигуры
                    if piece == "K":  # Белый король
                        img = self.images["wK"]
                    elif piece == "k":  # Черный король
                        img = self.images["bK"]
                    elif piece == "Q":  # Белый ферзь
                        img = self.images["wQ"]
                    elif piece == "q":  # Черный ферзь
                        img = self.images["bQ"]
                    elif piece == "P":  # Белая пешка
                        img = self.images["wP"]
                    elif piece == "p":  # Черная пешка
                        img = self.images["bP"]

                    # Вычисляем координаты для размещения изображения
                    x, y = col * cell_size + 45, row * cell_size + 20

                    # Размещаем изображение на доске
                    self.canvas.create_image(x, y, image=img, tags="piece")



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
    
    def get_all_valid_moves(self, piece, row, col):
        """Возвращает все допустимые ходы для данной фигуры"""
        valid_moves = []
        
        for r in range(8):
            for c in range(8):
                if self.is_valid_move(piece, row, col, r, c):
                    valid_moves.append((r, c))
        
        return valid_moves
    def is_check(self, color):
        """Проверяет, находится ли король на текущем цвете под шахом."""
        king_pos = self.find_king(color)  # Находим положение короля
        if not king_pos:
            return False  # Если король не найден (ошибка, хотя быть не должно)

        king_row, king_col = king_pos
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.isupper() if color == 'black' else piece.islower():
                    # Проверка, если фигура противника угрожает королю
                    valid_moves = self.get_all_valid_moves(piece, row, col)
                    for move in valid_moves:
                        to_row, to_col = move
                        if to_row == king_row and to_col == king_col:
                            return True  # Если фигура может попасть на клетку с королем
        return False
    def find_king(self, color):
        """Находит позицию короля на поле для данного цвета."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece == 'k' and color == 'black') or (piece == 'K' and color == 'white'):
                    return row, col  # Возвращаем позицию короля
        return None
    def is_safe_move(self, row, col):
        """Проверяет, безопасен ли ход на данную клетку для короля."""
        if not (0 <= row < 8 and 0 <= col < 8):
            return False  # Клетка вне поля

        target_piece = self.board[row][col]
        if target_piece and target_piece.islower():
            return False  # Если на клетке своя фигура, то ход невозможен

        # Проверяем, не будет ли эта клетка под атакой
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.isupper():  # Вражеская фигура
                    valid_moves = self.get_all_valid_moves(piece, r, c)
                    for move in valid_moves:
                        to_row, to_col = move
                        if to_row == row and to_col == col:
                            return False  # Клетка под атакой
        return True
    def king_escape(self):
        """Логика ухода короля от шаха, проверяет, не окажется ли король под шахом после хода."""
        king_pos = self.find_king('black')  # Найдем короля черных
        if not king_pos:
            return False  # Если король не найден, это ошибка

        king_row, king_col = king_pos
        # Перебираем все возможные клетки, куда может пойти король
        possible_moves = [
            (king_row - 1, king_col - 1), (king_row - 1, king_col), (king_row - 1, king_col + 1),
            (king_row, king_col - 1),                       (king_row, king_col + 1),
            (king_row + 1, king_col - 1), (king_row + 1, king_col), (king_row + 1, king_col + 1)
        ]

        # Пробуем найти безопасный ход
        for row, col in possible_moves:
            if self.is_safe_move(row, col):
                # Пробуем временно переместить короля на новую клетку
                self.move_piece((king_row, king_col), (row, col))
                # После перемещения проверяем, не находится ли король снова под шахом
                if not self.is_check('black'):  # Если король не под шахом, ход безопасен
                    return True  # Ход сделан

                # Если король всё равно под шахом, отменяем ход и пробуем следующую клетку
                self.move_piece((row, col), (king_row, king_col))

        # Если нет безопасных ходов, возвращаем False (нет возможного ухода)
        return False
    def is_checkmate(self, color):
        """Проверяет, находится ли король под матом для указанного цвета."""
        # Если король под шахом
        if not self.is_check(color):
            return False  # Если король не под шахом, нет мата

        # Проверяем, может ли король уйти из шаха
        if self.king_escape():
            return False  # Если есть возможность уйти из шаха, значит мата нет

        # Если нет безопасных ходов для короля, проверяем, можно ли предотвратить мат
        return True

    def ai_move(self):
        """ИИ делает ход по приоритетам: рубка, ферзь, продвижение пешки, обычное движение и уход от шаха."""
        ai_moves = []  # Для хранения обычных ходов
        pawn_moves = []  # Для хранения ходов пешек
        capture_moves = []  # Для хранения ходов, где есть возможность рубки
        queen_moves = []  # Для хранения ходов ферзя
        king_moves = []  # Для хранения ходов короля

        # Сначала ищем все ходы для фигур ИИ
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.islower():  # Ищем фигуры черных (проверка на наличие фигуры)
                    valid_moves = self.get_all_valid_moves(piece, row, col)

                    for move in valid_moves:
                        to_row, to_col = move
                        target_piece = self.board[to_row][to_col]

                        # 1. Если можно съесть фигуру
                        if target_piece and target_piece.isupper():  # Белая фигура
                            capture_moves.append((row, col, to_row, to_col, 3))  # Приоритет рубки

                        # 2. Ход ферзя
                        elif piece == "q":  # Ферзь
                            queen_moves.append((row, col, to_row, to_col, 2))  # Приоритет хода ферзя

                        # 3. Если это продвижение пешки (и пешка еще не достигла 7-й горизонтали)
                        elif piece == "p" and to_row == 7:
                            pawn_moves.append((row, col, to_row, to_col, 2))  # Приоритет продвижения пешки
                        elif piece == "p" and to_row != 7 and not target_piece:
                            # Если пешка не на 7-й горизонтали, но двигается вперед и не съедает
                            pawn_moves.append((row, col, to_row, to_col, 1))  # Простой ход пешки

                        # 4. Ход короля
                        elif piece == "k":  # Король
                            king_moves.append((row, col, to_row, to_col, 1))  # Приоритет хода короля

                        # 5. Обычный ход
                        elif not target_piece:
                            ai_moves.append((row, col, to_row, to_col, 1))  # Обычное движение

        # Сначала проверяем, под шахом ли король
        if self.is_check('black'):  # Проверка, если черный король под шахом
            print("Король под шахом! Ищем безопасный ход...")
            # Попробуем уйти от шаха
            if self.king_escape():  # Если удается уйти от шаха
                return  # ИИ завершает ход после того, как король ушел от шаха

        # Если рубка возможна, выполняем рубку
        if capture_moves:
            capture_moves.sort(key=lambda x: x[4], reverse=True)  # Сортируем по приоритету рубки
            best_move = capture_moves[0]
            from_row, from_col, to_row, to_col, _ = best_move
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  # После рубки ИИ завершает ход

        # Если рубки нет, проверяем, есть ли ходы для ферзя
        if queen_moves:
            queen_moves.sort(key=lambda x: x[4], reverse=True)  # Сортируем по приоритету хода ферзя
            best_move = queen_moves[0]
            from_row, from_col, to_row, to_col, _ = best_move
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  # После хода ферзя ИИ завершает ход

        # Если нет ферзя, проверяем ходы на продвижение пешки
        if pawn_moves:
            pawn_moves.sort(key=lambda x: x[4], reverse=True)  # Сортируем по приоритету продвижения
            best_move = pawn_moves[0]
            from_row, from_col, to_row, to_col, _ = best_move
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  # После продвижения пешки ИИ завершает ход

        # Если нет ни рубки, ни ферзя, ни пешки, выполняем ход королем
        if king_moves:
            king_moves.sort(key=lambda x: x[4], reverse=True)  # Сортируем по приоритету хода короля
            best_move = king_moves[0]
            from_row, from_col, to_row, to_col, _ = best_move
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  # После хода королем ИИ завершает ход

        # Если нет ни рубки, ни ферзя, ни короля, выполняем обычный ход
        if ai_moves:
            ai_moves.sort(key=lambda x: x[4], reverse=True)  # Сортируем по приоритету
            best_move = ai_moves[0]
            from_row, from_col, to_row, to_col, _ = best_move
            self.move_piece((from_row, from_col), (to_row, to_col))



    def is_king_in_check(self, color):
        """Проверяет, находится ли король указанного цвета в шахе"""
        king_position = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (color == "b" and piece == "k") or (color == "w" and piece == "K"):
                    king_position = (row, col)
                    break

        if not king_position:
            return False  # Король не найден

        # Проверяем, атакует ли фигура противника короля
        opponent_color = "w" if color == "b" else "b"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.islower() if opponent_color == "b" else piece.isupper():
                    # Проверяем, атакует ли фигура противника короля
                    valid_moves = self.get_all_valid_moves(piece, row, col)
                    if king_position in valid_moves:
                        return True  # Король в шахе

        return False

    def can_defend_king(self, from_row, from_col, to_row, to_col):
        """Проверяет, может ли ход защитить короля"""
        # Проверка для защиты короля, например, путем блокировки или перемещения короля
        # Здесь может быть сложная логика в зависимости от того, как именно игра защищается от атак
        return False  # Это просто пример; в реальной игре тут будет сложная логика




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
