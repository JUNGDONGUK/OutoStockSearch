docker run --rm -d -p 3306:3306 --name apro-mysql -e MYSQL_ROOT_PASSWORD=1234 -v C:\Project\data:/var/lib/mysql mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
