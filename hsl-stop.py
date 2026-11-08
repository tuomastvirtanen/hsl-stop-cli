#!/usr/bin/env python3
# HSL:n aikataulut pysäkkikohtaisesti
import sys
import urllib.request
import json
import time
from pathlib import Path

SECRETS_FILE = Path(__file__).resolve().parent / "api-secrets.txt"

def get_api_key():
    with SECRETS_FILE.open(encoding="utf-8") as f:
        return f.readline().strip()

def get_stops_by_name(stop_name):
    """Hakee pysäkit nimen osalla."""
    url = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
    query = """
    {
      stops(name: "%s") {
        name
        code
        stoptimesWithoutPatterns {
          realtimeArrival
          realtime
          serviceDay
          trip {
            routeShortName
            tripHeadsign
          }
        }
      }
    }
    """ % stop_name
    return exec_query(url, query, "stops")

def get_stops_by_code(stop_code):
    """Hakee pysäkin tarkan koodin perusteella."""
    url = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
    query = """
    {
      stopsByCodes(codes: ["%s"]) {
        name
        code
        stoptimesWithoutPatterns {
          realtimeArrival
          realtime
          serviceDay
          trip {
            routeShortName
            tripHeadsign
          }
        }
      }
    }
    """ % stop_code
    return exec_query(url, query, "stopsByCodes")

def exec_query(url, query, field_name):
    hdr = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'digitransit-subscription-key': get_api_key(),
        'User-Agent': 'HSL-Stop-CLI/1.0'
    }
    data = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=hdr)
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            return res_json.get("data", {}).get(field_name, [])
    except Exception as e:
        print(f"Virhe yhteydessä: {e}", file=sys.stderr)
        return []

def print_stop_data(stop):
    """Tulostaa yksittäisen pysäkin aikataulurivit."""
    print(f"\nPysäkki: {stop['name']} ({stop.get('code', 'Ei koodia')})")
    print("-" * 45)
    
    stoptimes = stop.get("stoptimesWithoutPatterns", [])
    if not stoptimes:
        print("  Ei tulevia linjoja lähiaikoina.")
        return
        
    for st in stoptimes[:5]:
        trip = st.get("trip", {}) if st.get("trip") else {}
        line = trip.get("routeShortName", "???")
        dest = trip.get("tripHeadsign", "Tuntematon")
        
        arrival_time = time.strftime("%H:%M", time.localtime(st["serviceDay"] + st["realtimeArrival"]))
        is_live = "•" if st["realtime"] else " "
        
        print(f"  {arrival_time} {is_live} | {line:<5} -> {dest}")

def main():
    if len(sys.argv) < 2:
        print("Käyttö: python3 -m hsl-stop <pysäkin_nimi_tai_koodi>")
        sys.exit(1)

    # Otetaan koko argumentti talteen (tukee myös välilyöntejä, jos syöte on sitaateissa)
    search_term = " ".join(sys.argv[1:]).strip()
    
    # Päätellään haetaanko koodilla vai nimellä
    # Jos syöte on pelkkä numero tai alkaa H-kirjaimella ja loppu on numeroa, se on koodi
    is_code = search_term.isdigit() or (search_term.upper().startswith('H') and search_term[1:].isdigit())

    if is_code:
        code = search_term.upper()
        if code.isdigit():
            code = f"H{code}"
        stops = get_stops_by_code(code)
    else:
        stops = get_stops_by_name(search_term)

    if not stops:
        print(f"Hakusanalla '{search_term}' ei löytynyt pysäkkejä.")
        sys.exit(1)

    # Tulostetaan kaikkien löytyneiden pysäkkien tiedot
    for stop in stops:
        print_stop_data(stop)
    print()

if __name__ == "__main__":
    main()
