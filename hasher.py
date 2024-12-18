
import csv
import hashlib
import pandas
h = hashlib.new("SHA256")
def nouveau_user():
    nomuser = input("donne ton user")
    vrai_mdp = input("donne ton mdp on va le haché grr paw")
    h.update(vrai_mdp.encode())
    hache_mdp = h.hexdigest()
    print(hache_mdp)
    with open('csvuser.csv','a', newline='', encoding='utf-8') as fichier :
        writer = csv.writer(fichier)
        writer.writerow([2,nomuser,hache_mdp])
    return 
print(nouveau_user())


def creationuser():
    