from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QGridLayout,
    QVBoxLayout,
    QTextBrowser,
    QLabel,
)

from common import get_common_dataframe, remove_transactions_between_accounts


class LabelerWindow(QWidget):

    def __init__(self) -> None:
        super().__init__()

        layout = QGridLayout()
        layout_left_panel = QVBoxLayout()

        self.textbox = QTextBrowser(self)

        layout_left_panel.addWidget(self.textbox)

        layout_right_panel = QVBoxLayout()
        layout_right_panel.addWidget(QLabel('Enter category:'))

        self.lineedit = QLineEdit(self)
        self.lineedit.returnPressed.connect(self.enter_category)
        layout_right_panel.addWidget(self.lineedit)

        layout.addLayout(layout_left_panel, 0, 0)
        layout.addLayout(layout_right_panel, 0, 1)

        self.setLayout(layout)

        df = get_common_dataframe()
        self.df = remove_transactions_between_accounts(df)

        self.index = 0


    def enter_category(self):
        row = self.next_row()
        if row is None:
            self.textbox.setText('All done.')
            return
        self.textbox.setText(row.to_string())

    def next_row(self):
        try:
            row = self.df.iloc[self.index]
        except IndexError:
            row = None
        self.index += 1
        return row


def main():

    qapp = QApplication([])

    main_window = LabelerWindow()
    main_window.show()

    qapp.exec()




if __name__ == "__main__":
    main()
