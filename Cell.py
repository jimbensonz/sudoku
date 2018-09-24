class Cell():
    def __init__(self, value='0'):
        self.value = value
        self.candidate = ['1','2','3','4','5','6','7','8','9']

        self.x = 0
        self.y = 0
        self.area = 0

    def __repr__(self):
        return self.value

    def __str__(self):
        return  str(self.value) + ': (' + str(self.y) + ', ' + str(self.x) + ')'

    def create(self, v, i, j):
        self.value = str(v)
        self.x = i
        self.y = j
        if i >= 1 and i <= 3:
            if j >= 1 and j <= 3:
                self.area = 1
            elif j >= 4 and j <= 6:
                self.area = 2
            elif j >= 7 and j <= 9:
                self.area = 3
        elif i >= 4 and i <= 6:
            if j >= 1 and j <= 3:
                self.area = 4
            elif j >= 4 and j <= 6:
                self.area = 5
            elif j >= 7 and j <= 9:
                self.area = 6
        elif i >= 7 and i <= 9:
            if j >= 1 and j <= 3:
                self.area = 7
            elif j >= 4 and j <= 6:
                self.area = 8
            elif j >= 7 and j <= 9:
                self.area = 9
                
    def clear(self):
        self.candidate = []
        
    def illegal(self):
        return self.value == '0' and not self.candidate

    def delCdt(self, _id):
        strID = str(_id)
        if strID in self.candidate:
            self.candidate.remove(strID)
            return True
        else:
            return False