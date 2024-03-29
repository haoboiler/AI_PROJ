#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ----------------------------------------------------------------------
# 定义棋子类型，输赢情况
# ----------------------------------------------------------------------
EMPTY = 0
BLACK = 1
WHITE = 2


# ----------------------------------------------------------------------
# 定义棋盘类，绘制棋盘的形状，切换先后手，判断输赢等
# ----------------------------------------------------------------------
class ChessBoard(object):
    def __init__(self):
        self.__board = [[EMPTY for n in range(15)] for m in range(15)]
        self.__dir = [[(-1, 0), (1, 0)], [(0, -1), (0, 1)], [(-1, 1), (1, -1)], [(-1, -1), (1, 1)]]
        #                (左      右)      (上       下)     (左下     右上)      (左上     右下)

    def board(self):  # 返回数组对象
        return self.__board

    def draw_xy(self, x, y, state):  # 获取落子点坐标的状态
        self.__board[x][y] = state

    def get_xy_on_logic_state(self, x, y):  # 获取指定点坐标的状态
        return self.__board[x][y]

    def get_next_xy(self, point, direction):  # 获取指定点的指定方向的坐标
        x = point[0] + direction[0]
        y = point[1] + direction[1]
        if x < 0 or x >= 15 or y < 0 or y >= 15:
            return False
        else:
            return x, y

    def get_xy_on_direction_state(self, point, direction):  # 获取指定点的指定方向的状态
        if point is not False:
            xy = self.get_next_xy(point, direction)
            if xy is not False:
                x, y = xy
                return self.__board[x][y]
        return False

    def anyone_win(self, x, y):
        state = self.get_xy_on_logic_state(x, y)
        #print("state")
        #print(state)
        for directions in self.__dir:  # 对米字的4个方向分别检测是否有5子相连的棋
            count = 1
            for direction in directions:  # 对落下的棋子的同一条线的两侧都要检测，结果累积
                point = (x, y)
                #print(point)
                while True:
                    if self.get_xy_on_direction_state(point, direction) == state:
                        count += 1
                        point = self.get_next_xy(point, direction)
                    else:
                        break
            if count >= 5:
                return state
        return EMPTY

    #gkh :implement for double three check
    def check_connect(self, x, y, connect_number, newdirection = None, live = None):
        state = self.get_xy_on_logic_state(x, y)
        for directions in self.__dir:
            count = 1
            if newdirection != None and newdirection in directions:
                continue
            for direction in directions:
                point = (x,y)
                redirection = (list(direction)[0] * -1, list(direction)[1] * -1)
                if live != None:
                    if self.get_xy_on_direction_state(point, redirection) != 0:
                        continue
                while True:
                    if count == connect_number:
                        #if need not check the chess live
                        if live == None:                        
                            return point, direction
                        else:
                            if self.get_xy_on_direction_state(point, direction) != 0:
                                break
                            else:
                                return point, direction
                    elif self.get_xy_on_direction_state(point, direction) == state:
                        count += 1
                        point = self.get_next_xy(point, direction)
                    else:        
                        break
        return 0,0


    #gkh implement double three check
    def breakrule(self, x, y):
        state = self.get_xy_on_logic_state(x, y)
        #gkh : check the double three, but does not implement the live function
        newpoint, newdirection = self.check_connect(x, y, 3, live = 2)
        if newpoint != 0:
            newpoint1, newdirection1 = self.check_connect(newpoint[0], newpoint[1], 3, newdirection, live = 2)
            newpoint2, newdirection2 = self.check_connect(x, y, 3, newdirection, live = 2)
            if newpoint1 != 0 or newpoint2 != 0:
                return True
        #check the double four
        newpoint, newdirection = self.check_connect(x, y, 4)
        if newpoint != 0:
            newpoint1, newdirection1 = self.check_connect(newpoint[0], newpoint[1], 4, newdirection)
            newpoint2, newdirection2 = self.check_connect(x, y, 4, newdirection)
            if newpoint1 != 0 or newpoint2 != 0:
                return True
        #check long
        newpoint, newdirection = self.check_connect(x, y, 6)
        if newpoint != 0:
            return True
        newpoint, newdirection = self.check_connect(x, y, 7)
        if newpoint != 0:
            return True
        newpoint, newdirection = self.check_connect(x, y, 8)
        if newpoint != 0:
            return True
        newpoint, newdirection = self.check_connect(x, y, 9)
        if newpoint != 0:
            return True             
        return False





    def reset(self):  # 重置
        self.__board = [[EMPTY for n in range(15)] for m in range(15)]
