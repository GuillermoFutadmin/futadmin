
import json

with open('baja.json', 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)
    print(f"Total features: {len(data['features'])}")
    # Print properties of first 5 features
    for f in data['features'][:5]:
        print(f['properties'])
    
    # Search for anything related to Tijuana or Mun 4 (Tijuana is usually 004 in BC)
    tijuana_features = [f for f in data['features'] if f['properties'].get('NOMGEO') == 'Tijuana' or f['properties'].get('CVE_MUN') == '004']
    print(f"Tijuana features: {len(tijuana_features)}")
    if tijuana_features:
        print("Sample Tijuana feature properties:")
        print(tijuana_features[0]['properties'])
