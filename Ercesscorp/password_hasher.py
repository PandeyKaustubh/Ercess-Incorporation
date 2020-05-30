from werkzeug.security import generate_password_hash, check_password_hash


def checker(hash, pasw):
    c = 0
    for x in range(len(hash)) :
        p =  hash[c]['password1']
        if check_password_hash(p, pasw) :
            break
            return True
        else:
            return False
    c+= 1



def hasher(pasw):

    hashp = generate_password_hash(pasw)
    if hashp is not None:
        return hashp
    else:
        return 'unable to hash'








