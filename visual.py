import datetime

import PyQt6.QtWidgets as QtWidgets
from matplotlib.dates import num2date, date2num
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import pandas as pd
from scipy.optimize import curve_fit

from common import get_common_dataframe, remove_transactions_between_accounts


class TextWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.textedit = QtWidgets.QTextBrowser(self)
        layout.addWidget(self.textedit)
        self.resize(800, 600)
        self.setLayout(layout)


class InteractiveCumulation:
    def __init__(self, df: pd.DataFrame) -> None:
        tog = df["amount"]

        # tog_2 = tog
        df_unique = remove_transactions_between_accounts(df)  # type: ignore

        self.infos: pd.Series = df_unique.loc[:, "info"]

        amounts_unique = df_unique["amount"]

        fig, ax = plt.subplots(1, 1)
        ax.step(
            amounts_unique.index,
            amounts_unique.sort_index().cumsum(),
            where="post",
            picker=True,
        )

        tog = tog.sort_index()
        x = tog.index
        y = tog.cumsum()
        ax.step(x, y, where="post", color="#22222222")

        self.textwindow = None
        self.span_selector = SpanSelector(
            ax,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True,
        )

        def linear(x, a, b):
            return a * x + b

        csum = amounts_unique.cumsum()

        # datetime.datetime
        # datetime.date
        # pd.Index.map
        xdata = csum.index.map(date2num)
        params, _ = curve_fit(linear, xdata, csum.values.flatten())

        ax.plot(xdata, linear(xdata, *params), "r")
        ax.set_xlim(xdata.min(), xdata.max())

        per_month = (linear(365, *params) - linear(0, *params)) / 12
        # matplotlib.figure.Figure
        fig.text(0, 0, f"Ušetrené približne {per_month:.0f} za mesiac.", snap=True)

        plt.show()

    def onselect(self, xmin, xmax):
        if self.textwindow is None:
            self.textwindow = TextWindow()
        self.textwindow.show()
        xmin = pd.Timestamp(num2date(xmin).date())
        xmax = pd.Timestamp(num2date(xmax).date())
        infoseries = pd.Series(
            self.infos[(self.infos.index > xmin) & (self.infos.index < xmax)]
        )
        infoseries.index = infoseries.index.map(lambda x: x.date())
        text = ""
        i: datetime.datetime
        text += '<table style="border: 1px solid black">\n'
        for i in infoseries.index.unique():  # type: ignore
            text += (
                f'<tr>\n<td colspan=6 style="padding: 6px"><h2>{i}</h2></td>\n</tr>\n'
            )
            if not isinstance(infoseries[i], pd.Series):
                text += "<tr>\n"
                for data in str(infoseries[i]).split("\n"):
                    text += f'<td style="padding: 6px">{data}</td>\n'
                text += "</tr>\n"
            else:
                unique_values = {}
                for entry in infoseries[i]:
                    amount = float(entry.split("\n")[0])
                    if amount * (-1) in unique_values:
                        unique_values.pop(amount * (-1))
                        continue
                    unique_values[amount] = entry
                for entry in unique_values.values():
                    text += "<tr>\n"
                    for data in entry.split("\n"):
                        text += f'<td style="padding: 6px">{data}</td>\n'
                    text += "</tr>\n"
        text += "</table>\n"
        # text = infoseries.map(lambda x: x.replace('\n', '<p/>'))
        self.textwindow.textedit.setHtml(text)


if __name__ == "__main__":
    df = get_common_dataframe()
    df = df[df.index > datetime.datetime(2024, 3, 1, 0, 0, 0)]
    # df = df[df.index > datetime.datetime(2024, 1, 1, 0, 0, 0)]
    # df = df[df.index < datetime.datetime(2026, 1, 1, 0, 0, 0)]
    # df = df[df.index > datetime.datetime(2024, 1, 1, 0, 0, 0)]
    # df = df[df.index < datetime.datetime(2025, 1, 1, 0, 0, 0)]
    # df = df[df.index > datetime.datetime(2023, 1, 1, 0, 0, 0)]
    # df = df[df.index < datetime.datetime(2024, 1, 1, 0, 0, 0)]
    # df = df[df.index > datetime.datetime(2022, 1, 1, 0, 0, 0)]
    # df = df[df.index < datetime.datetime(2023, 1, 1, 0, 0, 0)]
    # df = df[df.index > datetime.datetime(2021, 1, 1, 0, 0, 0)]
    # df = df[df.index < datetime.datetime(2022, 1, 1, 0, 0, 0)]
    InteractiveCumulation(df)  # type:ignore
