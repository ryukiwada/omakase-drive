import json, subprocess, sys, os
# v0.9.4: enlarged pilot bbox covering Wakayama, Kainan, Iwade and part of Kinokawa.
# Not a municipal boundary; does not cover all of these municipalities.
BBOX='135.05,34.10,135.43,34.38'
raw='wakayama_raw.geojson'; out='wakayama_roads.geojson'
subprocess.run(['overturemaps','download',f'--bbox={BBOX}','-f','geojson','--type=segment','-o',raw],check=True)
with open(raw,encoding='utf-8') as f:
    data=json.load(f)
features=data.get('features',[]) if data.get('type')=='FeatureCollection' else ([data] if data.get('type')=='Feature' else [])
if not features: raise RuntimeError('No features in downloaded data')
filtered=[]
for item in features:
    g=item.get('geometry') or {}
    if g.get('type') not in ('LineString','MultiLineString'):continue
    p=item.get('properties') or {}
    # Overture Maps classifications are not OSM lane/width evidence.
    road_class=p.get('class') or p.get('subtype') or ''
    coords=g.get('coordinates',[])
    def compact(line):
        return [[round(float(xy[0]),5),round(float(xy[1]),5)] for xy in line if len(xy)>=2]
    if g['type']=='LineString': coords=compact(coords)
    else: coords=[compact(line) for line in coords]
    filtered.append({'type':'Feature','geometry':{'type':g['type'],'coordinates':coords},'properties':{'highway':str(road_class)}})
if not filtered:raise RuntimeError('No road lines found')
with open(out,'w',encoding='utf-8') as f:
    json.dump({'type':'FeatureCollection','features':filtered},f,ensure_ascii=False,separators=(',',':'))
size=os.path.getsize(out)
print('bbox',BBOX,'saved',len(filtered),'features',size,'bytes',flush=True)
if size>24*1024*1024:raise RuntimeError('GeoJSON exceeds 24 MB limit. Narrow BBOX or split by region; do not commit oversized file.')
