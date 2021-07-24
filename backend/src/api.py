import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json, demjson
from sqlalchemy.sql.expression import join


from sqlalchemy.sql.sqltypes import String
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth, get_token_auth_header, verify_decode_jwt



app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():

    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
    }, 200)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(jwt):
    
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }, 200)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods = ['POST'])
@requires_auth(permission='post:drinks')
def post_drinks(jwt):

    

    
    
    try:
        
        drinks_to_create = request.get_json()
    
        if drinks_to_create is None:
            abort(422)

        drinks = [Drink(title= drink.title, recipe = drink.recipe) for drink in drinks_to_create]

        for drink in drinks:
            drink.insert()
    
        return jsonify({
            "success": True, "drinks": drinks_to_create
        })

    except:
        abort(422)
    
    finally:
        db.session.close()




'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods = ['PATCH'])
# @requires_auth(permission='patch:drinks')
def patch_drinks(id):

    drink = Drink.query.get(id)

    if drink is None:

        abort(404)

    drink_to_update = request.get_json()

    drink.title = drink_to_update['title']    

    drink.recipe = demjson.encode(drink_to_update['recipe'], encoding = 'utf-8')    

    drink.update()

    return jsonify({
        "success": True, 
        "drinks": drink.long()
    })




'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods = ['DELETE'])
# @requires_auth(permission='delete:drinks')
def delete_drinks(id):

    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    drink.delete()

    drink.update()

    return jsonify({
        "success": True, "delete": drink.id
    })



# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
            'success': False,
            'message': 'Not Found',
            'error': 404
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
