#!/bin/bash

# Проверяем, передан ли файл в качестве аргумента
if [ $# -eq 0 ]; then
    echo "Не указан файл с дампом. Использование: ./load_backup.sh <path_to_sql_file>"
    exit 1
fi

DUMP_FILE=$1

# Проверяем существование файла
if [ ! -f "$DUMP_FILE" ]; then
    echo "Файл '$DUMP_FILE' не найден!"
    exit 1
fi

# Загрузка дампа в базу данных
docker exec -i prestashop-project-mariadb-1 mysql -u root -padmin prestashop < "$DUMP_FILE"

if [ $? -eq 0 ]; then
    echo "Дамп успешно загружен: $DUMP_FILE"
else
    echo "Ошибка при загрузке дампа"
fi
