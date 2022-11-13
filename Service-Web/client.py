from video import *


clientpost = api.model('clientpost',{'nom':fields.String(exemple='Lalis'),
                        'prenom':fields.String(exemple='William'),
                        'email':fields.String(exemple='wi@hotmail.fr'),
                        'age':fields.Integer(exemple='23')})
clientget = api.model('clientget',{'id':fields.Integer(exemple=1),
                        'nom':fields.String(exemple='Lalis'),
                        'prenom':fields.String(exemple='William'),
                        'email':fields.String(exemple='wi@hotmail.fr'),
                        'age':fields.Integer(exemple='23')})


@api.route('/clients/<idclient>')
class ClientId(Resource):
    @api.doc(model = clientget)
    def get(self,idclient):
        """
        Retourne le détail d'un client
        """
        connection = sqlite3.connect('video1.db')
        cursor = connection.cursor()
        cursor.execute('SELECT id_client FROM client ')
        last_id = len(cursor.fetchall())
        if int(idclient) > last_id or int(idclient)==0:
            connection.close()
            abort(404)
        
        id = (idclient,)
        cursor.execute('SELECT * FROM Client WHERE id_client = ?',id)
        req = cursor.fetchone()

        client = {
            'id':req[0],
            'Nom':req[1],
            'Prenom':req[2],
            'Adress mail':req[3],
            'Age':req[4]
        }

        connection.close()

        response=jsonify(client)
        response.status=200
        return response

    @api.doc(body=clientpost, model=clientget)
    def put(self,idclient):
        """
        Modifie les détails d'un client (Nom, Prenom, )
        """
        if request.json:
            intid = int(idclient)
            connection = sqlite3.connect("video1.db")
            cursor = connection.cursor()

            cursor.execute('SELECT id_client FROM client')
            client_id = []
            client = {}
            for i in cursor.fetchall():
                client_id.append(int(i[0]))
            
            if intid not in client_id:
                abort(404)

            try:
                update_client = (request.json['nom'],request.json['prenom'],request.json['email'],request.json['age'],intid)
                cursor.execute('UPDATE client SET nom_client = ?, prenom = ?, email = ?, age = ?  WHERE id_client = ?',update_client)
                connection.commit()

                client['nom']=request.json['nom']
                client['prenom']=request.json['prenom']
                client['email']=request.json['email']
                client['age']=request.json['age']

            except(TypeError, ValueError):
                abort(400)
                connection.rollback()
            finally:
                connection.close()


            response = jsonify(client)
            response.status_code=200
            response.headers['location'] = '/clients'+str(intid)
            return response

        else:
            abort(415)

    @api.doc()
    def delete(self,idclient):
        """
        Supprimer un client
        """
        intid = int(idclient)

        connection = sqlite3.connect("video1.db")
        cursor = connection.cursor()

        cursor.execute('SELECT id_client FROM client')
        client_id = []
        for i in cursor.fetchall():
            client_id.append(int(i[0]))
        
        if intid not in client_id:
            abort(404)
        
        try:
            client_delete = (intid,)
            cursor.execute('DELETE FROM client WHERE id_client = ?',client_delete)
            connection.commit()
        except sqlite3.Error as e:
            print("Erreur lors de la suppression du client ",e)
            connection.rollback()
        finally:
            connection.close()
            return()

@api.route('/clients/<idclient>/film')
class ClientFilmAll(Resource):
    api.doc(model=get_allfilm)
    def get(self,idclient):
        """
        Retourne le titre et la location de tout les films compris dans 
        cette catégorie 
        """
        locations = []
        try:
            connection = sqlite3.connect('video1.db')
            cursor = connection.cursor()
            id = (int(idclient),)
            sql = """SELECT film.id_film,film.titre_film, categorie.nom_categorie FROM film
                    JOIN film_categorie
                    ON film.id_film = film_categorie.film_id
                    JOIN categorie
                    ON film_categorie.categorie_id = categorie.id_categorie
                    WHERE categorie.id_categorie = ?
                    """
            
            cursor.execute(sql,id)
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

    @api.doc(body=filmpost, model=filmget)
    def post(self,idcat):
        """
        Ajout d'un film dans la catégorie
        """
        film = {}
        id = 0
        intid = int(idcat)
        if request.json :
            try:
                connection = sqlite3.Connection("video1.db")
                cursor = connection.cursor()
                
                cursor.execute("SELECT film.id_film FROM film")
                id = len(cursor.fetchall())+1
                
                new_film = (id,request.json['titre'],
                            request.json['acteur_film'],
                            request.json['année réalisation'],
                            request.json['durée'],
                            request.json['resume_film'],
                            request.json['age_min'])

                cursor.execute('INSERT INTO film VALUES(?,?,?,?,?,?,?)',new_film)
                #id = cursor.lastrowid
                film_cat = (id,intid)
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
            response.headers['location'] = 'categorieFilm/'+idcat+'/film/'+str(id)
            return response

        else:
            abort(415)


if __name__=='__main__' :
    app.run(debug=True)