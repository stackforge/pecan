from pecan import expose, response, abort
from pecan.rest import RestController

people = {
    1: 'Luke',
    2: 'Leia',
    3: 'Han',
    4: 'Anakin'
}


class PeopleController(RestController):

    @expose('json')
    def get_all(self):
        return people

    @expose()
    def get_one(self, person_id):
        return people.get(int(person_id)) or abort(404)

    @expose()
    def post(self):
        # TODO: Create a new person
        response.status = 201

    @expose()
    def put(self, person_id):
        # TODO: Idempotent PUT (returns 200 or 204)
        response.status = 204

    @expose()
    def delete(self, person_id):
        # TODO: Idempotent DELETE
        response.status = 200


class RootController(object):

    people = PeopleController()

    @expose()
    def index(self):
        return "Hello, World!"
