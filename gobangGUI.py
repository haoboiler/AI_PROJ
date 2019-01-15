#!/usr/bin/env python
# -*- coding:utf-8 -*-


from chessboard import ChessBoard
#gkh: get global value from ai#######
from ai import searcher, blackweight_list, whiteweight_list ,last_value, now_value,black_last_count, white_last_count


WIDTH = 540
HEIGHT = 540
MARGIN = 22
GRID = (WIDTH - 2 * MARGIN) / (15 - 1)
PIECE = 34
EMPTY = 0
BLACK = 1
WHITE = 2

import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QPainter
from PyQt5.QtMultimedia import QSound
import csv, os

# ----------------------------------------------------------------------
# 定义线程类执行AI的算法
# ----------------------------------------------------------------------
class AI(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int, int)

    # 构造函数里增加形参
    def __init__(self, board, turn ,parent=None):
        super(AI, self).__init__(parent)
        self.board = board
        self.turn = turn


    # 重写 run() 函数
    def run(self):
        self.ai = searcher()
        self.ai.board = self.board
        # turn, depth
        # turn = 2 玩家先手，AI后手
        # turn = 1 AI先手，玩家后手
        score, x, y = self.ai.search(self.turn, 2)
        ##########gkh:learning weight function
        difference = 0
        if last_value != 0:
            difference = self.get_difference(0.9)
        if difference != 0:
            self.learning_weight(0.1, difference)
        #############
        self.finishSignal.emit(x, y)
    
    ####gkh: get difference function
    def get_difference(discount):
        return now_value * discount - last_value

    ####gkh: learning weight function
    def learning_weight(learning_rate, difference):
        if turn == 1:
            for i in range(len(blackweight_list)):
                blackweight_list[i] += learning_rate * difference * black_last_count[i]
        if turn == 2:
            for i in range(len(whiteweight_list)):
                whiteweight_list[i] += learning_rate * difference * white_last_count[i]

# ----------------------------------------------------------------------
# 重新定义Label类
# ----------------------------------------------------------------------
class LaBel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)

    def enterEvent(self, e):
        e.ignore()


class GoBang(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.chessboard = ChessBoard()  # 棋盘类

        palette1 = QPalette()  # 设置棋盘背景
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('img/chessboard.jpg')))
        self.setPalette(palette1)
        # self.setStyleSheet("board-image:url(img/chessboard.jpg)")  # 不知道这为什么不行
        self.setCursor(Qt.PointingHandCursor)  # 鼠标变成手指形状
        self.sound_piece = QSound("sound/luozi.wav")  # 加载落子音效
        self.sound_win = QSound("sound/win.wav")  # 加载胜利音效
        self.sound_defeated = QSound("sound/defeated.wav")  # 加载失败音效

        self.resize(WIDTH, HEIGHT)  # 固定大小 540*540
        self.setMinimumSize(QtCore.QSize(WIDTH, HEIGHT))
        self.setMaximumSize(QtCore.QSize(WIDTH, HEIGHT))

        self.setWindowTitle("GoBang")  # 窗口名称
        self.setWindowIcon(QIcon('img/black.png'))  # 窗口图标

        # self.lb1 = QLabel('            ', self)
        # self.lb1.move(20, 10)

        self.black = QPixmap('img/black.png')
        self.white = QPixmap('img/white.png')

        self.piece_now = BLACK  # 黑棋先行
        # self.my_turn = False  # 玩家先行
        self.step = 0  # 步数
        self.x, self.y = 1000, 1000

        self.mouse_point = LaBel(self)  # 将鼠标图片改为棋子
        self.mouse_point.setScaledContents(True)
        # self.mouse_point.setPixmap(self.black)  # 加载黑棋
        self.mouse_point.setGeometry(270, 270, PIECE, PIECE)
        self.pieces = [LaBel(self) for i in range(225)]  # 新建棋子标签，准备在棋盘上绘制棋子
        for piece in self.pieces:
            piece.setVisible(True)  # 图片可视
            piece.setScaledContents(True)  # 图片大小根据标签大小可变
        #gkh for weight reading##########
        f = open('./data/blackweight', 'r')
        line = f.readline()
        while line:
          blackweight_list.append(int(line[0:-1]))
          line = f.readline()
        f.close()
        f = open('./data/whiteweight', 'r')
        line = f.readline()
        while line:
          whiteweight_list.append(int(line[0:-1]))
          line = f.readline()
        f.close()
        print(blackweight_list, whiteweight_list)
        ###############
        #print(weight_list)
        self.mouse_point.raise_()  # 鼠标始终在最上层
        self.ai_down = True  # AI已下棋，主要是为了加锁，当值是False的时候说明AI正在思考，这时候玩家鼠标点击失效，要忽略掉 mousePressEvent

        self.setMouseTracking(True)
        self.show()

        # 玩家选择是否先手
        self.my_turn = QMessageBox.question(self, 'Let\'s play a game!','是否选择先手？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if self.my_turn == QMessageBox.No:
            # self.mouse_point.setPixmap(self.white)  # 加载白棋


            #################
            self.ai_down = False
            board = self.chessboard.board()
            ##########gkh : AI get the list
            self.AI = AI(board, 1)  # 新建线程对象，传入棋盘参数
            self.AI.finishSignal.connect(self.AI_draw)  # 结束线程，传出参数
            self.AI.start()  # run

    def paintEvent(self, event):  # 画出指示箭头
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()

    # def mouseMoveEvent(self, e):  # 黑色棋子随鼠标移动
    #     # self.lb1.setText(str(e.x()) + ' ' + str(e.y()))
    #     self.mouse_point.move(e.x() - 16, e.y() - 16)

    def mousePressEvent(self, e):  # 玩家下棋
        if e.button() == Qt.LeftButton and self.ai_down == True:
            x, y = e.x(), e.y()  # 鼠标坐标
            i, j = self.coordinate_transform_pixel2map(x, y)  # 对应棋盘坐标
            if not i is None and not j is None:  # 棋子落在棋盘上，排除边缘
                if self.chessboard.get_xy_on_logic_state(i, j) == EMPTY:  # 棋子落在空白处
                    self.draw(i, j)

                    self.ai_down = False
                    board = self.chessboard.board()
                    if self.piece_now == WHITE: # 玩家先手黑棋 已下完
                        self.AI = AI(board,2)  # 新建线程对象，传入棋盘参数
                    else:
                        self.AI = AI(board,1) # 玩家后手，AI先手
                    self.AI.finishSignal.connect(self.AI_draw)  # 结束线程，传出参数
                    self.AI.start()  # run



    def AI_draw(self, i, j):
        # if self.step != 0:
        self.draw(i, j)  # AI
        self.x, self.y = self.coordinate_transform_map2pixel(i, j)
        self.ai_down = True
        self.update()

    def draw(self, i, j):
        x, y = self.coordinate_transform_map2pixel(i, j)

        if self.piece_now == BLACK:
            self.pieces[self.step].setPixmap(self.black)  # 放置黑色棋子


            self.piece_now = WHITE
            self.chessboard.draw_xy(i, j, BLACK)

        else:
            self.pieces[self.step].setPixmap(self.white)  # 放置白色棋子
            self.piece_now = BLACK
            self.chessboard.draw_xy(i, j, WHITE)

        self.pieces[self.step].setGeometry(x, y, PIECE, PIECE)  # 画出棋子
        self.sound_piece.play()  # 落子音效
        self.step += 1  # 步数+1

        #gkh: check if there is rule breaker
        rulerbreak = False
        if self.piece_now == WHITE:
            rulerbreak = self.chessboard.breakrule(i, j)
            if (rulerbreak == True):
                self.gameover(2)
        if rulerbreak == False:
        #gkh :modify end at this place
            winner = self.chessboard.anyone_win(i, j)  # 判断输赢
            if winner != EMPTY:
                self.mouse_point.clear()
                self.gameover(winner)

    def drawLines(self, qp):  # 指示AI当前下的棋子
        # if self.step != 0:
            pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(self.x - 5, self.y - 5, self.x + 3, self.y + 3)
            qp.drawLine(self.x + 3, self.y, self.x + 3, self.y + 3)
            qp.drawLine(self.x, self.y + 3, self.x + 3, self.y + 3)

    def coordinate_transform_map2pixel(self, i, j):
        # 从 chessMap 里的逻辑坐标到 UI 上的绘制坐标的转换
        return MARGIN + j * GRID - PIECE / 2, MARGIN + i * GRID - PIECE / 2

    def coordinate_transform_pixel2map(self, x, y):
        # 从 UI 上的绘制坐标到 chessMap 里的逻辑坐标的转换
        i, j = int(round((y - MARGIN) / GRID)), int(round((x - MARGIN) / GRID))
        # 有MAGIN, 排除边缘位置导致 i,j 越界
        if i < 0 or i >= 15 or j < 0 or j >= 15:
            return None, None
        else:
            return i, j

    def gameover(self, winner):
        ######gkh: game over update 
        f = open('./data/blackweight', 'w')
        for i in range(len(blackweight_list)):
          f.write(str(blackweight_list[i]) + '\n')
        f.close()
        f = open('./data/whiteweight', 'w')
        for i in range(len(whiteweight_list)):
          f.write(str(whiteweight_list[i]) + '\n')
        f.close()
        ###################
        if winner == BLACK:
            self.sound_win.play()
            reply = QMessageBox.question(self, 'Black Win!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            self.sound_defeated.play()
            reply = QMessageBox.question(self, 'Black Lost!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:  # 复位
            self.piece_now = BLACK
            # self.mouse_point.setPixmap(self.black)
            self.step = 0
            for piece in self.pieces:
                piece.clear()
            self.chessboard.reset()
            self.update()
            # ycn's code, 复盘重选先后手
            self.my_turn = QMessageBox.question(self, 'Let\'s play a game!','是否选择先手？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if self.my_turn == QMessageBox.No:
                # self.mouse_point.setPixmap(self.white)  # 加载白棋
                self.ai_down = False
                board = self.chessboard.board()
                self.AI = AI(board, 1)  # 新建线程对象，传入棋盘参数
                self.AI.finishSignal.connect(self.AI_draw)  # 结束线程，传出参数
                self.AI.start()  # run
        else:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GoBang()
    sys.exit(app.exec_())
