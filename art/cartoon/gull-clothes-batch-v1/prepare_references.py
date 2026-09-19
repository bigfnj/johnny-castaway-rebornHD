"""Copy exact GJGULL2 originals and create nearest-neighbor viewing references."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INV = HERE.parent / 'character-inventory-v1'
RESOURCE = 'GJGULL2.BMP'
FRAMES = list(range(6)) + list(range(16,49))
POSES = {
0:'Curved support stick with sparse white motion/cloth-detail strokes beside its upper-left end; no bird or human anatomy. Retain the original arc and separate strokes.',
1:'Bare curved stick, tip at upper-right and thicker base at lower-left; preserve its bowed contour, with no hanging cloth or bird.',
2:'Small left-facing crouched gull, lowered neck and compact folded wings; feet beneath body.',
3:'More upright left/three-quarter gull, raised neck and visible feet; preserve head and eye visibility rather than copying a pure profile.',
4:'Low flattened clothes bundle, folded white/gray cloth with a dark inner fold and ragged projecting end; not a hat-only or boat drawing.',
5:'Gull reaching sharply down-left with long lowered neck and rump/tail high right; preserve both feet and the long diagonal pose.',
16:'Elongated folded clothes bundle angled from lower-left toward upper-right, with openings and layered cloth folds. Keep its narrow diagonal silhouette.',
17:'White ragged clothes hanging at the upper-left tip of a long curved stick that bows down-right. Source tag30 names clothes on stick. No human limbs or bird.',
18:'Preening gull with a folded wing/head overlap toward the left, partly open beak and contact shadow below; do not turn shadow into a foot.',
19:'Separate preening phase close to018, with changed mouth/wing details and contact shadow; retain the original differences.',
20:'More upright preening phase, beak open and wing alongside head; feet and soft gray contact shadow below.',
21:'Standing left-facing gull with slightly lowered head and compact folded wings; low tail extends right.',
22:'Very low flattened left-facing gull with head above body and low tail to right; keep the settling posture, not an upright stand.',
23:'Higher standing left-facing gull with raised neck, folded wing and visible feet; separate from021.',
24:'Lowered left-facing head and flattened body, stretched toward the left with low tail right; do not raise its neck.',
25:'Gull turning toward viewer/left, rounded front chest and stepping feet; original controls visible eye count.',
26:'Near-frontal compact gull, broad chest, head above short body and two stepping feet. Preserve frontal eye/beak relationship.',
27:'Right-facing flying gull with both wings raised; long clothes bundle lies diagonally below its body, attached at the beak.',
28:'Right-facing gull with lowered wings; folded clothes bundle extends diagonally below-left. Preserve wing-versus-cloth boundaries.',
29:'Right-facing gull with broadly spread nearly horizontal wings and clothes suspended diagonally below-left.',
30:'Right-facing flying gull with spread/slightly raised wings and hanging clothes drawn vertically beneath its beak at right.',
31:'Right-facing gull with steep raised wings and a vertical ragged clothes bundle hanging from the beak at right.',
32:'Right-facing flying gull, raised wings and elongated clothes below-left in a shallow diagonal; distinct phase from027.',
33:'Right-facing gull in lowered-wing stroke, with clothes angled down-left beneath the beak/body.',
34:'Low clothes bundle resting flat, dark inner fold and broad white cloth flaps; preserve the irregular folded outline.',
35:'Bare bowed support stick, thin tip upper-left and thicker base lower-right. Opposite arc orientation from001; no bird or clothes.',
36:'Right-facing gull with wings lowered and ragged clothes hanging nearly vertically from its beak; preserve clear separation of feet and cloth ends.',
37:'Right-facing flying gull in strong asymmetric wing stroke, clothes diagonal below-left; no ground shadow.',
38:'Left-facing flying gull in opposite banking view, raised wing and clothes extending below-right; do not mirror only the head.',
39:'Gull settled very low with head turned down toward its side and tail along the right; keep compressed resting silhouette.',
40:'Right-facing flying gull with wings in a steep oblique stroke and clothes below-left; original wing angles govern.',
41:'Right-facing gull in deep downstroke with large wing down at right and clothes bundle below-left.',
42:'Left-facing reverse flying pose, wing rising high to right and clothes extending below-right; retain original mirrored arrangement.',
43:'Left-facing reverse deep-downstroke pose, wide low wing and clothes bundle below-right.',
44:'Right-facing gull with wings raised and vertical clothes hanging below its beak; retain the distinct angle from031.',
45:'Small low-profile folded clothes bundle, flattened dark inner fold and thin pale edges; no bird or stick.',
46:'Front-facing flying gull carrying a compact clothes bundle beneath its beak, both wings extending down/out; preserve frontal view and eye placement.',
47:'Front-facing flying gull with wings spread widely near-horizontal, compact carried clothes below beak; do not use a side-profile face.',
48:'Front-facing flying gull with both wings high in a wide V, compact clothes below beak; preserve paired wings and frontal head.'
}
PROP_FRAMES = {0,1,4,16,17,34,35,45}

def digest(data): return hashlib.sha256(data).hexdigest()
def ident(path): return {'path':path.relative_to(ROOT).as_posix(),'sha256':digest(path.read_bytes())}
def save(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')

def main():
    index_path=INV/'source/frame-index.json'
    map_path=INV/'scene-map/resource-map.json'
    archive=INV/'reference-originals.zip'
    index=json.loads(index_path.read_text(encoding='utf-8'))
    mapping=json.loads(map_path.read_text(encoding='utf-8'))
    lookup={x['frame']:x for x in index['frames'] if x['resource']==RESOURCE}
    resource=next(x for x in mapping['resources'] if x['resource']==RESOURCE)
    assets=[]
    with zipfile.ZipFile(archive) as zipped:
        for f in FRAMES:
            item=lookup[f]
            raw=zipped.read(item['path'])
            if digest(raw)!=item['png_sha256']: raise ValueError('Original PNG hash differs: '+item['id'])
            original=HERE/f'reference/original/{RESOURCE}/{f:03}.png'
            nearest=HERE/f'reference/nearest8/{RESOURCE}/{f:03}.png'
            original.parent.mkdir(parents=True,exist_ok=True)
            nearest.parent.mkdir(parents=True,exist_ok=True)
            original.write_bytes(raw)
            with Image.open(io.BytesIO(raw)) as im:
                im.resize((im.width*8,im.height*8),Image.Resampling.NEAREST).save(nearest)
            actions=[{k:a[k] for k in ('ttm','tag','description','scope')} for a in resource['unique_slot_frame_actions'] if f in a['frames']]
            assets.append({'id':item['id'],'resource':RESOURCE,'frame':f'{f:03}','canvas':item['canvas'],'visible_bounds_exclusive':item['visible_bounds_exclusive'],'archive_member':item['path'],'original':ident(original),'nearest8':ident(nearest),'source_rgba_sha256':item['rgba_sha256'],'source_index_plane_sha256':item['index_plane_sha256'],'pose':POSES[f],'bird_count':0 if f in PROP_FRAMES else 1,'content':'prop only' if f in PROP_FRAMES else ('gull and clothes' if f>=27 and f!=39 else 'gull'),'static_frame_attribution':actions})
    sheets=[]
    for page,start in enumerate(range(0,len(assets),16),1):
        rows=assets[start:start+16]
        sheet=Image.new('RGB',(1280,((len(rows)+3)//4)*240),(225,231,235));draw=ImageDraw.Draw(sheet)
        for n,row in enumerate(rows):
            with Image.open(ROOT/row['original']['path']) as source:
                im=source.convert('RGBA');s=max(1,min(8,300//im.width,200//im.height));im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST)
                sheet.paste(im,(n%4*320+(320-im.width)//2,n//4*240+32+(200-im.height)//2),im)
            draw.text((n%4*320+8,n//4*240+8),f"{RESOURCE} {row['frame']} {row['canvas']}",fill='black')
        path=HERE/f'reference/{RESOURCE}-contact-{page:02}.png';sheet.save(path);sheets.append(ident(path))
    shared={'archive':ident(archive),'frame_index':ident(index_path),'scene_map':ident(map_path),'preparation':ident(Path(__file__)),'supplied_original_resource_sha256':index['source']['resource_sha256']}
    clothing=ROOT/'art/cartoon/standing018-proportions-v1/018-foot-v5.png'
    gull=ROOT/'art/cartoon/gulls-fish-batch-v1/generation/GJGULL1.BMP/009-generated-v1.png'
    identity={'clothing':ident(clothing),'gull':ident(gull),'guidance':'Established Johnny wears white ragged shorts; use pale cloth, subdued cool-gray folds and black outline. Original bundle/hanging/attachment geometry remains authoritative. Do not invent skin, limbs, a shirt or a cap-only substitute. The generated bird key controls materials, never per-frame pose.'}
    record={'schema_version':1,'scope':'39 exact GJGULL2 original drawings prepared for new Cartoon art; no generation or approval','count':len(assets),'excluded_markers':list(range(6,16)),'palette_limit':index['palette_limit'],**shared,'identity_references':identity,'contacts':sheets,'assets':assets,'semantic_note':'MJBATH tag30 is clothes on stick; tags29/31/32 describe stealing clothes, making a nest and settling. Historical cap-only descriptions are too narrow.','attribution_limit':'Static source associations only, no native timing or executed reachability claim. Frame number order is not an animation loop.'}
    save(HERE/'reference/source.json',record)
    plan={'schema_version':1,'status':'Reference preparation complete; new artwork and appearance approval pending','target_new_drawings':39,'user_batch_default':[36,48],'resources':[{'resource':RESOURCE,'frames':FRAMES,'count':39,'original_resource_payload_sha256':resource['original_payload_sha256'],'story_associations':resource['ttm_load_associations']}],'source_record':ident(HERE/'reference/source.json'),**shared,'identity_references':identity,'excluded_markers':list(range(6,16)),'assignments':{'standing':[2,3,5,18,19,20,21,22,23,24,25,26,39],'props_lift':[0,1,4,16,17,27,30,31,34,35,36,44,45],'carrying_flight':[28,29,32,33,37,38,40,41,42,43,46,47,48]},'shared_cloth_key':{'resource':RESOURCE,'frame':'017','reason':'Hanging white ragged clothes with source stick and visible folded cloth attachment.','status':'planned'},'assets':assets,'approval':None,'workflow':'Original pose and geometry first, shared keys for materials. One built-in imagegen call per drawing, untouched raw copies and exact requests. Appearance review first; no runtime exports or full tests in this pass.'}
    save(HERE/'batch-plan.json',plan)
    print(f'Prepared {len(assets)} originals, nearest8 references and {len(sheets)} contact sheets.')

if __name__=='__main__': main()
