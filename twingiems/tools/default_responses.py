''' This module defines the default responses the flask app can respond with.
'''

OK_QUERY_CODE = 200
OK_QUERY_RESPONSE = 'OK'

NULL_QUERY_CODE = 400
NULL_QUERY_RESPONSE = 'Query returned no tweets.'

BAD_QUERY_CODE = 400
BAD_QUERY_RESPONSE = 'Request was not for a user.'

BAD_ROUTE_CODE = 404
BAD_ROUTE_RESPONSE = 'Bad route'
