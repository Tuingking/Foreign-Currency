-- CREATE USER 'root'@'%' IDENTIFIED BY 'password';
-- GRANT ALL PRIVILEGES ON \*.\* TO 'root'@'%' WITH GRANT OPTION;

UPDATE mysql.user SET host="%" WHERE user="root";