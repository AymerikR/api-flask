from flask import Flask, jsonify, url_for, request, abort
#from flask_restx import Api, Resource, fields
import sqlite3

connection = sqlite3.connect("video.db")
cursor = connection.cursor()

id_film=(7,)
intid=(2,)

cursor.execute("SELECT film.age_min FROM film WHERE film.id_film= ?", id_film)
age_min= cursor.fetchone()
print(age_min)

cursor.execute('SELECT client.age from client WHERE client.id_client = ?', intid)
age_client=cursor.fetchone()

if age_client>=age_min:
    film_client = (id_film[0],intid[0])
    cursor.execute('INSERT INTO film_client VALUES (?,?)',film_client)
                

connection.commit()