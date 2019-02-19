from redis import Redis
redis = Redis()

import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify 

app = Flask(__name__)



class RateLimit(object):
    #give extra 10 seconds for key to expire in redis so that badly synchronized clocks between workers and redis server do not cause problems
    expiration_window = 10

    #key is a string that is used to keep track of the rate limits from each request
    #limit and per defind the number of rquests we want to allow over certain time period
    #send_x_headers is boolean that allow us to inject into each repsonse header the number of remaining requests a client can make before hitting limit
    def __init__(self, key_prefix, limit, per, send_x_headers):
        #reset keeps timestamp to indicate when a request limit can reset itself
        #why did they want to divide by per and then multiply by per? why don't they just add per to the current time?
        #time reset does not start from when it is first accessed - it starts from the last interval. (so if you accessed it at 1:15, but its time limit is every half hour, then the time actually started at 1:00, and will reset at 1:30)
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        #use a pipeline so make sure to never increment a key without also setting the key expiration in case an exceptin happens between those lines
        p = redis.pipeline()
        #increment value of pipeline
        p.incr(self.key)
        #set it to expire based on reset value and expirationn window
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)
    #calculate how many remaining requests 
    remaining = property(lambda x: x.limit - x.current)
    #check to see if hit the rate limit
    over_limit = property(lambda x: x.current >= x.limit)

#gets the view_rate_limit attribute from g in flask
def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)

#a messafe for when user has reached their limit, with 429 error (which means too many requests)
def on_over_limit(limit):
    return (jsonify({'data':'You hit the rate limit','error':'429'}),429)

#create ratelimit that wraps around decorator method 
def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            #use RateLimit class, and store it in g as view_rate_limit
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator




#append number of remaining requests, the limit for the endpoint, and time until limit resets itself inside header of each response
@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    #the rate limit feature can be turned off if send_x_headers is set to False
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response

@app.route('/rate-limited')
#only allow 300 requests per 30 seconds
@ratelimit(limit=300, per=30 * 1)
def index():
    return jsonify({'response':'This is a rate limited response'})

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)