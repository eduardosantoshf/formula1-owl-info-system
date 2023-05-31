# ws-second-project

### How to run

#### Instalar os requirements

    $ cd f1_app/
    $ pip install -r requirements.txt

#### GraphDB

    - criar um repositório com o nome "db"
    - importar os ficheiros "datasets/f1.nt" e "datasets/ontology.n3"

#### Aplicação

    $ python3 manage.py runserver

#### Inferências

Para ter o sistema totalmente funcional, é necessário realizar as inferências.

    $ python manage.py createsuperuser

Depois de criar o admin, fazer login como admin, ir à pagina de admin e clicar no botão das inferências.

