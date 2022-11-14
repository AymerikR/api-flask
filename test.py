import requests
from answer import ans

url="http://127.0.0.1:5000"

def get_categorieFilm_assert():

    print("\nTest get  categorieFilm :")

    _url = url + '/categorieFilm'
    response = requests.get(_url)

    assert(response.status_code==200)
    print("\t -test status code passed.")

    assert(response.json()[1]==ans["catFilm"][1])
    print("\t -test answer passed.")

def post_categorieFilm_assert():

    print("\nTest post categorieFilm :")

    body = {"intitule": "testCategorie", "description": "..."}

    _url = url + '/categorieFilm'
    response = requests.post(_url, json=body)

    assert(response.status_code==201)
    print("\t -test status code passed.")

    assert(response.json() == body)
    print("\t -test answer passed.")

def get_categorieFilm_id_assert():
    print("\nTest get categorieFilm/id :")

    _url = url + '/categorieFilm/2'
    response = requests.get(_url)

    assert(response.status_code==200)
    print("\t -test status code passed.")

    assert(response.json()==ans["catId"])
    print("\t -test answer passed.")

def get_categorieFilm_id_film_assert():
    print("\nTest get categorieFilm/id/film :")

    _url = url + '/categorieFilm/2/film'
    response = requests.get(_url)

    assert(response.status_code==200)
    print("\t -test status code passed.")

    assert(response.json()==ans["catIdFilm"])
    print("\t -test answer passed.")

def get_clients_assert():

    print("\nTest get clients :")

    _url = url + "/clients"
    response = requests.get(_url)

    assert(response.status_code==200)
    print("\t -test status code passed.")
    
    for i in range(3):
        assert(response.json()[i]==ans["getClient"][i])
    print("\t -test answer passed.")

def post_client_assert():

    print("\nTest post client :")

    body = {"nom_client" : "testNom", "prenom": "testPrenom","email" : "test@email.iot", "age": 1}
    _url = url + "/clients" 
    response = requests.post(_url, json=body)

    assert(response.status_code==201)
    print("\t -test status code passed.")

    assert(response.json() == body)
    print("\t -test answer passed.")

## Not working
def delete_categorieFilm_id_assert():
    print("\nTest delete Categorie :")

    _url = url + "/categorieFilm/7" 
    response = requests.delete(_url)
    print(response.status_code)
    assert(response.status_code==200)
    print("\t -test status code passed.")

    print(response.json())
    assert(response.json() == 0)
    print("\t -test answer passed.")

def post_film_edit_assert():
    
    print("\nTest post film edit :")

    _url = url + "/film/edit" 
    response = requests.post(_url, json=ans["postFilm"])

    assert(response.status_code==201)
    print("\t -test status code passed.")

    test = {'acteur film': 'test acteur', 'titre': 'testFilm'}
    assert(response.json() == test)
    print("\t -test answer passed.")

def get_film_id_assert():
    
    print("\nTest get film id :")

    _url = url + "/film/1"
    response = requests.get(_url)

    assert(response.status_code==200)
    print("\t -test status code passed.")
    
    assert(response.json()==ans["getFilmId"])
    
    print("\t -test answer passed.")

def get_assert():
    get_categorieFilm_assert()
    get_categorieFilm_id_assert()
    get_categorieFilm_id_film_assert()
    get_clients_assert()
    get_film_id_assert

def post_assert():
    post_categorieFilm_assert()
    post_client_assert()
    post_film_edit_assert()

get_assert()
post_assert()