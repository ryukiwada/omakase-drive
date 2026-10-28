import json,subprocess,sys,os
# Small pilot area around central Wakayama. Overture transportation segments, not OSM tag-complete.
raw='wakayama_raw.geojson'; out='wakayama_roads.geojson'
subprocess.run([sys.executable,'-m','pip','--version'],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['overturemaps','download','--bbox=135.13,34.18,135.25,34.29','-f','geojson','--type=segment','-o',raw],check=True)
features=[]
with open(raw, 'rb') as f:
    print('RAW SAMPLE:', repr(f.read(300)), flush=True)
with open(raw,encoding='utf-8') as f:
 for line in f:
  line=line.strip().lstrip("\x1e")
  if not line:continue
  item=json.loads(line)
  if item.get('type')=='FeatureCollection': features.extend(item.get('features',[]))
  elif item.get('type')=='Feature':features.append(item)
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
