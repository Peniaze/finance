import datetime
import pathlib

import PyQt6.QtWidgets as QtWidgets
from matplotlib.dates import num2date, date2num
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit


def get_common_dataframe(folder="data/"):
    dfs = []
    for file in pathlib.Path(folder).glob("*.csv"):
        if file.name.startswith("Pohyby"):
            # Reiffeisen csv file
            df = pd.read_csv(file, encoding="latin2", sep=";")
            df["Zaúčtovaná částka"] = (
                df["Zaúčtovaná částka"]
                .map(lambda x: x.replace(" ", "").replace(",", "."))
                .astype(float)
            )
            df["Datum zaúčtování"] = df["Datum zaúčtování"].map(
                lambda x: datetime.datetime.strptime(x, "%d.%m.%Y %H:%M")
            )
            df["info"] = (
                df[
                    [
                        "Město",
                        "Název obchodníka",
                        "Název protiúčtu",
                        "Zpráva",
                        "Poznámka",
                    ]
                ]
                .fillna("nan")
                .apply(lambda x: "\n".join(x), axis=1)
            )
            df["info"] = df[["Zaúčtovaná částka", "info"]].apply(
                lambda x: "\n".join(str(i) for i in x), axis=1
            )
            df["date"] = df["Datum zaúčtování"]
            df["amount"] = df["Zaúčtovaná částka"]
            dfs.append(df)
        else:
            # George csv file
            df = pd.read_csv(file, encoding="utf-16")
            df["Amount"] = df["Amount"].map(lambda x: x.replace(",", "")).astype(float)
            df["Processing Date"] = df["Processing Date"].map(
                lambda x: datetime.datetime.strptime(x, "%d.%m.%Y")
            )
            df["info"] = (
                df[["Partner Name", "Category", "Message for recipient"]]
                .fillna("nan")
                .apply(lambda x: "\n".join(x), axis=1)
            )
            df["info"] = df[["Amount", "info"]].apply(
                lambda x: "\n".join(str(i) for i in x), axis=1
            )
            df["date"] = df["Processing Date"]
            df["amount"] = df["Amount"]
            dfs.append(df)
    return pd.concat(dfs, axis=0).set_index("date").sort_index()


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
        self.infos: pd.Series = df.loc[:, "info"]
        tog = df["amount"]

        # tog = pd.concat(amounts, axis=0)
        # tog.index[0].date()
        date_o = None
        dates = []
        values = []
        i: datetime.datetime
        for i in tog.index.sort_values().unique():  # type: ignore
            date = i.date()
            value = tog[i].sum()
            if date != date_o:
                dates.append(date)
                date_o = date
                values.append(value)
            else:
                values[-1] += value

        tog_2 = pd.Series(data=values, index=dates)
        ax = plt.subplot()
        ax.plot(tog_2.index, tog_2.sort_index().cumsum(), picker=True)

        tog.sort_index().cumsum().plot(style="-", color="#22222222")

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

        csum = tog_2.cumsum()

        # datetime.datetime
        # datetime.date
        # pd.Index.map
        xdata = csum.index.map(date2num)
        params, _ = curve_fit(linear, xdata, csum.values)

        ax.plot(xdata, linear(xdata, *params), 'r')
        ax.set_xlim(xdata.min(), xdata.max())

        per_month = (linear(365, *params) - linear(0, *params)) / 12
        ax.set_title(per_month)

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
        text = ""
        i: datetime.datetime
        text += '<table style="border: 1px solid black">\n'
        for i in infoseries.index.unique():  # type: ignore
            text += f'<tr>\n<td colspan=6 style="padding: 6px"><h2>{i.date()}</h2></td>\n</tr>\n'
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
    df = df[df.index > datetime.datetime(2024, 6, 1, 0, 0, 0)]
    InteractiveCumulation(df)
    breakpoint()
