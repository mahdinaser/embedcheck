"""ValueShiftBench kill-test set generator (v0).
Each item: subject, relation, change_type, original (template A, value v1),
paraphrase (template B, value v1), update_min (template A, value v2),
update_para (template B, value v2), query (question about subject+relation).
All entities are fictional to avoid memorisation/contamination."""
import json, random
random.seed(20261026)

PROJECTS = ["Project Orion","Project Halcyon","the Bluefin initiative","Project Tamarisk","the Larkspur program",
  "Project Meridian","the Cobalt Ridge study","Project Wren","the Saffron pilot","Project Ostrava"]
COMPANIES = ["Kestrel Labs","Northwind Analytics","Velora Systems","Brightwater Foods","Quillon Robotics",
  "Harrow & Finch","Tessaline Bio","Corvid Logistics","Pinecrest Media","Sundial Energy"]
PEOPLE = ["Amara Voss","Tobias Renwick","Lena Okafor","Mateo Lindqvist","Priya Raman",
  "Jonah Whitlow","Selin Aydin","Marcus Feld","Hana Kobayashi","Elio Martell"]
CITIES = ["Lisbon","Denver","Osaka","Nairobi","Krakow","Montreal","Auckland","Valencia","Tallinn","Recife"]
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

def money(): return random.choice([2,3,4,5,6,7,8,9,12,15,18,25])
SPECS = {
 "number": [
  dict(subj=PROJECTS, q="What is the budget of {s}?",
       A="{s}'s budget is ${v} million.", B="The budget allocated to {s} is {v} million dollars.",
       C="{s} has been given a budget of ${v}M.", val=lambda: money()),
  dict(subj=COMPANIES, q="How many employees does {s} have?",
       A="{s} has {v} employees.", B="The workforce at {s} numbers {v} people.",
       C="{s} currently employs {v} staff.", val=lambda: random.choice([40,85,120,240,310,560,900,1400])),
  dict(subj=PEOPLE, q="How many days of leave does {s} have left?",
       A="{s} has {v} vacation days remaining.", B="There are {v} days of leave left for {s}.",
       C="{s}'s remaining annual leave is {v} days.", val=lambda: random.choice([3,5,7,9,12,14,18,21])),
 ],
 "date": [
  dict(subj=PROJECTS, q="When is the deadline for {s}?",
       A="The deadline for {s} is {v}.", B="{s} must be finished by {v}.",
       C="{s} is due on {v}.", val=lambda: f"{random.choice(MONTHS)} {random.randint(1,28)}"),
  dict(subj=PEOPLE, q="When is {s}'s dentist appointment?",
       A="{s}'s dentist appointment is on {v}.", B="{s} is scheduled to see the dentist on {v}.",
       C="{s} has a dental visit booked for {v}.", val=lambda: f"{random.choice(MONTHS)} {random.randint(1,28)}"),
 ],
 "entity": [
  dict(subj=PROJECTS, q="Who leads {s}?",
       A="{s} is led by {v}.", B="The lead on {s} is {v}.", C="{v} is in charge of {s}.",
       val=lambda: random.choice(PEOPLE)),
  dict(subj=COMPANIES, q="Where is {s} headquartered?",
       A="{s} is headquartered in {v}.", B="The main office of {s} is located in {v}.",
       C="{s} has its head office in {v}.", val=lambda: random.choice(CITIES)),
  dict(subj=PEOPLE, q="Who does {s} report to?",
       A="{s} reports to {v}.", B="{s}'s manager is {v}.", C="{v} is the direct supervisor of {s}.",
       val=lambda: random.choice(PEOPLE)),
 ],
 "status": [
  dict(subj=PROJECTS, q="What is the status of {s}?",
       A="{s} is currently {v}.", B="The status of {s} is {v}.", C="Right now {s} is {v}.",
       val=lambda: random.choice(["active","on hold","cancelled","completed","under review"])),
  dict(subj=PEOPLE, q="What is the status of {s}'s visa application?",
       A="{s}'s visa application is {v}.", B="The visa request filed by {s} has been {v}.",
       C="As for {s}'s visa, the application is {v}.", val=lambda: random.choice(["approved","rejected","pending","withdrawn"])),
 ],
 "category": [
  dict(subj=PEOPLE, q="What is {s}'s preferred programming language?",
       A="{s}'s preferred programming language is {v}.", B="{s} prefers to code in {v}.",
       C="When writing software, {s} likes to use {v}.", val=lambda: random.choice(["Python","Rust","Go","Java","TypeScript","Julia"])),
  dict(subj=PEOPLE, q="What diet does {s} follow?",
       A="{s} follows a {v} diet.", B="{s} eats a {v} diet.", C="{s}'s diet is {v}.",
       val=lambda: random.choice(["vegetarian","vegan","pescatarian","keto","gluten-free"])),
  dict(subj=COMPANIES, q="Which cloud provider does {s} use?",
       A="{s} runs its infrastructure on {v}.", B="{s}'s cloud provider is {v}.",
       C="{s} hosts its systems with {v}.", val=lambda: random.choice(["AWS","Azure","Google Cloud","Oracle Cloud"])),
 ],
 "polarity": [
  dict(subj=PEOPLE, q="Is {s} attending the offsite?",
       A="{s} {v} attending the offsite.", B="{s} {v2} going to the team offsite.", C="As for the offsite, {s} {v} attending.",
       val=lambda: None, pol=True),
  dict(subj=COMPANIES, q="Does {s} offer remote work?",
       A="{s} {v} remote work.", B="Working remotely {v2} at {s}.", C="{s} {v} employees to work from home.",
       val=lambda: None, pol=True, words=(("offers","does not offer"),("is allowed","is not allowed"),("allows","does not allow"))),
  dict(subj=PROJECTS, q="Has {s} been approved for funding?",
       A="{s} {v} been approved for funding.", B="Funding for {s} {v2} approved.", C="The funding request for {s} {v} been approved.",
       val=lambda: None, pol=True, words=(("has","has not"),("was","was not"),("has","has not"))),
  dict(subj=PEOPLE, q="Does {s} have access to the production database?",
       A="{s} {v} access to the production database.", B="Production database access {v2} granted to {s}.", C="{s} {v} permission to use the production database.",
       val=lambda: None, pol=True, words=(("has","does not have"),("is","is not"),("has","does not have"))),
 ],
}
POL_DEFAULT = (("is","is not"),("is","is not"),("is","is not"))

def render(spec, tmpl, s, v):
    out = _render(spec, tmpl, s, v)
    return out[0].upper() + out[1:]

def _render(spec, tmpl, s, v):
    if spec.get("pol"):
        w = spec.get("words", POL_DEFAULT)
        idx = {"A":0,"B":1,"C":2}[tmpl]
        word = w[idx][0] if v else w[idx][1]
        t = spec[tmpl]
        return t.replace("{v2}", word).replace("{v}", word).format(s=s)
    return spec[tmpl].format(s=s, v=v)

items, seen = [], set()
PER_TYPE = 50
for ctype, specs in SPECS.items():
    n = 0; tries = 0
    while n < PER_TYPE and tries < 5000:
        tries += 1
        spec = random.choice(specs); s = random.choice(spec["subj"])
        if spec.get("pol"):
            v1 = random.choice([True, False]); v2 = not v1
        else:
            v1 = spec["val"](); v2 = spec["val"]()
            if v1 == v2 or (ctype=="entity" and (v1==s or v2==s)): continue
        key = (ctype, spec["q"], s, str(v1), str(v2))
        if key in seen: continue
        seen.add(key)
        a, b = random.sample(["A","B","C"], 2)   # original wording a, paraphrase wording b
        items.append(dict(id=f"{ctype}-{n:03d}", change_type=ctype, subject=s, relation=spec["q"].format(s="X"),
            value_old=str(v1), value_new=str(v2), template_orig=a, template_para=b,
            original=render(spec,a,s,v1), paraphrase=render(spec,b,s,v1),
            update_min=render(spec,a,s,v2), update_para=render(spec,b,s,v2),
            query=spec["q"].format(s=s)))
        n += 1
json.dump(items, open("data/vsb_kill_v0.json","w"), indent=1)
print(len(items), {t: sum(i['change_type']==t for i in items) for t in SPECS})
for it in random.sample(items, 8): print(json.dumps({k:it[k] for k in ['change_type','original','paraphrase','update_min','update_para']}, ensure_ascii=False))
