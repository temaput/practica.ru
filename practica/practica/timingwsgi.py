"""
My simple timing wsgi middleware. Should serve as wsgi app for gunicorn, and
as wsgi server for django. Starts timing berfore calling django routines,
stops upon  receiving the start_response
"""

import time
class TimingWSGIMiddleware:

    def __init__(self, djangoapp):
        """
        We instatiate the middleware like that:
        application = TimingWSGIMiddleware(dangoapplication)
        """
        self.djangoapp = djangoapp

    def __call__(self, environ, start_response):
        """
        simpliest is just return self.djangoapp(environ, start_response)
        """
        def start_response_wrapper(start_response_ref, timings):
            def start_response_runner(status, response_headers, exc_info=None):
                """
                Here we find out when the response from django starts
                """
                timings.update(dict(
                    end_cpu = time.clock(),
                    end_real = time.time()
                ))
                start_response_ref(status, response_headers, exc_info)
            return start_response_runner


        timings = dict(
            start_cpu = time.clock(),
            start_real= time.time(),
        )

        result_ = self.djangoapp(environ, start_response_wrapper(start_response, timings))
        result = list(result_)
        result.append("%f Real Seconds\n<br>" % (timings['end_real']-timings['start_real']))
        result.append("%f CPU seconds\n<br>" % (timings['end_cpu']-timings['start_cpu']))
        return result

from cProfile import Profile
from pstats import Stats
import StringIO
sort_tuple = ('time', 'calls')

class ProfilingWSGIMiddleware:

    def __init__(self, djangoapp):
        """
        We instatiate the middleware like that:
        application = TimingWSGIMiddleware(dangoapplication)
        """
        self.djangoapp = djangoapp

    def __call__(self, environ, start_response):
        """
        simpliest is just return self.djangoapp(environ, start_response)
        """
        def start_response_wrapper(start_response_ref, timings, prof):
            def start_response_runner(status, response_headers, exc_info=None):
                """
                Here we find out when the response from django starts
                """
                timings.update(dict(
                    end_cpu = time.clock(),
                    end_real = time.time()
                ))
                prof.create_stats()
                start_response_ref(status, response_headers, exc_info)
            return start_response_runner


        timings = dict(
            start_cpu = time.clock(),
            start_real= time.time(),
        )

        prof = Profile()
        wsgiargs = [environ, start_response_wrapper(start_response, timings, prof)]
        result_ = prof.runcall(self.djangoapp, *wsgiargs, **{})

        out = StringIO.StringIO()
        stats = Stats(prof, stream=out)
        stats.sort_stats(*sort_tuple)
        stats.print_stats()

        result = list(result_)
        result.append("<pre>%f Real Seconds\n" % (timings['end_real']-timings['start_real']))
        result.append("%f CPU seconds\n" % (timings['end_cpu']-timings['start_cpu']))
        result.append("%s</pre>" % out.getvalue())
        return result
