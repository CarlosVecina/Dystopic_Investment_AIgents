import pandas as pd


def expand_df_dates(
    df: pd.DataFrame,
    date_column: str,
    start_date: str | pd.Timestamp,
    end_date: str | pd.Timestamp,
    inclusive: str,
) -> pd.DataFrame:
    date_range = pd.date_range(
        start=start_date, end=end_date, inclusive=inclusive, tz=df[date_column].dt.tz
    )
    df_date = pd.DataFrame(date_range, columns=[date_column])

    return pd.merge(df_date, df, on=date_column, how="left")


def generate_portfolio_evolution(
    df: pd.DataFrame,
    start_date: str | pd.Timestamp,
    end_date: str | pd.Timestamp,
    inclusive: str,
    date_column: str = "created_at",
):
    df_portfolio_expanded = expand_df_dates(
        df, date_column, start_date, end_date, inclusive
    )

    analized_date = None
    past_portfolio = pd.DataFrame()
    final_portfolio = pd.DataFrame()
    for row in df_portfolio_expanded.itertuples():
        if getattr(row, date_column) != analized_date:
            df_filtered = df_portfolio_expanded[
                df_portfolio_expanded[date_column] == getattr(row, date_column)
            ]
            analized_date = getattr(row, date_column)

            if df_filtered.shape[0] > 1:
                past_portfolio = df_filtered
                final_portfolio = pd.concat([final_portfolio, df_filtered])
            else:
                past_portfolio[date_column] = getattr(row, date_column)
                final_portfolio = pd.concat([final_portfolio, past_portfolio])
    return final_portfolio
