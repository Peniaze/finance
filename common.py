from itertools import combinations
import datetime
import pathlib

import pandas as pd

KURZ = 25


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
            df["account"] = "Reiffeisen"
            df["info"] = df[["Zaúčtovaná částka", "account", "info"]].apply(
                lambda x: "\n".join(str(i) for i in x), axis=1
            )
            df["date"] = df["Datum zaúčtování"]
            df["amount"] = df["Zaúčtovaná částka"]
            dfs.append(df)
        elif file.name.startswith("account-statement"):
            # Revolut
            df = pd.read_csv(file)
            df["amount"] = df["Amount"].astype(float)
            df.loc[df["Currency"] == "EUR", "amount"] *= KURZ
            df["date"] = df["Started Date"].map(
                lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
            )
            df["account"] = "Revolut"
            df["info"] = df[
                ["Amount", "Currency", "account", "Type", "Description"]
            ].apply(lambda x: "\n".join(str(i) for i in x), axis=1)
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
            df["account"] = "George"
            df["info"] = df[["Amount", "account", "info"]].apply(
                lambda x: "\n".join(str(i) for i in x), axis=1
            )
            df["date"] = df["Processing Date"]
            df["amount"] = df["Amount"]
            dfs.append(df)
    return pd.concat(dfs, axis=0).set_index("date").sort_index()


def remove_transactions_between_accounts(amounts: pd.Series):

    amounts_with_dates = amounts.copy().reset_index()
    amounts_with_dates["date"] = amounts.index.map(lambda x: x.date())

    dates = amounts_with_dates["date"]

    indexes_to_drop = []
    for unique_date in dates.unique():
        transactions_at_date = amounts_with_dates.loc[dates == unique_date, "amount"]
        for a, b in combinations(transactions_at_date, r=2):
            if a == -b:
                indexes = transactions_at_date[
                    (transactions_at_date == a) | (transactions_at_date == b)
                ].index
                if transactions_at_date[indexes].sum() != 0:
                    ...
                print(transactions_at_date[indexes])
                indexes_to_drop.extend(indexes)

    result = amounts.reset_index().drop(indexes_to_drop).set_index('date', drop=True)
    return result
    date_o = None
    dates = []
    values = []
    for i in amounts.index.sort_values().unique():
        assert hasattr(i, "date"), "Wrong type of index in dataframe"
        date = i.date()
        value = amounts[i].sum()
        if date != date_o:
            dates.append(date)
            date_o = date
            values.append(value)
        else:
            values[-1] += value

    return pd.Series(data=values, index=dates)
