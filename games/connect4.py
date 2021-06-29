

class ConnectFour:
    player1Emoji ='🔵'
    player2Emoji ='🔴'
    baseEmoji = '⬜'
    gameover = False
    currentGrid =[[]]
    currentPlayer = None
    emoji_dict = {'1⃣':0, '2⃣':1, '3⃣':2, '4⃣':3, '5⃣':4, '6⃣':5, '7⃣':6, '8⃣':7}
    def __init__(self,ctx,player1,player2):
        self.ctx = ctx
        self.player1 = player1
        self.player2 = player2
        self.currentPlayer = player1

    def generate_base_grid(self):
        baseEmoji = '⬜'
        grid = [
            [baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji],
            [baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji],
            [baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji],
            [baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji],
            [baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji],
            [baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji],
            [baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji],
            [baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji, baseEmoji]
                ]
        return grid

    def display_current_grid(self):
        if(self.currentGrid==[[]]):
            self.currentGrid = self.generate_base_grid()
        displayString =""
        for i in self.currentGrid:
            for j in i:
                displayString +=  j+ " "
            displayString += "\n"
        return displayString
    #
    def make_move(self,column):

        column = self.emoji_dict[column]
        for i in range(8):
            if self.currentGrid[7-i][column] == self.baseEmoji:
                if(self.currentPlayer == self.player1):
                    self.currentGrid[7 - i][column] = str(self.player1Emoji.emoji)
                    self.currentPlayer = self.player2
                    if self.isConnected(7-i,column):
                        self.gameover = True
                        return

                    break
                else:
                    self.currentGrid[7 - i][column] = str(self.player2Emoji.emoji)
                    self.currentPlayer = self.player1
                    break
        return

    def isConnected(self, row, col):
        if self.horizontal(row,col): return True
        if self.vertical(row, col): return True
        if self.diag1(row,col): return True
        if self.diag2(row,col): return True
        return False

    def horizontal(self, row, col):
        for i in range(8):
            for j in range(8):
                try:
                    if self.currentGrid[i][j] == self.currentGrid[row][col] and self.currentGrid[i][j + 1] == self.currentGrid[row][col] and self.currentGrid[i][j + 2] == self.currentGrid[row][col] and self.currentGrid[i][j + 3] == self.currentGrid[row][col]:
                        return True
                except IndexError:
                    next
        return False

    def vertical(self, row, col):
        for i in range(8):
            for j in range(8):
                try:
                    if self.currentGrid[i][j] == self.currentGrid[row][col] and self.currentGrid[i+1][j] == self.currentGrid[row][col] and self.currentGrid[i+2][j] == self.currentGrid[row][col] and self.currentGrid[i+3][j] == self.currentGrid[row][col]:
                        return True
                except IndexError:
                    next
        return False


    def diag1(self, row, col):
        for i in range(8):
            for j in range(8):
                try:
                    if self.currentGrid[i][j] == self.currentGrid[row][col] and self.currentGrid[i+1][j+1] == self.currentGrid[row][col] and self.currentGrid[i+2][j+2] == self.currentGrid[row][col] and self.currentGrid[i+3][j+3] == self.currentGrid[row][col]:
                        return True
                except IndexError:
                    next
        return False

    def diag2(self, row, col):
        for i in range(8):
            for j in range(8):
                try:
                    if self.currentGrid[i][j] == self.currentGrid[row][col] and self.currentGrid[i+1][j-1] == self.currentGrid[row][col] and self.currentGrid[i+2][j-2] == self.currentGrid[row][col] and self.currentGrid[i+3][j-3] == self.currentGrid[row][col]:
                        return True
                except IndexError:
                    next
        return False



  #O(N) - Win condition optimised, not tested - 16 operations max

    # def horizontal(self, row, col):
    #     left, right, counter, reset = True, True, 1, [row, col]
    #     while left:
    #         if col - 1 >= 0 and self.currentGrid[row][col] == self.currentGrid[row][col - 1]:
    #             counter = counter + 1
    #             col = col - 1
    #             if counter == 4: return True
    #         else:
    #             break
    #
    #     row, col = reset[0], reset[1]
    #
    #     while right:
    #         if col + 1 <= len(self.currentGrid[0]) - 1 and self.currentGrid[row][col] == self.currentGrid[row][col + 1]:
    #             counter = counter + 1
    #             col = col + 1
    #             if counter == 4: return True
    #         else:
    #             break
    #
    #     return False
    #
    # def vertical(self, row, col):
    #     up, down, counter, reset = True, True, 1, [row, col]
    #     while down:
    #         if row - 1 >= 0 and self.currentGrid[row][col] == self.currentGrid[row-1][col]:
    #             counter = counter + 1
    #             row = row - 1
    #             if counter == 4: return True
    #         else:
    #             break
    #
    #     return False
    #
    # def diag1(self, row, col):
    #     up, down, counter, reset = True, True, 1, [row, col]
    #     while up:
    #         if row - 1 >= 0 and col - 1 >= 0 and self.currentGrid[row][col] == self.currentGrid[row-1][col-1]:
    #             counter = counter + 1
    #             row, col = row - 1, col - 1
    #             if counter == 4: return True
    #         else:
    #             break
    #
    #     row, col = reset[0], reset[1]
    #
    #     while down:
    #         if row + 1 <= len(self.currentGrid) - 1  and col + 1 <= len(self.currentGrid[0]) - 1 and self.currentGrid[row][col] == self.currentGrid[row+1][col+1]:
    #             counter = counter + 1
    #             row, col = row + 1 , col + 1
    #             if counter == 4: return True
    #         else:
    #             break
    #     return False
    #
    # def diag2(self, row, col):
    #     up, down, counter, reset = True, True, 1, [row, col]
    #     while up:
    #         if row - 1 >= 0 and col + 1 <= len(self.currentGrid[0]) - 1 and self.currentGrid[row][col] == self.currentGrid[row - 1][col + 1]:
    #             counter = counter + 1
    #             row, col = row -1 , col + 1
    #             if counter == 4: return True
    #         else:
    #             break
    #
    #     row, col = reset[0], reset[1]
    #
    #     while down:
    #         if row + 1 <= len(self.currentGrid) - 1 and col - 1 >= 0 and self.currentGrid[row][col] == self.currentGrid[row + 1][col - 1]:
    #             counter = counter + 1
    #             row, col =  row + 1, col - 1
    #             if counter == 4: return True
    #         else:
    #             break
    #
    #     return False