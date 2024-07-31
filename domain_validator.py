import whois

def is_registered ( domain_name ):


    """ A function that returns a boolean indicating whether a 'domain name is registerd """

    try : 

        w = whois . whois (domain_name)

    except Exception: 
        return False
    
    else: 
        return bool(w.domain_name)
    

if __name__ == "__main__":

    print(is_registered ("google.com"))

    print(is_registered("pfx.com.ng"))
