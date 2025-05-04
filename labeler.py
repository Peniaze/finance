from os import wait
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QGridLayout,
    QVBoxLayout,
    QTextBrowser,
    QLabel,
)
import rapidfuzz

from common import get_common_dataframe, remove_transactions_between_accounts

CATEGORIES = {
    "Entertainment": [
        "Games",
        "Music",
        "Other",
        "Sports",
    ],
    "Food and drink": [
        "Dining out",
        "Groceries",
        "Liquor",
        "Other",
    ],
    "Home": [
        "Electronics",
        "Furniture",
        "Household items",
        "Maintenance",
        "Mortgage",
        "Other",
        "Pets",
        "Rent",
        "Services",
    ],
    "Life": [
        "Childcare",
        "Clothing",
        "Education",
        "Gifts",
        "Insurance",
        "Medical expenses",
        "Other",
        "Taxes",
    ],
    "Transportation": [
        "Bicycle",
        "Bus/train",
        "Car",
        "Gas/fuel",
        "Hotel",
        "Other",
        "Parking",
        "Plane",
        "Taxi",
    ],
    "Uncategorized": [
        "General",
    ],
    "Utilities": [
        "Cleaning",
        "Electricity",
        "Heat/gas",
        "Other",
        "Trash",
        "Tv/phone/internet",
        "Water",
    ],
}


class LabelerWindow(QWidget):

    def __init__(self) -> None:
        super().__init__()

        layout = QGridLayout()
        layout_left_panel = QVBoxLayout()

        self.textbox = QTextBrowser(self)

        layout_left_panel.addWidget(self.textbox)

        layout_right_panel = QVBoxLayout()

        self.category_view = QTextBrowser(self)
        layout_right_panel.addWidget(self.category_view)

        layout_right_panel.addWidget(QLabel("Enter category:"))

        self.lineedit = QLineEdit(self)
        self.lineedit.textChanged.connect(self.view_categories)
        self.lineedit.returnPressed.connect(self.enter_category)
        layout_right_panel.addWidget(self.lineedit)

        layout.addLayout(layout_left_panel, 0, 0)
        layout.addLayout(layout_right_panel, 0, 1)

        self.setLayout(layout)

        df = get_common_dataframe()
        self.df = remove_transactions_between_accounts(df)

        self.view_categories()

        self.index = 0
        self.enter_category()

    def view_categories(self):
        lineedit_text = self.lineedit.text()

        if lineedit_text == "":
            t = []
            for topic, subcategories in CATEGORIES.items():
                t.append(f"{topic}:")
                t.append("<ul>")
                for category in subcategories:
                    t.append(f"<li>{category}</li>")
                t.append("</ul>")
            self.category_view.setText("".join(t))
            return

        categories = []
        for topic, subcategories in CATEGORIES.items():
            subs = [":".join((topic, i)) for i in subcategories]
            categories.extend(subs)
        sorted_categories = rapidfuzz.process.extract(
            lineedit_text, categories, limit=None
        )
        t = "<ul>"
        for index, (c, _, _) in enumerate(sorted_categories):
            if index == 0:
                t += f'<li style="background-color: yellow"> {c} </li>\n'
                continue
            t += f"<li> {c} </li>\n"
        t += "</ul>"
        self.category_view.setText(t)

    def enter_category(self):
        row = self.next_row()
        if row is None:
            self.textbox.setText("All done.")
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
    main_window.resize(640, 480)
    main_window.show()

    qapp.exec()


if __name__ == "__main__":
    main()
