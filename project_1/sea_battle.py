from random import randint
import time


class GamePlayException(Exception):
    pass


class BoardErrorException(GamePlayException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку!\n'


class BoardLineError(GamePlayException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за пределы поля!\n'


class BoardInputError(GamePlayException):
    def __str__(self):
        return 'Повторите ввод, используя две цифры без пробела!\n'


class BoardInputTotal(GamePlayException):
    def __str__(self):
        return 'Вы ввели больше двух координат или добавили пробел!\n'


class BoardInputInt(GamePlayException):
    def __str__(self):
        return 'Вы ввели не цифры!\n'


class GameErrorException(GamePlayException):
    pass


class Dot:  # принимает координаты
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:  # создает корабль
    def __init__(self, long, gps, gor=0):
        self.long = long  # длина
        self.gps = gps  # местоположение
        self.gor = gor  # направление, 0 - по оси X
        self.hp = long  # жизни

    @ property
    def dots(self):  # возвращает список координат коробля
        ship_gps = []
        for i in range(self.long):
            s_x, s_y = self.gps.x, self.gps.y
            if self.gor:
                s_x += i
            else:
                s_y += i
            ship_gps.append(Dot(s_x, s_y))

        return ship_gps


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.board = [['0'] * size for _ in range(size)]
        self.hid = hid  # показывать ли корабли на доске
        self.ships_total = 0  # список убитых кораблей
        self.ships = []  # список кораблей
        self.go = []  # список ходов
        self.busy = []  # список координат кораблей

    def __str__(self):  # вывод доски в консоль
        s = ' |1|2|3|4|5|6|'
        for i, z in enumerate(self.board):
            s += f'\n{i+1}|' + '|'.join(z) + '|'
        if self.hid:
            s = s.replace('■', '0')
        return s

    def out(self, d):  # проверяем величину координат
        return not (0 <= d.x < self.size) or not (0 <= d.y < self.size)

    def add_ship(self, ship):  # добавляем корабль на доску
        for i in ship.dots:
            if self.out(i) or i in self.busy:
                raise GameErrorException()
        if self.contour(ship.dots):
            '''если контур корабля не накладывается на другие корабли,
          то устанавливаем корабль на доску'''
            for i in ship.dots:
                self.board[i.x][i.y] = '■'
                self.busy.append(Dot(i.x, i.y))
            self.ships.append(ship)
        else:
            raise GameErrorException()

    def contour(self, ship):  # создается контур вокруг корабля
        con = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]
        sf = []  # координаты контура
        for i in ship:
            for z in con:
                sf_x, sf_y = i.x + z[0], i.y + z[1]
                sf.append(Dot(sf_x, sf_y))
        for s in sf:
            if s in self.busy:
                break
        else:
            return True
        return False

    def shot(self, d):  # делаем выстрел
        if d in self.go:
            raise BoardErrorException()  # в ту же клетку
        elif self.out(d):
            raise BoardLineError()  # за пределы поля
        self.go.append(d)  # если все ок, добавляем в сделанные ходы
        for i in self.ships:  # узнаем куда попали
            if d in i.dots:
                i.hp -= 1
                self.board[d.x][d.y] = 'X'
                if i.hp == 0:
                    print('\nКорабль уничтожен!')
                    self.ships_total += 1  # считаем уничтоженные корабли для определения победы
                else:
                    print('\nКорабль подбит!')
                return True

        self.board[d.x][d.y] = 'T'
        print("\nМимо!")
        return False


class Player:
    def __init__(self, board, ai_board):
        self.board = board
        self.ai_bord = ai_board

    def ask(self):
        GameErrorException()

    def move(self):
        while True:  # цикл запроса ходов, при ошибке пробуем еще раз
            try:
                a = self.ask()
                b = self.ai_bord.shot(a)
                return b
            except GamePlayException as e:
                print(e)


class Ai(Player):  # переопределяем метод запроса для компьютера
    def ask(self):
        while True:
            d = Dot(randint(0, 5), randint(0, 5))
            if d in self.ai_bord.go:  # если такой ход был, пробуем другой
                continue
            return d


class User(Player):
    def ask(self):
        d = list(input('Введите координаты выстрела!\n'))
        if len(d) == 2:  # начинаем проверять координаты на корректность
            a, b = d
            if a.isdigit() and b.isdigit():
                a, b = int(a) - 1, int(b) - 1
                return Dot(a, b)
            else:
                raise BoardInputInt()

        else:
            raise BoardInputTotal()


class Game:
    def __init__(self):
        self.all_ships = [3, 2, 2, 1, 1, 1, 1]
        plz = self.random_board()  # доска пользователя
        comp = self.random_board()  # доска компютера
        comp.hid = True  # скрываем корабли от пользвателя
        '''дальше, в зависимости от выбранного класса, будет 
        формироваться разный запрос координат'''
        self.us = User(plz, comp)
        self.co = Ai(comp, plz)

    def random_place(self):  # созжание доски
        board = Board()
        total = 0  # счетчик попыток
        for i in self.all_ships:
            '''проходимся по списку длин кораблей, начиная с самого длинного.
            Сделаем лимит в 2000 раз на установку 1 корабля, при неудачи возвращаем 
            None вместо доски'''
            while True:
                try:
                    total += 1
                    if total > 2000:
                        return None
                    s = Ship(i, Dot(randint(0, 5), randint(0, 5)), randint(0, 1))
                    board.add_ship(s)
                except GameErrorException:  # если поймали ошибку при установки корабля,
                    continue  # то пробуем еще раз
                else:
                    break
        return board

    def random_board(self):  # пробуем создать доску, пока не получиться
        board = None
        while board is None:
            board = self.random_place()
        return board

    def greet(self):  # приветствие пользователя
        print('              Игра')
        print('-' * 37)
        print('        | Морской бой! |')
        print('-' * 37)
        time.sleep(1)
        print("Уничтожь корабли противника раньше,\n"
              "чем он уничтожит твои!")
        print('-' * 37)
        time.sleep(3)
        print('Вводи 2 координаты без пробела, определяя\n'
              'клетку выстрела. Первая цифра координат\n'
              'по оси Y, вторая по оси X.')
        print('-' * 37)
        time.sleep(6)
        print('Если ты попал по кораблю противника,\n'
              'то стреляешь еще раз!')
        print('-' * 37)
        time.sleep(4)
        print('В игре участвуют корабли длиной:\n'
              '      3, 2, 2, 1, 1, 1, 1')
        print('-' * 37)
        time.sleep(3)
        print('И последнее, корабли не могут соприкосаться\n'
              'друг с другом, расстояние между ними\n'
              'минимум одна клетка.')
        print('-' * 37)
        time.sleep(6)
        print('             Удачи!')
        print('-' * 37)
        print()
        time.sleep(2)

    def loop(self):  # игровой цикл
        c, u = self.co, self.us
        total = randint(0, 1)  # счетчик для определения хода
        print('Доска компьютера!')
        print(c.ai_bord)
        time.sleep(2)
        print()
        print('Доска Пользователя!')
        print(u.ai_bord)
        time.sleep(2)
        print()
        '''после представления досок, 
        перестреливаемся с противником
         в бесконечном цикле, до чьей - либо победы
        '''
        while True:
            total += 1
            if total % 2:
                print('Ход компьютера!')
                rep = c.move()  # стреляем
                print(c.ai_bord)  # показываем доску
                print('-'*17)
                time.sleep(3)
                if rep:  # при попадания отматываем счетчик на -1, чтобы повторить ход
                    total -= 1
                    if c.ai_bord.ships_total == 7:  # и проверяем на победу
                        print("Победил Компьютер!\n")
                        break
                    continue
            else:
                print('Ход Пользователя!')
                print(u.ai_bord)
                print()
                rep = u.move()
                print(u.ai_bord)
                print('-'*17)
                time.sleep(2)
                if rep:
                    total -= 1
                    if u.ai_bord.ships_total == 7:
                        print(f"Победил Пользователь!\n")
                        break
                    continue

        print('Конец игры!')

    def start(self):
        self.greet()  # запускаем приветствие
        self.loop()  # запускаем игровой цикл


g = Game()
print(g.start())

