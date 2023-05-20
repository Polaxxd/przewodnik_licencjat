import mysql.connector

mydb = mysql.connector.connect(
	host="limba.wzks.uj.edu.pl",
	user="20_palonek",
	passwd = "polap1103",
	)

my_cursor = mydb.cursor()

#my_cursor.execute("CREATE DATABASE przewodnik")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
	print(db)
