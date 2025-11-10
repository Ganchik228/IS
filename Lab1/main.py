import tkinter as tk
from tkinter import ttk, messagebox

BOARD_SIZE = 8
FILES = "abcdefgh"
RANKS = "87654321"  # row 0 -> rank 8, row 7 -> rank 1

PIECE_SYMBOL = {
    'K': '♔',
    'k': '♚',
    'Q': '♕',
    'R': '♖',
    'B': '♗',
    'N': '♘',
}

WHITE_PIECES = ['Ферзь', 'Ладья', 'Слон', 'Конь']
PIECE_SHORT = {'Ферзь':'Q','Ладья':'R','Слон':'B','Конь':'N'}


def rc_to_sq(r,c):
    return r*8 + c

def sq_to_rc(sq):
    return divmod(sq, 8)

def sq_to_alg(sq):
    r,c = sq_to_rc(sq)
    return FILES[c] + RANKS[r]

def on_board(r,c):
    return 0 <= r < 8 and 0 <= c < 8

# generate attacked squares by a single white piece (ignoring 'turn' rules)
def attacks_by(piece, sq, board):
    r,c = sq_to_rc(sq)
    attacked = set()
    if piece == 'N':
        for dr,dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            rr,cc = r+dr, c+dc
            if on_board(rr,cc):
                attacked.add(rc_to_sq(rr,cc))
    elif piece == 'B' or piece == 'R' or piece == 'Q':
        directions = []
        if piece in ('B','Q'):
            directions += [(-1,-1),(-1,1),(1,-1),(1,1)]
        if piece in ('R','Q'):
            directions += [(-1,0),(1,0),(0,-1),(0,1)]
        for dr,dc in directions:
            rr,cc = r+dr, c+dc
            while on_board(rr,cc):
                s = rc_to_sq(rr,cc)
                attacked.add(s)
                # stop if any piece blocks further sliding
                if s in board:
                    break
                rr += dr; cc += dc
    return attacked


def any_white_attacks(square, white_pieces, board):
    for p, sq in white_pieces:
        if square in attacks_by(p, sq, board):
            return True
    return False


def kings_adjacent(sq1, sq2):
    r1,c1 = sq_to_rc(sq1); r2,c2 = sq_to_rc(sq2)
    return max(abs(r1-r2), abs(c1-c2)) <= 1


def black_has_legal_king_move(bk_sq, white_pieces, board):
    r,c = sq_to_rc(bk_sq)
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if dr==0 and dc==0: continue
            rr,cc = r+dr, c+dc
            if not on_board(rr,cc): continue
            s = rc_to_sq(rr,cc)
            # can't move onto white king
            if s == board.get('white_king_sq'):
                continue
            # kings can't be adjacent after move
            if kings_adjacent(s, board.get('white_king_sq')):
                continue
            # capture consideration
            new_white = [ (p,pos) for p,pos in white_pieces if pos != s ]
            tmp_board = {}
            tmp_board['white_king_sq'] = board.get('white_king_sq')
            for p,pos in new_white:
                tmp_board[pos] = p
            if not any_white_attacks(s, new_white, tmp_board):
                return True
    return False


def is_in_check(bk_sq, white_pieces, board):
    return any_white_attacks(bk_sq, white_pieces, board)

#####################################
# GUI / Search routine (manual black king placement, white pieces selected via dropdowns)
#####################################
class MateFinderApp:
    def __init__(self, root):
        self.root = root
        root.title("Мат/Пат генератор — выбрать чёрного короля, выбрать типы белых фигур и найти")
        self.selected_black = None
        self.solutions = []
        self.index = 0

        top = ttk.Frame(root)
        top.pack(side='top', fill='x', padx=8, pady=6)

        # Piece type selectors (like first version)
        ttk.Label(top, text="Белая фигура 1:").grid(row=0,column=0, sticky='w')
        self.p1 = tk.StringVar(value=WHITE_PIECES[0])
        ttk.Combobox(top, textvariable=self.p1, values=WHITE_PIECES, state='readonly').grid(row=0,column=1)

        ttk.Label(top, text="Белая фигура 2:").grid(row=0,column=2, sticky='w', padx=(12,0))
        self.p2 = tk.StringVar(value=WHITE_PIECES[1])
        ttk.Combobox(top, textvariable=self.p2, values=WHITE_PIECES, state='readonly').grid(row=0,column=3)

        ttk.Button(top, text="Найти комбинации", command=self.find_combinations).grid(row=0,column=4, padx=10)
        ttk.Button(top, text="Сбросить чёрного короля", command=self.reset_black).grid(row=0,column=5, padx=6)

        # board canvas
        self.canvas = tk.Canvas(root, width=8*60, height=8*60)
        self.canvas.pack(padx=8, pady=6)
        self.canvas.bind("<Button-1>", self.on_board_click)

        # controls
        ctl = ttk.Frame(root)
        ctl.pack(fill='x', padx=8, pady=(0,8))
        ttk.Button(ctl, text="<<", command=self.prev_solution).grid(row=0,column=0)
        ttk.Button(ctl, text=">>", command=self.next_solution).grid(row=0,column=1)
        ttk.Label(ctl, text="Перейти к:").grid(row=0,column=2,padx=(10,0))
        self.go_entry = ttk.Entry(ctl, width=6)
        self.go_entry.grid(row=0,column=3)
        ttk.Button(ctl, text="Перейти", command=self.goto_solution).grid(row=0,column=4, padx=(4,10))
        self.status_label = ttk.Label(ctl, text="Кликните по доске, чтобы поставить чёрного короля.")
        self.status_label.grid(row=0,column=5, columnspan=4, sticky='w')

        self.draw_board()

    def reset_black(self):
        self.selected_black = None
        self.solutions = []
        self.index = 0
        self.status_label.config(text="Чёрный король сброшен. Поставьте его кликом по доске.")
        self.draw_board()

    def draw_board(self, highlight=None, placement=None):
        self.canvas.delete("all")
        size = 60
        for r in range(8):
            for c in range(8):
                x0 = c*size; y0 = r*size; x1 = x0+size; y1=y0+size
                color = '#F0D9B5' if (r+c)%2==0 else '#B58863'
                self.canvas.create_rectangle(x0,y0,x1,y1, fill=color, outline='black')
        # draw coords
        for c in range(8):
            x = c*size + 3
            self.canvas.create_text(x, 8, anchor='nw', text=FILES[c], font=('Arial',8))
        for r in range(8):
            y = r*size + 3
            self.canvas.create_text(8, y, anchor='nw', text=RANKS[r], font=('Arial',8))

        # highlight chosen black square
        if self.selected_black is not None:
            r,c = sq_to_rc(self.selected_black)
            x0 = c*size; y0 = r*size; x1 = x0+size; y1=y0+size
            self.canvas.create_rectangle(x0+2,y0+2,x1-2,y1-2, outline='red', width=3)

        # draw pieces from placement
        if placement:
            def draw_piece(symbol, sq):
                r,c = sq_to_rc(sq)
                x = c*size + size/2
                y = r*size + size/2
                self.canvas.create_text(x,y, text=symbol, font=('Arial',28), fill='black')
            # white king
            wk = placement['white_king_sq']
            draw_piece(PIECE_SYMBOL['K'], wk)
            # white pieces
            p1,p2 = placement['p1'], placement['p2']
            draw_piece(PIECE_SYMBOL[p1[0]], p1[1])
            draw_piece(PIECE_SYMBOL[p2[0]], p2[1])
            # black king
            bk = placement['black_king_sq']
            draw_piece(PIECE_SYMBOL['k'], bk)
        else:
            if self.selected_black is not None:
                r,c = sq_to_rc(self.selected_black)
                x = c*size + size/2
                y = r*size + size/2
                self.canvas.create_text(x,y, text=PIECE_SYMBOL['k'], font=('Arial',28), fill='black')

    def on_board_click(self, event):
        size = 60
        c = int(event.x // size)
        r = int(event.y // size)
        if not on_board(r,c):
            return
        sq = rc_to_sq(r,c)
        # first click (or any click) sets black king position
        self.selected_black = sq
        self.status_label.config(text=f"Чёрный король: {sq_to_alg(sq)}")
        self.draw_board()

    def find_combinations(self):
        if self.selected_black is None:
            messagebox.showinfo("Ошибка", "Сначала выберите клетку для чёрного короля кликом по доске.")
            return
        p1 = PIECE_SHORT[self.p1.get()]
        p2 = PIECE_SHORT[self.p2.get()]
        self.status_label.config(text="Идёт поиск... (несколько секунд)")
        self.root.update_idletasks()
        black_sq = self.selected_black
        all_squares = [s for s in range(64) if s != black_sq]
        sols = []
        for wk in all_squares:
            if kings_adjacent(wk, black_sq):
                continue
            for p1sq in all_squares:
                if p1sq in (wk,): continue
                for p2sq in all_squares:
                    if p2sq in (wk,p1sq): continue
                    board = {}
                    board['white_king_sq'] = wk
                    board[p1sq] = p1
                    board[p2sq] = p2
                    white_pieces = [(p1,p1sq),(p2,p2sq)]
                    in_check = is_in_check(black_sq, white_pieces, board)
                    has_move = black_has_legal_king_move(black_sq, white_pieces, board)
                    if not has_move:
                        typ = 'mate' if in_check else 'stalemate'
                        sols.append({
                            'white_king_sq': wk,
                            'p1': (p1,p1sq),
                            'p2': (p2,p2sq),
                            'black_king_sq': black_sq,
                            'type': typ
                        })
        self.solutions = sols
        self.index = 0
        self.status_label.config(text=f"Найдено {len(sols)} комбинаций ({self.p1.get()},{self.p2.get()}).")
        if sols:
            self.show_solution(0)
        else:
            self.draw_board()

    def show_solution(self, idx):
        if not (0 <= idx < len(self.solutions)):
            return
        sol = self.solutions[idx]
        desc = f"{idx+1}/{len(self.solutions)} — {sol['type'].upper()}: Black {sq_to_alg(sol['black_king_sq'])}, WK {sq_to_alg(sol['white_king_sq'])}, {sol['p1'][0]}@{sq_to_alg(sol['p1'][1])}, {sol['p2'][0]}@{sq_to_alg(sol['p2'][1])}"
        self.status_label.config(text=desc)
        self.draw_board(highlight=sol['black_king_sq'], placement=sol)

    def prev_solution(self):
        if not self.solutions: return
        self.index = (self.index - 1) % len(self.solutions)
        self.show_solution(self.index)

    def next_solution(self):
        if not self.solutions: return
        self.index = (self.index + 1) % len(self.solutions)
        self.show_solution(self.index)

    def goto_solution(self):
        if not self.solutions: return
        try:
            v = int(self.go_entry.get())
        except:
            messagebox.showinfo("Ошибка", "Введите номер решения (целое число).")
            return
        if v < 1 or v > len(self.solutions):
            messagebox.showinfo("Ошибка", "Номер вне диапазона.")
            return
        self.index = v-1
        self.show_solution(self.index)

if __name__ == "__main__":
    root = tk.Tk()
    app = MateFinderApp(root)
    root.mainloop()
