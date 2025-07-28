import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres(host, port=5432, user="couple_user", password="couple_password", database="couple_diary_db", max_retries=30):
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            conn.close()
            print("PostgreSQL is ready!")
            return True
        except OperationalError:
            retries += 1
            print(f"PostgreSQL is not ready yet... ({retries}/{max_retries})")
            time.sleep(1)
    
    print("Failed to connect to PostgreSQL")
    return False

if __name__ == "__main__":
    wait_for_postgres("postgres")