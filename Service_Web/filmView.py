from .app import app, api
from .models import *

from flask import jsonify, url_for, request, abort
from flask_restx import Resource, fields
import sqlite3


"""
Gestion des catégories
"""

@api.route('/categorieFilm')
class CategorieAll(Resource):

    @api.doc(model=get_allcategories)
    def get(self):
        """
        Retourne l'intitulé et la location de toutes les catégories
        """
        locations=[]
        try:  
            connection = sqlite3.connect("video1.db")
        except sqlite3.Error as e:
            raise(e)

        cursor = connection.cursor()

        try:
            query = 'SELECT DISTINCT id_categorie, nom_categorie FROM categorie'
            cursor.execute(query)
            categories = cursor.fetchall()

            for idc in categories:
                intitule = idc[1]
                locations.append({
                    'intitule':intitule,
                    'location':'/categorieFilm/'+str(idc[0])})

        except sqlite3.Error as e:
            raise(e)

        connection.close()
        return(jsonify(locations))

    @api.doc(body=categoriepost,model=categorieget)
    def post(self):
        """
        Création d'une nouvelle catégorie
        """
        categorie = {}
        id = 0

        if request.json :
            try:
                connection = sqlite3.connect('video1.db')
                cursor = connection.cursor()
            except sqlite3.Error as e:
                raise(e)

            try:
                categorie['intitule']=request.json['intitule']
                categorie['description']=request.json['description']

                new_categorie = (request.json['intitule'],request.json['description'])
                query = 'INSERT INTO categorie (nom_categorie, description_categorie) VALUES(?,?)'
                cursor.execute(query,new_categorie)
                id = cursor.lastrowid
                connection.commit()
    
            except Exception as e:
                print("[ERREUR]",e)
                connection.rollback()
            finally:
                connection.close()

            response = jsonify(categorie)
            response.status_code = 201
            response.headers['location'] = '/categorieFilm/'+str(id)
            return response
        
        else:
            abort(415)

@api.route('/categorieFilm/<idcat>')
class CategorieOne(Resource):

    @api.doc(model = categorieget)
    def get(self,idcat):
        """
        Retourne le détail d'une catégorie
        """
        try:
            connection = sqlite3.connect('video1.db')
            cursor = connection.cursor()
        except sqlite3.Error as e:
            raise(e)

        try:
            int_idcat = int(idcat)
            query = 'SELECT id_categorie FROM categorie '
            cursor.execute(query)

            last_id = len(cursor.fetchall())
            if int_idcat > last_id or int_idcat==0:
                connection.close()
                abort(404)
            
            id = (int_idcat,)
            cursor.execute('SELECT * FROM categorie WHERE id_categorie = ?',id)
            res = cursor.fetchone()

            categorie = {
                'id':res[0],
                'intitule':res[1],
                'description':res[2]
            }

        except sqlite3.Error as e:
            abort(500)

        finally:
            connection.close()

            response=jsonify(categorie)
            response.status=200
            return response

    @api.doc(body=categoriepost, model=categorieget)
    def put(self,idcat):
        """
        Modifie les détails d'une catégorie (Titre, Description)
        """

        if request.json:
            int_idcat = int(idcat)

            try:
                connection = sqlite3.connect("video1.db")
                cursor = connection.cursor()
            except sqlite3.Error as e:
                raise(e)


            cursor.execute('SELECT id_categorie FROM categorie')
            categories_id = []
            categorie = {}
            for i in cursor.fetchall():
                categories_id.append(int(i[0]))
            
            if int_idcat not in categories_id:
                abort(404)


            try:
                update_categorie = (request.json['intitule'],request.json['description'],int_idcat)
                cursor.execute('UPDATE categorie SET nom_categorie = ?, description_categorie = ? WHERE id_categorie = ?',update_categorie)
                connection.commit()

                categorie['intitule']=request.json['intitule']
                categorie['description']=request.json['description']

            except(TypeError, ValueError):
                connection.rollback()
                abort(400)
                
            finally:
                connection.close()


            response = jsonify(categorie)
            response.status_code=200
            response.headers['location'] = '/categorieFilm/'+str(int_idcat)
            return response

        else:
            abort(415)

    @api.doc()
    def delete(self,idcat):
        """
        Supprimer une catégorie
        """
        intid = int(idcat)

        try:
            connection = sqlite3.connect("video1.db")
            cursor = connection.cursor()
        except sqlite3.Error as e:
            raise(e)

        cursor.execute('SELECT id_categorie FROM categorie')
        categories_id = []
        for i in cursor.fetchall():
            categories_id.append(int(i[0]))
        
        if intid not in categories_id:
            abort(404)
        
        try:
            categorie_delete = (intid,)
            cursor.execute('DELETE FROM categorie WHERE id_categorie = ?',categorie_delete)
            connection.commit()
        except sqlite3.Error as e:
            print("Erreur lors de la suppression de la catégorie",e)
            connection.rollback()
        finally:
            connection.close()
            return()

"""
Gestion des films dans une catégorie
"""

@api.route('/categorieFilm/<idcat>/film')
class FilmAll(Resource):
    api.doc(model=get_allfilm)
    def get(self,idcat):
        """
        Retourne le titre et la location de tout les films compris dans 
        cette catégorie 
        """
        locations = []
        try:
            connection = sqlite3.connect('video1.db')
            cursor = connection.cursor()
            id = (int(idcat),)
            query = """SELECT film.id_film,film.titre_film, categorie.nom_categorie FROM film
                    JOIN film_categorie
                    ON film.id_film = film_categorie.film_id
                    JOIN categorie
                    ON film_categorie.categorie_id = categorie.id_categorie
                    WHERE categorie.id_categorie = ?
                    """
            
            cursor.execute(query,id)
            films = cursor.fetchall()
            for i in films:
                titre = i[1]
                locations.append({
                    'titre':titre,
                    'categorie':i[2],
                    'location':'categorieFilm/'+idcat+'/film/'+str(i[0])})
        except sqlite3.Error as e:
            print("Erreur",e)
            connection.rollback()
        finally:
            connection.close()
            return(jsonify(locations))

    

"""
Gestion des films 
"""

@api.route('/film/edit')
class editFilm(Resource):
    @api.doc(body=filmpost, model=filmget)
    def post(self):
        """
        Ajout d'un film 
        """
        film = {}
        id = 0
        if request.json :
            try:
                connection = sqlite3.connect("video1.db")
                cursor = connection.cursor()
                
                cursor.execute("SELECT film.id_film FROM film")
                id = len(cursor.fetchall())+1

                categories = request.json['categorie']
                
                new_film = (request.json['titre'],
                            request.json['acteur_film'],
                            request.json['annee_realisation'],
                            request.json['duree'],
                            request.json['resume_film'],
                            request.json['age_min'])

                cursor.execute('INSERT INTO film (titre_film,acteurs_film,annee_realisation,duree_film,resume_film,age_min) VALUES(?,?,?,?,?,?)',new_film)
                #id = cursor.lastrowid
                for i in categories:
                    film_cat = (id,i)
                    cursor.execute('INSERT INTO film_categorie VALUES (?,?)',film_cat)

                connection.commit()

                film['titre']=request.json['titre']
                film['acteur film']=request.json['acteur_film']
                film['année réalisation']=request.json['année réalisation']
                film['durée']=request.json['durée']
                film['résumé film']=request.json['resume_film']
                film['age minimum']=request.json['age_min']
                
            

            except Exception as e:
                print("[Erreur]",e)
                connection.rollback()
            
            finally:
                connection.close()

            response = jsonify(film)
            response.status_code = 201
            response.headers['location'] = '/film/'+str(id)
            return response

        else:
            abort(415)
    

@api.route('/film/<idfilm>')
class FilmOne(Resource):
    @api.doc(model=filmget)
    def get(self,idfilm):
        """
        Retourne le détail d'un film
        """
        connection = sqlite3.connect('video1.db')
        cursor = connection.cursor()
        cursor.execute("SELECT id_film FROM film")
        last_id = len(cursor.fetchall())

        if int(idfilm) > last_id or int(idfilm)==0:
            connection.close()
            abort(404)

        id = (int(idfilm),)
        query1 = 'SELECT * FROM film WHERE id_film = ?'
        cursor.execute(query1,id)
        film = cursor.fetchall()

        sql1 = '''SELECT categorie.nom_categorie FROM categorie
                JOIN film_categorie 
                ON categorie.id_categorie = film_categorie.categorie_id
                JOIN film
                ON film_categorie.film_id = film.id_film
                WHERE film_categorie.film_id = ?
                '''
        cursor.execute(sql1,id)
        categories = cursor.fetchall()
        categorie = ''
        for i in categories:
            categorie += i[0] + ' '


        film_detail = {
            'id':film[0][0],
            'titre':film[0][1],
            'categorie':categorie,
            'acteur film':film[0][2],
            'annee realisation':film[0][3],
            'duree':film[0][4],
            'resume film':film[0][5],
            'age minimum':film[0][6]
        }

        connection.close()

        response = jsonify(film_detail)
        response.status=200
        return response 


    @api.doc(body=filmpost, model=filmget)
    def put(self,idfilm):
        """
        Modifie les détails d'un film
        """

        if request.json:
            int_filmId = int(idfilm)
            connection = sqlite3.connect("video1.db")
            cursor = connection.cursor()

            cursor.execute('SELECT id_film FROM film')
            films_id = []
            film = {}
            for i in cursor.fetchall():
                films_id.append(int(i[0]))

            if int_filmId not in films_id:
                abort(404)

            try:
                update_film = (request.json['titre'],request.json['acteur_film'],request.json['annee_realisation'],request.json['duree'],request.json['resume_film'],request.json['age_min'],int_filmId)
                cursor.execute("""UPDATE film SET 
                                titre_film = ?,
                                acteurs_film = ?,
                                annee_realisation = ?,
                                duree_film = ?,
                                resume_film = ?,
                                age_min = ?
                                WHERE id_film = ?""",update_film)
                connection.commit()

                film['titre']=request.json['titre']
                film['acteurs film']=request.json['acteur_film']
                film['année réalisation']=request.json['annee_realisation']
                film['durée']=request.json['duree']
                film['resume film']=request.json['resume_film']
                film['age minimum']=request.json['age_min']
            
            except sqlite3.Error as e:
                connection.rollback()
                abort(400)
            finally:
                connection.close()

            response = jsonify(film)
            response.status_code=200
            response.headers['location']='/film/'+idfilm
            return response
        
        else:
            abort(415)

    @api.doc()
    def delete(self,idfilm):
        """
        Supprimer un film 
        """
        connection = sqlite3.connect("video1.db")
        cursor = connection.cursor()

        cursor.execute("SELECT id_film FROM film")
        film_id = []

        for i in cursor.fetchall():
            film_id.append(int(i[0]))
        
        if int(idfilm) not in film_id:
            abort(404)

        try:
            film_delete = (int(idfilm),)
            cursor.execute("DELETE FROM film WHERE id_film = ?",film_delete)
            connection.commit()
        except sqlite3.Error as e:
            print("Erreur lors de la suppression du film",e)
            connection.rollback()
        finally:
            connection.close()
            return()



"""
Gestion des clients
"""

@api.route("/clients")
class client(Resource):
    @api.doc(model=add_client)
    def get(self):
        """
        Retourne la liste de tous les clients
        """
        connection = sqlite3.connect("video1.db")
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM client;')
            clients = cursor.fetchall()
            app.logger.info(clients[0])
        except sqlite3.Error as e:
            raise(e)
        finally:
            connection.close()

        
        return jsonify(self.ClienttoJson(clients))
    
    def ClienttoJson(self, clients):
        allClientList = []
        for client in clients:
            row = {"nom_client": client[1], "prenom": client[2], "email": client[3], "age": client[4]}
            allClientList.append(row)
        return allClientList

    @api.doc(body=add_client, model=add_client)
    def post(self):
        """
        Ajout d'un nouveau client
        """

        newClient = {}
        if request.json:
            connection = sqlite3.connect('video1.db')
            try:
                
                cursor = connection.cursor()
                
                var =  (request.json["nom_client"], request.json["prenom"], request.json["email"], request.json["age"])
                query = 'INSERT INTO client(nom_client, prenom, email, age) VALUES (?, ?, ?, ?)'
                
                cursor.execute(query, var)
                connection.commit()
                
            except sqlite3.Error as e:
                connection.rollback()
                print(e)
            finally:
                connection.close()

            newClient["nom_client"] = request.json["nom_client"]
            newClient["prenom"] = request.json["prenom"]
            newClient["email"] = request.json["email"]
            newClient["age"] = request.json["age"]
            

            response = jsonify(newClient)
            response.status_code = 201
            response.headers['location'] = '/clients'
            return response
        else:
            abort(415)



if __name__=='__main__' :
    app.run(debug=True)

