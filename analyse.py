import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def fetch_product_prices():
    """Извлекает данные о ценах продуктов из базы данных"""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, price, datetime 
        FROM products
        ORDER BY name, datetime
    """)

    data = cursor.fetchall()
    conn.close()

    products = {}
    for name, price, dtime in data:
        if name not in products:
            products[name] = {'prices': [], 'datetime': []}
        products[name]['prices'].append(price)
        products[name]['datetime'].append(datetime.strptime(dtime, '%Y-%m-%d %H:%M:%S.%f'))

    return products


def plot_price_history(products):
    """Строит график цен по времени для каждого продукта"""
    plt.figure(figsize=(12, 6))

    for product, data in products.items():
        plt.plot(data['datetime'], data['prices'], label=product, marker='o')

    plt.title('История изменения цен продуктов')
    plt.xlabel('Время')
    plt.ylabel('Цена')
    plt.grid(True)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()

    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    try:
        products_data = fetch_product_prices()
        if products_data:
            plot_price_history(products_data)
        else:
            print("В базе данных нет данных о ценах продуктов.")
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
