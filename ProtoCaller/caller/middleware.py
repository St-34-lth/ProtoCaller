from django.http import HttpResponseRedirect
# my code starts here 

#redirects to index on 404 status.
class RedirectToIndexMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if the response status is 404 (Page Not Found)
        if response.status_code == 404:
            print('redirected to index')
            
            return HttpResponseRedirect('/')

        return response
    
# my code starts here 