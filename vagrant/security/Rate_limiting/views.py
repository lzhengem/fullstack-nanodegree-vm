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
        self.reset = (int(time.time()) // per) * per + per #when it can reset itself (in unix time)
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers

        #use a pipeline so make sure to never increment a key without also setting the key expiration in case an exceptin happens between those lines
        p = redis.pipeline() #make sure to increment key and set expiration at same time.
        p.incr(self.key) #increment pipeline
        p.expireat(self.key, self.reset + self.expiration_window) #set to expire at reset value + expiration window
        self.current = min(p.execute()[0], limit) #current is how many requests currently made

    remaining = property(lambda x: x.limit - x.current) #how many remaining requests available until time expires
    over_limit = property(lambda x: x.current >= x.limit) #returns true if requests made hit or exceeds limit

def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None) #_view_rate_limit will be of class RateLimit

def on_over_limit(limit):
    return (jsonify({'data':'You hit the rate limit','error':'429'}),429)

def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit) #if it is over the limit, return a message that tells them that theyve hit the limit
            return f(*args, **kwargs) #if it is not over the limit, return f with args?
        return update_wrapper(rate_limited, f)
    return decorator




#after the request, if this resource requests to send headers, append the limi status to the headers
@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
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