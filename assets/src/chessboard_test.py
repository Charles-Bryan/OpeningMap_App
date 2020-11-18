import chess
import chess.svg

# from PyQt5.QtSvg import QSvgWidget
# from PyQt5.QtWidgets import QApplication, QWidget
#
#
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.setGeometry(100, 100, 1100, 1100)
#
#         self.widgetSvg = QSvgWidget(parent=self)
#         self.widgetSvg.setGeometry(10, 10, 1080, 1080)
#
#         self.chessboard = chess.Board()
#
#         self.chessboardSvg = chess.svg.board(self.chessboard).encode("UTF-8")
#         self.widgetSvg.load(self.chessboardSvg)
#
#     def paintEvent(self, event):
#         self.chessboardSvg = chess.svg.board(self.chessboard).encode("UTF-8")
#         self.widgetSvg.load(self.chessboardSvg)
#
# if __name__ == "__main__":
#     app = QApplication([])
#     window = MainWindow()
#     print(0)
#     window.show()
#     app.exec()


board = chess.Board("8/8/8/8/4N3/8/8/8 w - - 0 1")
squares = board.attacks(chess.E4)
image = chess.svg.board(board=board, squares=squares)

print(0)