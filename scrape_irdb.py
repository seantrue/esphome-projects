from bs4 import BeautifulSoup
import requests

with open("denon_irdb_codes.txt","w") as outf:
    bs = BeautifulSoup(open("denon.html").read(),features="html.parser")
    forms = bs.find_all("form")
    for form in forms:
        label = form.find_all("li")[0].text
        if label.startswith("Denon A/V Receivers"):
            print(label)
            inputs = form.find_all("input")
            post_params = {}
            for inp in inputs:
                try:
                    post_params[inp['name']] =inp['value']
                except KeyError:
                    pass
            response = requests.post("https://irdb.tk/codes/",data=post_params, verify=False)
            text = response.text
            bs2 = BeautifulSoup(text, features="html.parser")
            pronto_codes = bs2.find(id="pronto")
            buttons = pronto_codes.find_all("button")
            codes = pronto_codes.find_all("pre")
            print("{len(codes} codes")
            print(f"#{label}", file=outf)
            for b,c in zip(buttons, codes):
                label = "_".join(b.text.lower().split()).replace(".","")
                print(f"{label}: {c.text}",file=outf)
