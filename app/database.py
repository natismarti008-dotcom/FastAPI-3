import os
from contextlib import contextmanager

import pymysql
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()


# Función que crea y administra la conexión a MySQL
@contextmanager
def conectar():

    # Establece la conexión con la base de datos
    conexion = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.getenv("DB_NAME", "tienda"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=10,
    )

    try:
        # Entrega la conexión para que pueda ser utilizada
        yield conexion

        # Guarda los cambios realizados en la base de datos
        conexion.commit()

    except Exception:

        # Si ocurre un error, deshace los cambios realizados
        conexion.rollback()

        # Vuelve a lanzar el error
        raise

    finally:

        # Cierra la conexión al finalizar el proceso
        conexion.close()