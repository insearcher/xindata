"""
Скрипт для исправления анализа по методам оплаты
"""

import pandas as pd
import numpy as np

def main():
    # Загрузка данных
    df = pd.read_csv('/Users/frolov/Downloads/freelancer_earnings_bd.csv')
    
    # Анализ дохода по методам оплаты
    crypto_earnings = df[df['Payment_Method'] == 'Crypto']['Earnings_USD'].mean()
    other_earnings = df[df['Payment_Method'] != 'Crypto']['Earnings_USD'].mean()
    difference = crypto_earnings - other_earnings
    percentage = (difference / other_earnings) * 100
    
    print('\nАнализ дохода по методам оплаты:')
    print(f'Средний доход фрилансеров, принимающих оплату в криптовалюте: ${crypto_earnings:.2f}')
    print(f'Средний доход фрилансеров, использующих другие способы оплаты: ${other_earnings:.2f}')
    print(f'Разница: ${difference:.2f} ({percentage:.2f}%)')
    
    # Подробный анализ по всем методам оплаты
    print('\nСредний доход по всем методам оплаты:')
    payment_earnings = df.groupby('Payment_Method')['Earnings_USD'].agg(['mean', 'median', 'count']).reset_index()
    payment_earnings = payment_earnings.sort_values(by='mean', ascending=False)
    
    for _, row in payment_earnings.iterrows():
        print(f"{row['Payment_Method']}: ${row['mean']:.2f} (медиана: ${row['median']:.2f}, кол-во: {row['count']})")

if __name__ == "__main__":
    main()
