import pandas as pd

def timedelta_to_hms_micro(td):
    if pd.isna(td):
        return None

    total_microseconds = int(td.total_seconds() * 1_000_000)
    hours, remainder = divmod(total_microseconds, 3_600_000_000)
    minutes, remainder = divmod(remainder, 60_000_000)
    seconds, microseconds = divmod(remainder, 1_000_000)

    return f"{hours:02}:{minutes:02}:{seconds:02}.{microseconds:06d}"


def convert_all_timedelta_columns(df):
    for col in df.select_dtypes(include=["timedelta64[ns]"]).columns:
        df[col] = df[col].apply(timedelta_to_hms_micro)
    return df
