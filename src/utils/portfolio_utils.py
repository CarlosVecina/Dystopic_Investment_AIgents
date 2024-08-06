import pandas as pd


def expand_df_dates(df, date_column, start_date, end_date, inclusive):
    date_range = pd.date_range(start=start_date, end=end_date, inclusive=inclusive)
    df_date= pd.DataFrame(date_range, columns=[date_column])

    return pd.merge(
        df_date,
        df,
        on=date_column,
        how="left"
    )


def generate_portfolio_evolution(df, start_date, end_date, inclusive):
    df_portfolio_expanded = expand_df_dates(df, "date", start_date, end_date, inclusive)

    analized_date = None
    past_portfolio =  pd.DataFrame()
    final_portfolio = pd.DataFrame()
    for row in df_portfolio_expanded.itertuples():
        if row.date != analized_date:
            df_filtered = df_portfolio_expanded[df_portfolio_expanded.date == row.date]
            analized_date = row.date

            if df_filtered.shape[0] > 1:
                past_portfolio = df_filtered
                final_portfolio = pd.concat(
                    [final_portfolio,
                    df_filtered]
                )
            else:
                past_portfolio["date"] = row.date
                final_portfolio = pd.concat(
                    [final_portfolio,
                    past_portfolio]
                )
    return final_portfolio
