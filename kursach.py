import tkinter as tk
from tkinter import messagebox
import json
import os
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64



# ===================== Функции работы с пользователями =====================
KEY_FILE = "encryption_key.key"  # Файл для хранения ключа шифрования
DB_FILE = 'users.json'  # Файл для хранения данных пользователей
incorrect = ('!@#$%^&*+_-=|/?><~`[]±§')
# Проверяем, существует ли ключ и загружаем его, если нет — создаём новый
def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()  
    else:
        key = get_random_bytes(16)  # 16 байт для AES-128
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

KEY = load_or_create_key()  

# Шифруем пароль с помощью AES
def encrypt_password(password):
    cipher = AES.new(KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(password.encode(), AES.block_size))  # шифруем пароль
    iv = base64.b64encode(cipher.iv).decode('utf-8')  
    ct = base64.b64encode(ct_bytes).decode('utf-8')  
    return iv + ":" + ct  

# Расшифровываем пароль с помощью AES
def decrypt_password(encrypted_password):
    try:
        iv, ct = encrypted_password.split(":")  
    except ValueError:
        raise ValueError("Неверный формат зашифрованного пароля.")
    
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)  
    pt = unpad(cipher.decrypt(ct), AES.block_size)  
    return pt.decode('utf-8')

# Загружаем пользователей из файла
def load_users():
    """Загружаем пользователей как список словарей"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return [] 

# Сохраняем пользователей в файл
def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

# ===================== Функции регистрации и авторизации =====================

def register():
    """Регистрация пользователя с проверками"""
    username = entry_username.get()
    password = entry_password.get()
    
    if len(username) < 5:
        messagebox.showerror("Ошибка", "Логин должен быть не менее 5 символов!")
        return
    
    if '@' not in username:
        messagebox.showerror("Ошибка", "Логин должен содержать символ '@'!")
        return
    
    if len(password) < 5:
        messagebox.showerror("Ошибка", "Пароль должен быть не менее 5 символов!")
        return
    
    for char in username:
        if char in incorrect and char != '@':  
            messagebox.showerror("Ошибка", f"Недопустимый символ в логине: {char}")
            return
    
    for char in password:
        if char in incorrect:
            messagebox.showerror("Ошибка", f"Недопустимый символ в пароле: {char}")
            return
    
    if '@' in password:
        messagebox.showerror("Ошибка", "Пароль не должен содержать символ '@'!")
        return
    
    users = load_users()
    if any(user['login'] == username for user in users):
        messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")
        return
    
    encrypted_password = encrypt_password(password)
    users.append({'login': username, 'password': encrypted_password})
    save_users(users)
    messagebox.showinfo("Успех", "Регистрация успешна! Теперь войдите.")

def login():
    """Авторизация пользователя с проверками"""
    username = entry_username.get()
    password = entry_password.get()
    
    if not username or not password:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return
    
    users = load_users()

    for user in users:
        if user['login'] == username:  
            try:
                if decrypt_password(user['password']) == password:
                    messagebox.showinfo("Успех", "Вход выполнен!")
                    root.destroy()  
                    start_game()  
                    break
            except ValueError:
                messagebox.showinfo("Ошибка", "Неверный формат зашифрованного пароля.")
                break
    else:
        messagebox.showinfo("Ошибка", "Неверный логин или пароль!")

# ===================== Игровая логика =====================

class ChessGame:
    def __init__(self, master):
        self.game_over = False
        self.master = master
        self.master.title("Эндшпиль: Король и пешки")
        self.master.geometry("500x550")  
        self.master.resizable(width=False, height=False)  
        self.master.configure(bg='#009999')  

        self.canvas = tk.Canvas(master, width=400, height=500, bg='#006363')  
        self.canvas.pack(side=tk.TOP, padx=20, pady=20)  

        self.reset_button = tk.Button(master, text="Сбросить игру", command=self.reset_game, 
                                    bg='#006363', fg='white', font=("Arial", 12, "bold"))
        self.reset_button.pack(side=tk.BOTTOM, padx=20, pady=20)  

        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.selected_piece = None  
        self.init_board()

        self.canvas.bind("<Button-1>", self.on_click)



    def init_board(self):
        """Создаем шахматную доску и добавляем координаты"""
        cell_size = 50  # Размер клетки
        board_size = 8 * cell_size  # Размер доски
        offset = 20  # Отступ для координат

        self.canvas.config(width=board_size + offset, height=board_size + offset)

        colors = ["white", "gray"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(
                    col * cell_size, row * cell_size,
                    (col + 1) * cell_size, (row + 1) * cell_size,
                    fill=color
                )

        #координаты (цифры 1-8)
        for row in range(8):
            self.canvas.create_text(
                offset // 2, row * cell_size + cell_size // 2,
                text=str(8 - row), font=("Arial", 14, "bold"),
                anchor="center"
            )

        #координаты (буквы A-H)
        for col in range(8):
            self.canvas.create_text(
                col * cell_size + cell_size // 2, board_size + offset // 2,
                text=chr(65 + col), font=("Arial", 14, "bold"),
                anchor="center"
            )

        positions = set()

        def get_random_empty_position(for_pawn=False, is_white=False, is_king=False):
            """Выбирает случайную пустую клетку на доске"""
            while True:
                row = random.randint(0, 7)
                col = random.randint(0, 7)

                if for_pawn:
                    if row == 0 or row == 7 or row == 1 or row == 6:  
                        continue

                if is_king:
                    if is_white:
                        if row < 4:  
                            continue
                    else:
                        if row > 3:  
                            continue

                if (row, col) not in positions:
                    positions.add((row, col))
                    return row, col

        self.wk_pos = get_random_empty_position(is_king=True, is_white=True)  # Белый король

        self.bk_pos = get_random_empty_position(is_king=True, is_white=False)  # Черный король

        king_row, king_col = self.bk_pos
        attack_positions = [
            (king_row - 1, king_col - 1), (king_row - 1, king_col), (king_row - 1, king_col + 1),  
            (king_row, king_col - 1),                    (king_row, king_col + 1),  
            (king_row + 1, king_col - 1), (king_row + 1, king_col), (king_row + 1, king_col + 1)   
        ]

        attack_positions = [
            (r, c) for r, c in attack_positions if 0 <= r < 8 and 0 <= c < 8
        ]

        self.wp1_pos = get_random_empty_position(for_pawn=True, is_white=True)
        while self.wp1_pos in attack_positions:
            self.wp1_pos = get_random_empty_position(for_pawn=True, is_white=True)

        self.wp2_pos = get_random_empty_position(for_pawn=True, is_white=True)
        while self.wp2_pos in attack_positions:
            self.wp2_pos = get_random_empty_position(for_pawn=True, is_white=True)

        self.wk_pos = get_random_empty_position(is_king=True, is_white=True)
        while self.wk_pos in attack_positions:
            self.wk_pos = get_random_empty_position(is_king=True, is_white=True)

        self.bp_pos = get_random_empty_position(for_pawn=True, is_white=False)  

        self.board[self.wk_pos[0]][self.wk_pos[1]] = "K"
        self.board[self.wp1_pos[0]][self.wp1_pos[1]] = "P"
        self.board[self.wp2_pos[0]][self.wp2_pos[1]] = "P"
        self.board[self.bk_pos[0]][self.bk_pos[1]] = "k"
        self.board[self.bp_pos[0]][self.bp_pos[1]] = "p"

        self.draw_pieces()




    def draw_pieces(self):
        """Рисуем фигуры на доске с использованием изображений"""
        self.canvas.delete("piece")  

        self.images = {
            "wK": tk.PhotoImage(file="w_king.png"),
            "bK": tk.PhotoImage(file="b_king.png"),
            "wQ": tk.PhotoImage(file="w_queen.png"),
            "bQ": tk.PhotoImage(file="b_queen.png"),
            "wP": tk.PhotoImage(file="w_pawn.png"),
            "bP": tk.PhotoImage(file="b_pawn.png")
        }

        cell_size = 50

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    img = None
                    if piece == "K":  
                        img = self.images["wK"]
                    elif piece == "k":  
                        img = self.images["bK"]
                    elif piece == "Q":  
                        img = self.images["wQ"]
                    elif piece == "q":  
                        img = self.images["bQ"]
                    elif piece == "P":  
                        img = self.images["wP"]
                    elif piece == "p":  
                        img = self.images["bP"]

                    if img:
                        x = col * cell_size + cell_size // 2
                        y = row * cell_size + cell_size // 2
                        self.canvas.create_image(x, y, image=img, tags="piece")




    def is_king_captured(self, player):
        """Проверяет, захвачен ли король указанного игрока"""
        if player == 1:  
            for row in range(8):
                for col in range(8):
                    if self.board[row][col] == 'K':  
                        return False  
        elif player == 2:  
            for row in range(8):
                for col in range(8):
                    if self.board[row][col] == 'k':  
                        print("Король белых на доске")  
                        return False  
        print("Король захвачен!")  
        return True  


    def on_click(self, event):
        """Обрабатываем клик по доске"""
        if self.game_over:
            return  

        col = event.x // 50
        row = event.y // 50
        clicked_piece = self.board[row][col]

        if self.selected_piece:
            from_row, from_col = self.selected_piece

            if clicked_piece and clicked_piece.isupper():
                self.selected_piece = (row, col)
                return  

            if not self.is_valid_move(self.board[from_row][from_col], from_row, from_col, row, col):
                self.selected_piece = None
                return

            self.move_piece(self.selected_piece, (row, col))
            self.selected_piece = None

            # Проверяем, не потерял ли игрок своего короля
            if self.is_king_captured(1):  
                self.game_over = True
                self.winner_label.config(text="Черные победили!")  
                self.restart_button.pack()
                self.resize_and_center(640, 690)
                return

            self.ai_move()

        elif clicked_piece and clicked_piece.isupper():  
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
                self.board[to_row][to_col] = "Q"  
            elif piece == "p" and to_row == 7:
                self.board[to_row][to_col] = "q"  
            self.draw_pieces()

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
                return True  

            if abs(from_col - to_col) == 1 and from_row - to_row == 1 and target_piece and target_piece.islower():
                return True  

        # Черная пешка
        if piece == "p":
            if from_col == to_col and to_row - from_row == 1 and target_piece is None:
                return True  

            if abs(from_col - to_col) == 1 and to_row - from_row == 1 and target_piece and target_piece.isupper():
                return True  



        # Ферзь – ходит как король, но по вертикали, горизонтали и диагоналям на любое количество клеток
        if piece in ("Q", "q"):
            if from_row == to_row:  
                for col in range(min(from_col, to_col) + 1, max(from_col, to_col)):
                    if self.board[from_row][col] is not None:
                        return False  
                return True
            elif from_col == to_col:  
                for row in range(min(from_row, to_row) + 1, max(from_row, to_row)):
                    if self.board[row][from_col] is not None:
                        return False  
                return True
            elif abs(from_row - to_row) == abs(from_col - to_col):
                row_step = 1 if to_row > from_row else -1
                col_step = 1 if to_col > from_col else -1
                row, col = from_row + row_step, from_col + col_step
                while row != to_row and col != to_col:
                    if self.board[row][col] is not None:
                        return False  
                    row += row_step
                    col += col_step
                return True

        return False



    
    def reset_game(self):
        """Сбрасывает игру, создавая новую доску"""
        self.board = [[None for _ in range(8)] for _ in range(8)]  
        self.selected_piece = None
        self.game_over = False  
        self.init_board()

    def show_victory_message(self, message):
        """Показывает всплывающее окно с сообщением о победе и перезапускает игру"""
        self.game_over = True 
        messagebox.showinfo("Победа!", message)
        self.reset_game()  
    
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
        king_pos = self.find_king(color)  
        if not king_pos:
            return False 

        king_row, king_col = king_pos
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.isupper() if color == 'black' else piece.islower():
                    valid_moves = self.get_all_valid_moves(piece, row, col)
                    for move in valid_moves:
                        to_row, to_col = move
                        if to_row == king_row and to_col == king_col:
                            return True  
        return False
    def find_king(self, color):
        """Находит позицию короля на поле для данного цвета."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece == 'k' and color == 'black') or (piece == 'K' and color == 'white'):
                    return row, col  
        return None


    def is_safe_move(self, row, col):
        """Проверяет, безопасен ли ход на данную клетку для короля, включая атаки со стороны вражеских фигур."""
        if not (0 <= row < 8 and 0 <= col < 8):
            return False  

        target_piece = self.board[row][col]
        if target_piece and target_piece.islower():
            return False  

        if self.is_under_attack(row, col):  
            return False  

        return True


    def is_under_attack(self, row, col):
        """Проверяет, атакует ли клетку вражеская фигура."""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.isupper():  
                    valid_moves = self.get_all_valid_moves(piece, r, c)
                    for move in valid_moves:
                        to_row, to_col = move
                        if to_row == row and to_col == col:
                            return True  
        return False


    def king_escape(self):
        """Логика ухода короля от шаха, проверяет, не окажется ли король под шахом после хода и не подставится ли он под рубку от вражеских фигур."""
        king_pos = self.find_king('black')  
        if not king_pos:
            return False  

        king_row, king_col = king_pos
        possible_moves = [
            (king_row - 1, king_col - 1), (king_row - 1, king_col), (king_row - 1, king_col + 1),
            (king_row, king_col - 1),                       (king_row, king_col + 1),
            (king_row + 1, king_col - 1), (king_row + 1, king_col), (king_row + 1, king_col + 1)
        ]

        for row, col in possible_moves:
            if self.is_safe_move(row, col) and not self.is_under_attack(row, col):
                self.move_piece((king_row, king_col), (row, col))
                if not self.is_check('black'): 
                    return True 

                self.move_piece((row, col), (king_row, king_col))

        return False

    def simulate_move(self, from_row, from_col, to_row, to_col):
        """Временный ход для проверки безопасности"""
        self.temp_piece = self.board[to_row][to_col]  
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None

    def undo_move(self, from_row, from_col, to_row, to_col):
        """Откат хода после проверки"""
        self.board[from_row][from_col] = self.board[to_row][to_col]
        self.board[to_row][to_col] = self.temp_piece
        self.temp_piece = None

    def ai_move(self):
        """ИИ делает ход по приоритетам: взятие короля, рубка, ферзь, продвижение пешки, обычное движение и уход от шаха."""
        ai_moves = []  # Обычные ходы
        pawn_moves = []  # Ходы пешек
        capture_moves = []  # Обычные взятия
        queen_moves = []  # Ходы ферзя
        king_moves = []  # Ходы короля (избегает шаха)
        safe_king_moves = []  # Безопасные ходы короля
        king_capture = []  # Самый приоритетный ход – взятие короля

        #  Проверяем, можно ли сразу взять короля
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.islower():  
                    valid_moves = self.get_all_valid_moves(piece, row, col)

                    for move in valid_moves:
                        to_row, to_col = move
                        target_piece = self.board[to_row][to_col]

                        if target_piece == "K":  
                            king_capture.append((row, col, to_row, to_col, 999))

        # Если можно сразу взять короля, делаем это
        if king_capture:
            from_row, from_col, to_row, to_col, _ = king_capture[0]
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  

        # Если король под шахом, ищем безопасный ход или рубку
        if self.is_check('black'):
            print("Король под шахом! Ищем безопасный ход...")
            
            # Проверим, может ли король взять фигуру
            king_row, king_col = self.find_king('black')
            valid_king_moves = self.get_all_valid_moves('k', king_row, king_col)
            for move in valid_king_moves:
                to_row, to_col = move
                target_piece = self.board[to_row][to_col]
                if target_piece and target_piece.isupper():  
                    capture_moves.append((king_row, king_col, to_row, to_col, 3))

            if capture_moves:  
                capture_moves.sort(key=lambda x: x[4], reverse=True)
                from_row, from_col, to_row, to_col, _ = capture_moves[0]
                self.move_piece((from_row, from_col), (to_row, to_col))
                return  

            #  Если король не может рубить, пытаемся найти безопасные ходы.
            if self.king_escape():  
                return 

        

        king_under_check = self.is_check('black')  

        # Перебираем все фигуры ИИ
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.islower():  # Черные фигуры
                    valid_moves = self.get_all_valid_moves(piece, row, col)

                    for move in valid_moves:
                        to_row, to_col = move
                        target_piece = self.board[to_row][to_col]

                        # Взятие короля
                        if target_piece == "K":  
                            king_capture.append((row, col, to_row, to_col, 999))

                        if king_under_check and piece == "k":
                            if not self.is_under_attack(to_row, to_col):
                                safe_king_moves.append((row, col, to_row, to_col, 10))  
                            continue  

                        # Взятие любой белой фигуры 
                        if target_piece and target_piece.isupper() and piece != "k":  
                            capture_moves.append((row, col, to_row, to_col, 3))

                        # Ход ферзя
                        elif piece == "q":
                            queen_moves.append((row, col, to_row, to_col, 2))

                        # Продвижение пешки
                        elif piece == "p" and to_row == 7:
                            pawn_moves.append((row, col, to_row, to_col, 2))
                        elif piece == "p" and not target_piece:
                            pawn_moves.append((row, col, to_row, to_col, 1))

                        # Обычный ход короля 
                        elif piece == "k" and not self.is_under_attack(to_row, to_col):
                            if to_row in (0, 7) or to_col in (0, 7):
                                king_moves.append((row, col, to_row, to_col, 0))  
                            else:
                                king_moves.append((row, col, to_row, to_col, 1))

                        elif not target_piece:
                            ai_moves.append((row, col, to_row, to_col, 1))




        # Если можно рубить фигуру, делаем это
        if capture_moves:
            capture_moves.sort(key=lambda x: x[4], reverse=True)
            from_row, from_col, to_row, to_col, _ = capture_moves[0]
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  

        # Ход ферзя
        if queen_moves:
            queen_moves.sort(key=lambda x: x[4], reverse=True)
            from_row, from_col, to_row, to_col, _ = queen_moves[0]
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  

        # Продвижение пешки
        if pawn_moves:
            pawn_moves.sort(key=lambda x: x[4], reverse=True)
            from_row, from_col, to_row, to_col, _ = pawn_moves[0]
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  

        # Обычный ход короля
        if king_moves:
            king_moves.sort(key=lambda x: x[4], reverse=True)
            from_row, from_col, to_row, to_col, _ = king_moves[0]
            self.move_piece((from_row, from_col), (to_row, to_col))
            return  

        # Обычный ход
        if ai_moves:
            ai_moves.sort(key=lambda x: x[4], reverse=True)
            from_row, from_col, to_row, to_col, _ = ai_moves[0]
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
            return False  

        opponent_color = "w" if color == "b" else "b"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.islower() if opponent_color == "b" else piece.isupper():
                    valid_moves = self.get_all_valid_moves(piece, row, col)
                    if king_position in valid_moves:
                        return True  

        return False

def start_game():
    """Запуск игры"""
    game_window = tk.Tk()
    ChessGame(game_window)
    game_window.mainloop()

# ===================== Интерфейс авторизации =====================

root = tk.Tk()
root.title('Вход/регистрация')
root.geometry("400x200")
root.resizable(width=False, height=False)
root.configure(bg='#009999')

# Логин
log_label = tk.Label(root, bg='#009999', text='Логин', font=('Arial', 12))
log_label.pack(pady=5)
entry_username = tk.Entry(root, bg='#006363',fg='white', font=('Arial', 12))
entry_username.pack(pady=5)

# Пароль
password_label = tk.Label(root, bg='#009999', text='Пароль', font=('Arial', 12))
password_label.pack(pady=5)
entry_password = tk.Entry(root, bg='#006363',fg='white', font=('Arial', 12), show="*")
entry_password.pack(pady=5)

# Кнопка "Вход"
btn_log = tk.Button(root, text='Войти', bg='#006363', fg='white', font=('Arial', 12), command=login)
btn_log.pack()

# Кнопка "Зарегистрироваться"
btn_reg = tk.Button(root, text='Зарегестрироваться', bg='#006363', fg='white', font=('Arial', 12), command=register)
btn_reg.pack()

root.mainloop()
