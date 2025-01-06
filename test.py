import smtplib
import json 
from email.message import EmailMessage
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    if col == "Stock":
        l.sort(key=lambda x: int(x[0]), reverse=reverse)
    else:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    for column in tv["columns"]:
        tv.heading(column, text=column)
    if reverse:
        tv.heading(col, text=f"{col} ▲")
    else:
        tv.heading(col, text=f"{col} ▼")

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


#test d'envoi email : 
json_file = open("config.json")
gmail_cfg = json.load(json_file)
print(gmail_cfg)

msg = EmailMessage()
msg["to"] = "random@gmail.com"
msg["from"] = gmail_cfg["email"]
msg["Subject"] = "ALERTE MOT DE PASSE COMPROMIS"
msg.set_content("""
Bonjour,

Nous avons détecté que votre mot de passe a été compromis. 
Par mesure de sécurité, nous vous recommandons de le changer immédiatement.

Merci de votre compréhension.

L'équipe de sécurité Dimitri le Goat et Malo le blond
""")
with smtplib.SMTP_SSL(gmail_cfg["server"],gmail_cfg["port"]) as smtp:
    smtp.login(gmail_cfg["email"],gmail_cfg["pwd"])
    smtp.send_message(msg)
    print("le mot de passe a bien été envoyé")


