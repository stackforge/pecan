from pecan import expose, response, abort

people = {
    1: 'Luke',
    2: 'Leia',
    3: 'Han',
    4: 'Anakin'
}


class PersonController(object):

    def __init__(self, person_id):
        self.person_id = person_id

    @expose(generic=True)
    def index(self):
        return people.get(self.person_id) or abort(404)

    @index.when(method='PUT')
    def put(self):
        # TODO: Idempotent PUT (returns 200 or 204)
        response.status = 204

    @index.when(method='DELETE')
    def delete(self):
        # TODO: Idempotent DELETE
        response.status = 204


class PeopleController(object):

    @expose()
    def _lookup(self, person_id, *remainder):
        return PersonController(int(person_id)), remainder

    @expose(generic=True, template='json')
    def index(self):
        return people

    @index.when(method='POST', template='json')
    def post(self):
        # TODO: Create a new person
        response.status = 201


class RootController(object):

    people = PeopleController()

    @expose()
    def index(self):
        return "Hello, World!"
