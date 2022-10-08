from dashboard.models import ShortUrlTracker
import random
from django.shortcuts import redirect
from django.http import HttpResponse

#get random string for url
def get_random(tries=0):
    length = 5
    length += tries

    # Removed l, I, 1
    dictionary = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz234567890"
    return ''.join(random.choice(dictionary) for _ in range(length))


def create(event_id, link, source):
    for tries in range(3):
        try:
            short = get_random(tries)
            shortUrlFilter = ShortUrlTracker.objects.filter(short_url=short)
            if(len(shortUrlFilter) == 0):
                ShortUrlTracker.objects.create(event_id=event_id, short_url=short, original_url=link, source=source)
                return short
        except:
            continue

def expand_url(request, slug):
    try:
        short = slug
        shortUrlFilter = ShortUrlTracker.objects.filter(short_url=short).values('original_url')
        if(len(shortUrlFilter) == 1):
            original_url = list(shortUrlFilter)[0]['original_url']
            if original_url != '':
                return redirect(original_url)
            else:
                return HttpResponse('<h1 style="margin-top:50px;">Hold on!<br/> The page is not yet ready for you to see.</h1>')
        else:
            return HttpResponse('<h1 style="margin-top:50px;">Hold on!<br/> The page is not yet ready for you to see.</h1>')
    except Exception as e:
        pass

