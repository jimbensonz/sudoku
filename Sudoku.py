from Cell import *
from util import *

import csv
import numpy as np
from copy import deepcopy
from keras.models import model_from_json
from collections import Counter
from PIL import Image


class Sudoku():
    def __init__(self):
        self.sudoku = [[Cell() for j in range(10)] for i in range(10)]

    def __str__(self):
        s = '\n'
        for i in range(1,10):
            for j in range(1,10):
                v = self.sudoku[i][j].value
                if v == '0':
                    s += '.'
                else:
                    s += v
                s += ' '
                if j == 3 or j == 6:
                    s += '| '
            s += '\n'
            if i == 3 or i == 6:
                s += '-'*6
                s += '+'
                s += '-'*7
                s += '+'
                s += '-'*7
                s += '\n'
        return s
    
    def __getitem__(self, idx):
        return self.sudoku[idx]

    def readCsv(self, path):
        with open(path, newline='', encoding='utf-8', errors='ignore') as csvfile:
            rows = csv.reader(csvfile)
            i = 1
            for row in rows:
                j = 1
                for num_str in row:
                    num = num_str.replace(' ', '')
                    self.sudoku[i][j].create(num, i, j)
                    j += 1
                i += 1
                
    def readImg(self, path):
        im = Image.open(path).convert('L')
        im_resize = im.resize((28*9, 28*9), Image.BILINEAR)
        pix = 255 - np.array(im_resize)
        
        # Remove Border
        _size = 28 * 9
        tol_num = 25 * 9

        # Column Border
        for j in range(_size):
            ct = Counter(pix[:, j])
            for key in ct.keys():
                if key != 0 and ct[key] >= tol_num:
                    pix[:, j] = np.zeros(_size)
            
        # Row Border
        for i in range(_size):
            ct2 = Counter(pix[i])
            for key in ct2.keys():
                if key != 0 and ct2[key] >= tol_num:
                    pix[i] = np.zeros(_size)
                    
        # Mnist Model
        json_file = open('model/mnist_model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()

        model = model_from_json(loaded_model_json)
        model.load_weights('model/mnist_model_weight.h5')

        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        
        # Number Recognition
        for i in range(1, 10):
            lst = []
            for j in range(1, 10):
                subim = pix[(i-1)*28 : i*28, (j-1)*28 : j*28]
                
                # Centering
                x_min, x_max = 28, 0
                y_min, y_max = 28, 0
                for ii in range(28):
                    for jj in range(28):
                        if subim[ii][jj] != 0:
                            if ii < y_min:
                                y_min = ii
                            elif ii > y_max:
                                y_max = ii
                            if jj < x_min:
                                x_min = jj
                            elif jj > x_max:
                                x_max = jj
                                
                x_shift = 14 - round( (x_min+x_max) / 2)
                y_shift = 14 - round( (y_min+y_max) / 2)
                subim_center = np.array(subim, copy=True)
                for ii in range(28):
                    for jj in range(28):
                        subim_center[ii][jj] = subim[(ii-y_shift)%28][(jj-x_shift)%28]

                        
                x = subim_center.reshape(1, 28, 28, 1).astype('float32')
                x_norm = x / 255
                y_pred = model.predict(x_norm)
                y_pred[0][0] = 0.5
                num = np.argmax(y_pred)
#                 if num == 9:
#                     if y_pred[0][5] > 0.33:
#                         num = 5
                self.sudoku[i][j].create(num, i, j)
    
    def done(self):
        for i in range(1, 10):
            for j in range(1, 10):
                if self.sudoku[i][j].value == '0':
                    return False
        return True
    
    def illegal(self):
        for i in range(1, 10):
            for j in range(1, 10):
                if self.sudoku[i][j].illegal():
                    return True
        return False

    def delRowCdt(self, rowID, num, protected_area = 0):
        startX = area2startX(protected_area)
        x = []
        if protected_area != 0:
            x = [startX, startX+1, startX+2]
            
        ret = False
        for j in range(1,10):
            if j not in x:
                ret |= self.sudoku[rowID][j].delCdt(num)
        return ret
                
    def delColCdt(self, colID, num, protected_area = 0):
        startY = area2startY(protected_area)
        y = []
        if protected_area != 0:
            y = [startY, startY+1, startY+2]
            
        ret = False
        for i in range(1, 10):
            if i not in y:
                ret |= self.sudoku[i][colID].delCdt(num)
        return ret
                
    def delAreaCdt(self, areaID, num):
        startX = area2startX(areaID)
        startY = area2startY(areaID)
        
        ret = False
        for i in range(startY, startY+3):
            for j in range(startX, startX+3):
                ret |= self.sudoku[i][j].delCdt(num)
        return ret

    def fillCell(self, rowID, colID, num):
        self.sudoku[rowID][colID].value = num
        self.sudoku[rowID][colID].clear()

    def updateCellCdt(self, rowID, colID, areaID, num):
        self.delRowCdt(rowID, num)
        self.delColCdt(colID, num)
        self.delAreaCdt(areaID, num)

    def updateCell(self, rowID, colID, areaID, num):
        self.fillCell(rowID, colID, num)
        self.updateCellCdt(rowID, colID, areaID, num)

    def trivial_operation(self):
        for i in range(1,10):
            for j in range(1,10):
                if self.sudoku[i][j].value != '0':
                    self.updateCell(i, j, self.sudoku[i][j].area, self.sudoku[i][j].value)
        
        modify = True
        while modify:
            modify = False
            for i in range(1, 10):
                for j in range(1, 10):
                    if self.sudoku[i][j].value == '0':
                        if len(self.sudoku[i][j].candidate) == 1:
                            self.updateCell(i, j, self.sudoku[i][j].area, self.sudoku[i][j].candidate[0])
                            modify = True

            # Row Elimination
            for i in range(1, 10):
                candidate_lst = []
                for j in range(1, 10):
                    if self.sudoku[i][j].value == '0':
                        candidate_lst += self.sudoku[i][j].candidate
                ct = Counter(candidate_lst)
                for num in ct.keys():
                    if ct[num] == 1:
                        for j in range(1, 10):
                            if self.sudoku[i][j].value == '0':
                                if num in self.sudoku[i][j].candidate:
                                    self.updateCell(i, j, self.sudoku[i][j].area, num)
                                    modify = True

            # Column Elimination
            for j in range(1, 10):
                candidate_lst = []
                for i in range(1, 10):
                    if self.sudoku[i][j].value == '0':
                        candidate_lst += self.sudoku[i][j].candidate
                ct = Counter(candidate_lst)
                for num in ct.keys():
                    if ct[num] == 1:
                        for i in range(1, 10):
                            if self.sudoku[i][j].value == '0':
                                if num in self.sudoku[i][j].candidate:
                                    self.updateCell(i, j, self.sudoku[i][j].area, num)
                                    modify = True

            # Area Elimination
            for area in range(1, 10):
                startX = area2startX(area)
                startY = area2startY(area)
                candidate_lst = []
                for i in range(startX, startX+3):
                    for j in range(startY, startY+3):
                        if self.sudoku[i][j].value == '0':
                            candidate_lst += self.sudoku[i][j].candidate
                ct = Counter(candidate_lst)
                for num in ct.keys():
                    if ct[num] == 1:
                        for i in range(startX, startX+3):
                            for j in range(startY, startY+3):
                                if self.sudoku[i][j].value == '0':
                                    if num in self.sudoku[i][j].candidate:
                                        self.updateCell(i, j, self.sudoku[i][j].area, num)
                                        modify = True

            # Advanced Elimination
            if not modify:
                print('-----------')
                for area in range(1, 10):
                    startX = area2startX(area)
                    startY = area2startY(area)

                    # Row Elimination
                    set1 = set()
                    set2 = set()
                    set3 = set()
                    for j in range(startX, startX+3):
                        set1.update(self.sudoku[startY][j].candidate)
                        set2.update(self.sudoku[startY+1][j].candidate)
                        set3.update(self.sudoku[startY+2][j].candidate)
                    for num in set1:
                        if num not in set2 and num not in set3:
                            modify |= self.delRowCdt(startY, num, protected_area = area)
                    for num in set2:
                        if num not in set1 and num not in set3:
                            modify |= self.delRowCdt(startY+1, num, protected_area = area)
                    for num in set3:
                        if num not in set1 and num not in set2:
                            modify |= self.delRowCdt(startY+2, num, protected_area = area)

                    # Column Elimination
                    set1 = set()
                    set2 = set()
                    set3 = set()
                    for i in range(startY, startY+3):
                        set1.update(self.sudoku[i][startX].candidate)
                        set2.update(self.sudoku[i][startX+1].candidate)
                        set3.update(self.sudoku[i][startX+2].candidate)
                    for num in set1:
                        if num not in set2 and num not in set3:
                            modify |= self.delColCdt(startX, num, protected_area = area)
                    for num in set2:
                        if num not in set1 and num not in set3:
                            modify |= self.delColCdt(startX+1, num, protected_area = area)
                    for num in set3:
                        if num not in set1 and num not in set2:
                            modify |= self.delColCdt(startX+2, num, protected_area = area)

    def solve(self, verbose=1):
        sudoku2 = deepcopy(self)

        stack = []
        while not sudoku2.done():     
            sudoku2.trivial_operation()
                
            if not sudoku2.done():
                if sudoku2.illegal():
                    if not stack:
                        print('The sudoku exercise is illegal!')
                        break
                    else:
                        print('Choose option B')
                        sudoku2 = stack.pop()
                else:
                    sudoku_a = deepcopy(sudoku2)
                    sudoku_b = deepcopy(sudoku2)
                    find = False
                    for i in range(1, 10):
                        for j in range(1, 10):
                            if len(sudoku2[i][j].candidate) == 2:
                                num_a = sudoku2[i][j].candidate[0]
                                num_b = sudoku2[i][j].candidate[1]
                                sudoku_a.updateCell(i, j, sudoku_a[i][j].area, num_a)
                                sudoku_b.updateCell(i, j, sudoku_b[i][j].area, num_b)
                                print('Choose option A', i, j, num_a)
                                find = True
                                break
                        if find:
                            break
                    sudoku2 = sudoku_a
                    stack.append(sudoku_b)

        print(sudoku2)
        return sudoku2