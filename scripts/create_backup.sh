#!/bin/bash

# Директория для бэкапов
BACKUP_DIR="../backups"
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
fi

# Генерация имени для резервной копии с датой
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/mysql-dump_$DATE.sql"

# Выполнение дампа базы данных
docker exec -i prestashop-project-mariadb-1 mysqldump -u root -padmin --no-tablespaces prestashop > "$BACKUP_FILE" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Backup успешно создан: $BACKUP_FILE"
else
    echo "Ошибка при создании backup"
fi
