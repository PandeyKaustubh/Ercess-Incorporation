from django import template



register  =  template.Library()


# @register(name = 'cut')
def slice(value):

    return value[:300]


register.filter('cut' , slice)
