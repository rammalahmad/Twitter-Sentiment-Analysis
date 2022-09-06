'''
This file contains all the constants of SurfMetrics twitter project
'''

#Scraping:

BEARER_Token = "AAAAAAAAAAAAAAAAAAAAAOkFdgEAAAAANo34nERWQRp4cssRA2FU80w2ohM%3D8t2Z4Lh5MakNsaKrRradEFf36nOTxg9SjgJa3eISYggqxcYNdY"
consumer_key= 'KXHbQNIaed9ywyS1lmpKSXI3R'
consumer_secret= 'OivZv9DtACA0J0evHAG3bC1DeZ29l1pz5CM7LaO5lNFibJq7rl'
access_token= '1534544118893973505-SkeusWYlvDUip4TlXKSK4hiyEpgjCZ'
access_token_secret= 'h6cmAj92Atkq6zDfiipBTb4gFEdjqN2gfnpJFHgK1tg7M'
search_url = "https://api.twitter.com/1.1/tweets/search/fullarchive/Scraping.json"


#ESG Filtering

E_dic_fr = ["carbone", "durable", "empreinte", "gaspillage", "co2", "energie fossile", 
        "contamination", "environnement", " déchets","activités minières et extractives", 
         "biologique","atmosphère", "altermondialisme", "biodiversité", "biomasse", "biosphère",
         "changement climatique", "circuit court", "climat", "collapsologie", "combustibles nucléaires",
          "commerce équitable", "consommation"," responsable", "convention climat","crise écologique", 
          "cycle de vie du produit", "déchets radioactifs", "décroissance", "déforestation", 
         "démantèlement des centrales nucléaires","droits environnementaux","écologie", "économie circulaire", 
         "economie sociale et solidaire", "Economie verte", "ecoquartier", "ecosystèmes", "effet de serre", 
         "efficacité énergétique", "empreinte écologique","energie fossile ", "energie nucléaire",
        "energies renouvelables", "erosion", "forêts", "gaz de schiste", "matières premières", "méthane",
         "micropolluants", "nature", "niveau de la mer","normes et labels", "ONGs", "parties prenantes", 
         "pesticides", "pétrole", "plan climat", "politique environnementale","pollutions", "recyclage", "réfugiés climatiques", 
         "responsabilité sociale des entreprises", "ressources naturelles", "risques naturels", "transition","urbanisation"]

S_dic_fr = ["carriere", "donation", "diversite", "ecart salarial",  "ecart revenus",  "satisfaction", "union", "employe", 
        "licenciements", "genre", "femme", "discrimination", "accidents", "dommages", "droits de l’homme", "egalite", "corruption", 
        "alcool", "drogues", "sexe",  "tabac", "armes", "accès à 0l’eau", "accès aux droits", "aide au développement", "bien commun", 
        "citoyenneté", "contrat social", "crise économique", "crise financière", "crise sociale", "délocalisations", "démocratie", 
        "droit à l’eau", "droits économiques, sociaux et culturels", "droits humains", "education", "emploi", "ethique", "exclusion", 
        "finance solidaire", "guerre", "inégalité écologique", "inégalité sociale", "inégalités", "mesure du bien-être", "migration", 
        "paix", "politiques migratoires", "santé", "sécurité", "solidarité"]

G_dic_fr = ["gouvernance", "politique", "formation", "talents", "carriere", "board","corporate", "conseil administration","comite", 
        "nomination", "executif", "audit", "structure", "performance","experience", "PDG", "DG", "Directeur", "compte-rendu", "reunions", 
        "CEO", "President",  "election", "senior", "revenus", "remuneration", "actionnaires", "chef", "vote", "directeur", "gouvernement",
         "parachute dore", "confidentiel", "CSR", "investissement"]


E_dic_en = ["carbon", "sustainable", "footprint", "waste", "co2", "fossil fuel", "contamination", "environment", "waste", 
        "mining and quarrying", "biological", "atmosphere", "alterglobalism", "biodiversity", "biomass", "biosphere", "climate change", 
        "short circuit", "climate", "collapsology", "nuclear fuels", "fair trade", "consumption", "responsible", "climate convention",
        "ecological crisis", "product life cycle", "radioactive waste", "degrowth", "deforestation", "dismantling of nuclear power plants",
        "environmental rights", "ecology", "circular economy", "social and solidarity economy", "green economy", "eco-district",
        "ecosystems", "greenhouse effect", "energy efficiency", "ecological footprint", "fossil energy", "nuclear energy",
        "renewable energy", "erosion", "forests", "shale gas", "raw materials", "methane", "micropollutants", "nature", "sea level",
        "standards and labels", "NGOs", "stakeholders", "pesticides", "oil", "climate plan", "environmental policy", "pollution", 
        "recycling", "climate refugees", "corporate social responsibility", "natural resources", "natural risks", "transition", 
        "urbanisation"]


S_dic_en = ["career", "donation", "diversity", "wage gap", "income gap", "satisfaction", "union", "employee", "dismissals", "gender", 
        "woman", "discrimination", "accidents", "damage", "human rights", "equality", "corruption", "alcohol", "drugs", "sex", "tobacco",
        "weapons", "access to water", "access to rights", "development aid", "common good", "citizenship", "social contract",
        "economic crisis", "financial crisis", "social crisis", "relocations", "democracy", "right to water", 
        "economic, social and cultural rights", "human rights", "education", "employment", 
        "ethics", "exclusion", "solidarity finance", "war", "ecological inequality", "social inequality", "inequalities", 
        "measuring well-being", "migration", "peace", "migration policies", "health", "security", "solidarity"]


G_dic_en = ["governance", "policy", "training", "skills", "career", "board", "corporate",  "governance",  "committee", "nomination", 
        "executive", "audit", "structure", "performance",  "experience",  "reporting", "external", "meetings", "CEO", "Chairman", 
        "election", "senior", "wage","remuneration", "shareholders", "chief", "vote", "director", "state", "government", 
        "golden parachute", "confidential", "CSR", "stakeholder", "investment"]




fr_dic = [E_dic_fr,S_dic_fr,G_dic_fr]

en_dic = [E_dic_en,S_dic_en,G_dic_en]