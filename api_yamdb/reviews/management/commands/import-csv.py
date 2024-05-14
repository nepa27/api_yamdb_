import csv
import sqlite3

from django.core.management.base import BaseCommand

from api_yamdb.api_yamdb.settings import BASE_DIR

print(BASE_DIR)

base = 'api_yamdb/static/data/'
files = ('category.csv', 'genre.csv', 'titles.csv',
         'genre_title.csv', 'review.csv', 'comments.csv')
tables = ('reviews_category', 'reviews_genre', 'reviews_title',
          'reviews_title_genre', 'reviews_review', 'reviews_comment')


def import_csv_to_sqlite(csv_file, table_name):
    conn = sqlite3.connect('api_yamdb/db.sqlite3')
    cursor = conn.cursor()
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        columns = ', '.join(header)
        for row in csv_reader:
            size = ', '.join(['?'] * len(row))
            cursor.execute(
                f"INSERT INTO {table_name} ({columns}) VALUES ({size})", row
            )
    conn.commit()
    conn.close()


class Command(BaseCommand):
    def handle(self, *args, **kwargs) -> None:
        for file, table in zip(files, tables):
            try:
                print('start download', file)
                import_csv_to_sqlite(base + file, table)
                print('finish download', file)
            except Exception as e:
                print(e)
