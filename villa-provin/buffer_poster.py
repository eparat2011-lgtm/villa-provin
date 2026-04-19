#!/usr/bin/env python3
"""
Villa Provin — Automatischer Instagram Poster via Buffer
Läuft auf der Villa VM und plant Posts direkt in Buffer
"""
import http.client, json, ssl, os, sys
from datetime import datetime, timedelta

BUFFER_TOKEN = 'EG4n_D1PyKZ2hbmkyhVHMOgMn1jzRDl58gzKo-Arobl'
ORG_ID = '69dc0cbc215143c91dff8c95'
CHANNEL_ID = '69dc10fe031bfa423cf8c2c8'  # @villaprovin Instagram

HEADERS = {
    'Authorization': f'Bearer {BUFFER_TOKEN}',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Origin': 'https://publish.buffer.com',
    'Referer': 'https://publish.buffer.com/'
}

def graphql(query_str):
    body = json.dumps({"query": query_str})
    ctx = ssl.create_default_context()
    conn = http.client.HTTPSConnection("api.buffer.com", context=ctx)
    conn.request("POST", "/", body=body, headers=HEADERS)
    resp = conn.getresponse()
    return json.loads(resp.read())

def create_idea(title, text):
    mutation = """mutation {
  createIdea(input: {
    organizationId: \"""" + ORG_ID + """\",
    content: {
      title: \"""" + title.replace('"', "'") + """\"
      text: \"""" + text.replace('"', "'").replace('\n', '\\n') + """\"
    }
  }) {
    ... on Idea { id content { title } }
  }
}"""
    data = graphql(mutation)
    return data.get('data', {}).get('createIdea', {}).get('id')

def list_ideas():
    query = """{ ideas(organizationId: \"""" + ORG_ID + """\") { id content { title } } }"""
    data = graphql(query)
    return data.get('data', {}).get('ideas', [])

# Content Plan
POSTS = [
    {
        "title": "Grillabend unter Sternen",
        "caption": """Stell dir vor: Der warme Abendwind, der Duft von Rosmarin und frisch gegrillten Köstlichkeiten. Am OFYR-Holzgrill entstehen unvergessliche Abende — oder schnell Meeresfrüchte auf der Napoleon-Plancha, ein gekühlter Rosé aus dem Kühlschrank, und direkt in den Salzwasserpool. Das ist Villa Provin. 🥂

#VillaProvin #ProvenceTraum #OutdoorKüche #OFYR #LuxusVilla #Vence #CotedAzur #AlFrescoDining #ProvenceLife #LuxuryTravel #Grillabend #SommerNächte #TraumUrlaub #ProvenceMoments #FrankreichUrlaub""",
        "photo": "IMG_3912.jpg",
        "day": "thursday",
        "time": "19:00"
    },
    {
        "title": "Morgenblick über Vence",
        "caption": """Wach auf in deinem provenzalischen Märchen. Kaffee in der Hand, während die Sonne über Vence und dem Mittelmeer aufgeht. Jeder Morgen hier ist ein Meisterwerk. Das ist nicht nur Urlaub — das ist ein Gefühl. ✨

#VillaProvin #ProvenceMorning #MeerBlick #LuxusVilla #Vence #CotedAzur #Sonnenaufgang #TraumUrlaub #ProvenceLife #LuxuryTravel #FrankreichUrlaub #MorgenMomente #Provence #LuxuryEscapes #Fernweh""",
        "photo": "DSC_6446.jpg",
        "day": "monday",
        "time": "08:30"
    },
    {
        "title": "Salzwasser-Pool Oase",
        "caption": """Das sanfte Rauschen des Salzwasserpools, der Blick über Vence bis ans Mittelmeer. Tauche ein und spüre, wie der Alltag abfällt. Kindersicher ummauert, beheizt, unvergesslich. 💙

#VillaProvin #SalzwasserPool #ProvenceRelax #LuxusUrlaub #Vence #CotedAzur #PoolVibes #FamilienUrlaub #TraumUrlaub #LuxuryEscapes #SommerSonne #ProvenceLife #InfinityPool #MeTime #DreamVacation""",
        "photo": "DSC_6602.jpg",
        "day": "tuesday",
        "time": "13:00"
    },
    {
        "title": "Über der Matisse-Kapelle",
        "caption": """Direkt unter uns liegt ein Meisterwerk der Kunstgeschichte: die berühmte Matisse-Kapelle in Vence. Villa Provin ist dein Tor zur Provence — zur Kunst, zur Natur, zum Leben. 🎨

#VillaProvin #MatisseKapelle #Vence #KunstInProvence #CotedAzur #CulturalTravel #ChapelleDuRosaire #ProvenceLife #LuxuryTravel #Matisse #FrenchRiviera #ArtHistory #MustVisit #SecretPlaces""",
        "photo": "DSC_6446.jpg",
        "day": "sunday",
        "time": "10:00"
    },
    {
        "title": "Aktiv in der Provence",
        "caption": """Morgens Peloton Bike, mittags Rad durch die provenzalischen Hügel, nachmittags im Salzwasserpool. Die Wanderwege beginnen direkt vor der Haustür. Dein Körper, dein Geist, deine Provence. 💪

#VillaProvin #PelotonBike #WellnessReise #WandernProvence #LuxuryFitness #Vence #CotedAzur #AktivUrlaub #ProvenceAktiv #ReiseFit #MindBodySoul #LuxuryLifestyle #NaturErlebnis #FitnessUrlaub""",
        "photo": "DSC_6680.jpg",
        "day": "wednesday",
        "time": "17:00"
    },
]

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ideas"
    
    if cmd == "ideas":
        print("Erstelle Buffer Ideas für alle Posts...")
        for post in POSTS:
            idea_id = create_idea(post['title'], post['caption'])
            if idea_id:
                print(f"✅ '{post['title']}' → ID: {idea_id}")
            else:
                print(f"❌ '{post['title']}' fehlgeschlagen")
    
    elif cmd == "list":
        ideas = list_ideas()
        print(f"{len(ideas)} Ideas in Buffer:")
        for i in ideas:
            print(f"  {i['id']}: {i['content']['title']}")
    
    print("Done!")
