import json,subprocess,sys,os
# Small pilot area around central Wakayama. Overture transportation segments, not OSM tag-complete.
raw='wakayama_raw.geojson'; out='wakayama_roads.geojson'
subprocess.run([sys.executable,'-m','pip','--version'],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['overturemaps','download','--bbox=135.13,34.18,135.25,34.29','-f','geojson','--type=segment','-o',raw],check=True)
with open(raw, encoding='utf-8') as f:
    data = json.load(f)

if data.get('type') == 'FeatureCollection':
    features = data.get('features', [])
elif data.get('type') == 'Feature':
    features = [data]
else:
    raise ValueError('Unsupported GeoJSON format')
filtered=[]
for item in features:
 g=item.get('geometry') or {}
 if g.get('type') not in ('LineString','MultiLineString'):continue
 p=item.get('properties') or {}
 road_class=p.get('class') or p.get('subtype') or ''
 # Overture classes are not OSM highway tags. Never assert lanes or width.
 filtered.append({'type':'Feature','geometry':g,'properties':{'highway':str(road_class),'name':'','lanes':'','width':'','source':'Overture Maps transportation'}})
with open(out,'w',encoding='utf-8') as f:json.dump({'type':'FeatureCollection','features':filtered},f,ensure_ascii=False,separators=(',',':'))
print('saved',len(filtered),'features',os.path.getsize(out),'bytes')
if not filtered:raise RuntimeError('No road segments returned')
if os.path.getsize(out)>12*1024*1024:raise RuntimeError('GeoJSON exceeds app 12 MB limit; reduce bounding box')
