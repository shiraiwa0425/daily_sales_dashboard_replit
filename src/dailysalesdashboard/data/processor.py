import pandas as pd

def standardize_data(df):
    """CSVデータを標準化して一貫性を確保する"""
    # 必須カラムの確認と追加
    required_columns = ["日付", "時間帯", "支払方法", "売上金額", "備考"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    
    # 時間帯の標準化（昼営業/夜営業以外の値を修正）
    valid_times = ['昼営業', '夜営業']
    df.loc[~df['時間帯'].isin(valid_times), '時間帯'] = '昼営業'  # デフォルト値
    
    # 支払方法の標準化
    # 昼営業のデータは'lunch'、夜営業のデータは'dinner'をデフォルト値とする
    df.loc[(df['支払方法'].isnull() | df['支払方法'] == '') & 
           (df['時間帯'] == '昼営業'), '支払方法'] = 'lunch'
    df.loc[(df['支払方法'].isnull() | df['支払方法'] == '') & 
           (df['時間帯'] == '夜営業'), '支払方法'] = 'dinner'
    
    return df

def validate_sales_data(df):
    """売上データの検証を行う関数"""
    # 必須カラムが存在するかチェック
    required_columns = ["日付", "時間帯", "支払方法", "売上金額"]
    if not all(col in df.columns for col in required_columns):
        return False
    
    # 日付形式のチェック
    try:
        pd.to_datetime(df['日付'])
    except:
        return False
    
    # 売上金額が数値であることを確認
    try:
        df['売上金額'] = pd.to_numeric(df['売上金額'])
    except:
        return False
    
    return True

def aggregate_sales_by_date(df):
    """日付ごとの売上を集計"""
    df['日付'] = pd.to_datetime(df['日付'])
    return df.groupby('日付')['売上金額'].sum().reset_index()

def aggregate_sales_by_time(df):
    """時間帯ごとの売上を集計"""
    return df.groupby('時間帯')['売上金額'].sum().reset_index()

def aggregate_sales_by_payment(df):
    """支払方法ごとの売上を集計"""
    return df.groupby('支払方法')['売上金額'].sum().reset_index()

def calculate_sales_statistics(df):
    """売上統計を計算"""
    stats = {}
    
    # 総売上
    stats['total_sales'] = df['売上金額'].sum()
    
    # 平均売上
    stats['avg_daily_sales'] = df.groupby('日付')['売上金額'].sum().mean()
    
    # 時間帯別売上
    time_sales = df.groupby('時間帯')['売上金額'].sum()
    stats['lunch_sales'] = time_sales.get('昼営業', 0)
    stats['dinner_sales'] = time_sales.get('夜営業', 0)
    
    return stats