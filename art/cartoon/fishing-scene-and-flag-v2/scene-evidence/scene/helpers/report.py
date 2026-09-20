"""Read back the six native color-context stills; no rendering or asset changes."""
from pathlib import Path
import hashlib,io,json,re,shutil,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def pin(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
pattern=r'CAPTURE: frame=(\d+) display=(\d+) ticks=(\d+) flip=(\d+) x=(-?\d+) y=(-?\d+) dx=(-?\d+) dy=(-?\d+) canvas=(\d+)x(\d+) file=(\S+)'
cases=[]
with zipfile.ZipFile(ROOT/'assets/scrantic_data.zip') as z:
 for label,scale in [('hd-ttm29-seed11',1),('cartoon-ttm29-seed11',2)]:
  folder=HERE/label;log=(folder/'scene/capture.log').read_text()
  build=json.loads((folder/'build.json').read_bytes());launch=json.loads((folder/'launch.json').read_bytes());run=json.loads((folder/'run.json').read_bytes())
  assert launch['returncode']==0 and launch['no_surviving_task_container'] and launch['source_archive_unchanged']
  assert all(sha((ROOT/p).read_bytes())==s for p,s in build['compiled_source_sha256'].items())
  assert 'DONE: direct native TTM returned and cleanup complete' in log
  assert 'SETUP: direct original MJFISH.TTM tag1' in log
  assert 'TTM=MJFISH.TTM tag=29 seed=11' in log
  snapshots=folder/'helpers';snapshots.mkdir(exist_ok=True)
  for name in ('driver.c','capture.py','run.py','report.py'):
   target=snapshots/name
   if target.exists():assert target.read_bytes()==(HERE/name).read_bytes()
   else:shutil.copyfile(HERE/name,target)
  assert sha((snapshots/'driver.c').read_bytes())==build['driver_sha256']
  rows=[]
  for raw in re.findall(pattern,log):
   f,ordinal,ticks,flip,x,y,dx,dy,w,h=map(int,raw[:10]);ppm=folder/'scene'/raw[10];png=ppm.with_suffix('.png')
   original=Image.open(ppm).convert('RGB');shown=Image.open(png).convert('RGB');assert original.tobytes()==shown.tobytes()
   assert original.size==(640*scale,480*scale) and flip==1
   left,top=(x+dx)*scale,(y+dy)*scale
   row={'frame':f,'display_ordinal':ordinal,'ticks':ticks,'time_ms':ticks*20,'flip':flip,'logical_position':[x,y],'logical_scene_offset':[dx,dy],'scale':scale,'draw_canvas':[w,h],'draw_bounds_pixels':[left,top,left+w,top+h],'image':pin(png),'pixels_sha256':sha(shown.tobytes())}
   if scale==2:
    member=f'data/hd/BMP/MJFISH3.BMP/{f:03}.png';payload=z.read(member);sprite=Image.open(io.BytesIO(payload)).convert('RGBA').transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    assert f'Art asset: {member}' in log and sprite.size==(w,h)
    mismatch=0;count=0
    for yy in range(h):
     for xx in range(w):
      rgba=sprite.getpixel((xx,yy))
      if rgba[3]:
       count+=1;mismatch+=tuple(rgba[:3])!=shown.getpixel((left+xx,top+yy))
    assert mismatch==0
    box=sprite.getchannel('A').getbbox()
    row.update(fish_source={'archive':run['archive_sha256'],'member':member,'sha256':sha(payload)},opaque_source_pixels=count,opaque_source_pixel_mismatches=mismatch,fish_alpha_bounds_pixels=[left+box[0],top+box[1],left+box[2],top+box[3]])
   else:
    row['fish_source']={'archive':run['archive_sha256'],'resource':'MJFISH3.BMP','mode':'native packed-resource decode using JOHNCAST.PAL'}
    row['bounds_note']='Full native submitted sprite canvas, conservative for transparent pixels. No independent visible-pixel boundary claim.'
   rows.append(row)
  assert {r['frame'] for r in rows}=={8,9,10}
  palette=[list(map(int,r)) for r in re.findall(r'^RGB: (\d+) (\d+) (\d+) (\d+)$',log,re.M)]
  assert len(palette)==16 and palette[2]==[2,0,168,0] and palette[4]==[4,168,0,0]
  cases.append({'id':label,'style':'Original resources at native resolution' if scale==1 else 'Current Cartoon with existing HD fish fallback','archive_sha256':run['archive_sha256'],'captures':sorted(rows,key=lambda r:r['frame']),'palette_resource':'JOHNCAST.PAL','palette_rgb_by_index':palette,'palette_note':'Original resource decoding uses this actual port palette. Current Cartoon fish use the loaded HD PNG colors, verified pixel-exact in the displayed scene.','run':pin(folder/'run.json'),'launch':pin(folder/'launch.json'),'build':pin(folder/'build.json'),'log':pin(folder/'scene/capture.log'),'helpers':[pin(p) for p in sorted(snapshots.iterdir())]})
assert [[(r['frame'],r['ticks'],r['logical_position'],r['flip']) for r in c['captures']] for c in cases][0]==[[(r['frame'],r['ticks'],r['logical_position'],r['flip']) for r in c['captures']] for c in cases][1]
report={'schema_version':1,'status':'captured','scope':'Six actual native window-surface captures for fish color context. Direct original MJFISH.TTM tag1 load setup then tag29; unchanged ttmPlay and grUpdateDisplay on adsInitIsland context. Native draw positions, flips and script phase order retained.','limits':['This supplied script tag is not directly scheduled by current FISHING.ADS; not a naturally reached story-scene claim.','Static day/high-tide island fixture at0,0 with raft0,holiday0,seed11. No walking setup or animated island/cloud scheduler in direct-tag loop.','Original graphics shown through current Linux port, not the historical Windows executable. Engine palette directives are not implemented; graphicsInit uses palResources[0], JOHNCAST.PAL.','No generated Cartoon fish are integrated in these captures. Current scene uses existing HD fish fallback.','No smoke/regression matrix or bulk integration validation was run.'], 'source_findings':pin(HERE/'source-findings.json'),'source_decode':pin(HERE/'source-attribution/source-scene.json'),'private_original_archive':pin(HERE/'archive.json'),'cases':cases,'readback':{'six_PNGs_exact_to_native_PPM':True,'paired_positions_flips_ticks':True,'all_compiled_C_sources_still_exact':True,'current_fish_opaque_pixels_exact_to_loaded_HD_PNGs':True,'production_archive_unchanged':True}}
save(HERE/'selected-captures.json',report)
print(json.dumps({'report':pin(HERE/'selected-captures.json'),'cases':[{'id':c['id'],'captures':[{'frame':r['frame'],'bounds':r['draw_bounds_pixels'],'image':r['image']} for r in c['captures']]} for c in cases]},indent=2))
