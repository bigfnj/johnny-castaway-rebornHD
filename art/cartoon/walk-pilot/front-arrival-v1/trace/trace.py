"""Trace front wait/turn scope from original rows, production C and script inventory.

No rendering or artwork generation. Requires an existing decoder probe and the
supplied original installation; only trace.json is written beside this script.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import zipfile

FAMILY = {0, 3, 9, 10, 12, 15, 16, 17, 18, 23}
HEADINGS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
IMAGE = 'johnny-platform-cleanup:latest'
GLUE = r'''
#include <stdio.h>
#include <stdlib.h>
#include "mytypes.h"
#include "graphics.h"
#include "walk.h"
#include "art_style.h"
static int xx, yy, ff, flip;
static struct TTtmSlot *actor;
const TArtStyle *artStyleCurrent(void) { static TArtStyle style={"hd","HD","",2,1}; return &style; }
int zipvfs_exists(const char *p) { (void)p; return 0; }
void grClearScreen(PlatformSurface *s) { (void)s; }
void grDrawSprite(PlatformSurface *s, struct TTtmSlot *t, int x, int y, uint16 f, uint16 b) {
    (void)s; (void)b; if(t==actor){xx=x;yy=y;ff=f;flip=0;}
}
void grDrawSpriteFlip(PlatformSurface *s, struct TTtmSlot *t, int x, int y, uint16 f, uint16 b) {
    grDrawSprite(s,t,x,y,f,b); if(t==actor)flip=1;
}
void grDrawSpriteAtop(PlatformSurface *s, struct TTtmSlot *t, int x, int y, uint16 f, uint16 b) {
    (void)s;(void)t;(void)x;(void)y;(void)f;(void)b;
}
int main(int argc,char **argv){
    if(argc!=6)return 2;
    struct TTtmSlot slot={0},bg={0}; struct TTtmThread thread={0};
    thread.ttmSlot=&slot; actor=&slot; srand((unsigned)atoi(argv[5]));
    walkInit(atoi(argv[1]),atoi(argv[2]),atoi(argv[3]),atoi(argv[4]));
    for(int n=0;n<1024;n++){
        uint16 delay=walkAnimate(&thread,&bg);
        if(!delay)return 0;
        printf("%d %d %d %d %d\n",ff,flip,xx,yy,delay);
    }
    return 3;
}
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def lfsha(data):
    return sha(data.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').encode())


def native():
    root = Path('/src')
    with tempfile.TemporaryDirectory(prefix='front-arrival-trace-') as temp:
        work = Path(temp)
        source, binary = work / 'driver.c', work / 'trace'
        source.write_text(GLUE)
        command = ['gcc', '-O0', '-I/src/src/engine', '-I/src/platform', '-I/src/src/data',
                   str(source), '/src/src/engine/walk.c', '/src/src/engine/calcpath.c',
                   '/src/src/engine/utils.c', '-o', str(binary)]
        built = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if built.returncode:
            raise RuntimeError(built.stderr)
        cases = {}
        requests = [(f'wait-{chr(65+n)}-{h}', n, h, n, h) for n in range(6) for h in range(8)]
        requests += [(f'A-turn-{a}-{b}', 0, a, 0, b) for a in range(8) for b in range(8)]
        requests += [('E-to-A',4,1,0,1),('A-to-E',0,1,4,5),('C-to-B',2,1,1,1),('E-to-F',4,7,5,7)]
        for label, a, ah, b, bh in requests:
            run = subprocess.run([str(binary),str(a),str(ah),str(b),str(bh),'2'], capture_output=True, text=True, timeout=3)
            if run.returncode: raise RuntimeError(label + run.stderr)
            rows = [list(map(int,line.split())) for line in run.stdout.splitlines()]
            cases[label] = {'api_arguments':[a,ah,b,bh], 'glibc_seed':2,
                            'draws':[dict(zip(('frame','flip_x','x','y','delay_ticks'),r)) for r in rows]}
        print(json.dumps({'method':'Compiled untouched walk.c + calcpath.c + utils.c; draw-call observers replace rendering only. Actual delays are returns from walkAnimate, not display-event timestamps.',
                          'glue_sha256':sha(GLUE.encode()), 'executable_sha256':sha(binary.read_bytes()),
                          'compiler_stderr':built.stderr, 'cases':cases}))


def rows_and_groups(root):
    rows, groups = [], []
    for number,line in enumerate((root/'src/data/walk_data.h').read_text().splitlines(),1):
        match = re.fullmatch(r'\s*\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\},\s*(?://\s*(.*))?',line)
        if not match: continue
        values = list(map(int,match.groups()[:4]))
        if match[5]: groups.append({'label':match[5], 'rows':[]})
        row={'row':len(rows),'source_line':number,'raw':values,'frame':values[3],
             'flip_x':bool(values[0]),'x':values[1]-1,'y':values[2]}
        rows.append(row)
        if values[1]: groups[-1]['rows'].append(row)
    assert len(rows)==489
    return rows,groups


def ttm_uses(resources, probe, inventory, original=False):
    # Static linear binding attribution; no claim to execute all branch paths.
    from inventory_scenes import metadata, decode
    result=[]
    for resource in resources.values():
        if resource['type']!='TTM': continue
        metadata(resource)
        decode(resource,probe)
        expected=next(r for r in inventory['original_resources' if original else 'port_resources'] if r['name']==resource['name'])
        assert resource['decoded_sha256']==expected['decoded_sha256'],resource['name']
        bindings,selected,delay={},0,None
        tags={r['id']:r['description'] for r in resource['tags']}
        for c in resource['_commands']:
            op,args=c['command'],c['args']
            if op=='SET_BMP_SLOT': selected=args[0]
            elif op=='LOAD_IMAGE': bindings[selected]=args[0]
            elif op=='SET_DELAY': delay=max(4,args[0])
            elif op=='TIMER': delay=(args[0]+args[1])//2
            elif op in ('DRAW_SPRITE','DRAW_SPRITE_FLIP') and bindings.get(args[3])=='JOHNWALK.BMP' and args[2] in FAMILY:
                result.append({'resource':resource['name'],'decoded_sha256':resource['decoded_sha256'],
                    'tag':c['tag'],'tag_description':tags.get(c['tag']), 'command_offset':c['offset'],
                    'command':op,'args':args,'frame':args[2],'bmp_slot':args[3],
                    'preceding_linear_delay_ticks':delay,'flip_x':op=='DRAW_SPRITE_FLIP'})
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path)
    parser.add_argument('--original-root',type=Path)
    parser.add_argument('--probe',type=Path)
    parser.add_argument('--native',action='store_true')
    args=parser.parse_args()
    if args.native: return native()
    root=args.repo.resolve()
    sys.path.insert(0,str(root/'tools'))
    from inventory_scenes import resource_catalog
    inventory=json.loads((root/'docs/knowledge-base/port-inventory.json').read_text())
    reference=json.loads((root/'art/cartoon/walk-expansion-v1/reference/source.json').read_text())
    table=(root/'src/data/walk_data.h').read_bytes()
    assert lfsha(table)==reference['walk_table_lf_sha256']
    rows,groups=rows_and_groups(root)
    exe=(args.original_root/'WINDOWS/SCRANTIC.EXE').read_bytes()
    assert sha(exe)=='7811b526b36bba2f08326d7a680f2f063190b4278e5a36393fde5a02080b0262'
    original_rows=[]
    for index in range(489):
        first,x,y=struct.unpack_from('<HHH',exe,0x188ea+index*6)
        original_rows.append([first>>15,x,y,first&32767])
    assert original_rows==[r['raw'] for r in rows]
    with zipfile.ZipFile(root/'assets/scrantic_data.zip') as archive:
        pmap,pvol=archive.read('data/RESOURCE.MAP'),archive.read('data/RESOURCE.001')
    assert sha(pmap)==inventory['inputs']['port_map_sha256'] and sha(pvol)==inventory['inputs']['port_volume_sha256']
    original_dir=args.original_root/'SIERRA/SCRANTIC'
    omap,ovol=(original_dir/'RESOURCE.MAP').read_bytes(),(original_dir/'RESOURCE.001').read_bytes()
    assert sha(omap)==inventory['inputs']['original_map_sha256'] and sha(ovol)==inventory['inputs']['original_volume_sha256']
    port=resource_catalog(pmap,pvol)[1]
    original=resource_catalog(omap,ovol)[1]
    uses=ttm_uses(port,args.probe.resolve(),inventory)
    original_uses=ttm_uses(original,args.probe.resolve(),inventory,True)
    pack=json.loads((root/'art/cartoon/pack.json').read_text())
    accepted={r['path']:r for r in pack['assets']}
    catalog=json.loads((root/'docs/knowledge-base/cartoon-production-catalog.json').read_text())
    families=[]
    for frame in sorted(FAMILY):
        path=f'BMP/JOHNWALK.BMP/{frame:03}.png'
        asset=next(a for a in catalog['assets'] if a['path']==path)
        families.append({'frame':frame,'path':path,'runtime_canvas':asset['runtime_canvas'],
                         'status':'already-approved' if path in accepted else 'needs-new-art',
                         'acceptance':accepted.get(path,{}).get('review'),
                         'original_xpm_sha256':reference['xpm_sha256'][f'{frame:03}']})
    wait_turn=[g for g in groups if g['label'].endswith((' turn',' wait'))]
    for group in wait_turn:
        for h,row in enumerate(group['rows']): row['heading']=h; row['heading_name']=HEADINGS[h]
    image_id=subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()
    run=subprocess.run(['docker','run','--rm','--network','none','--mount',f'type=bind,source={root.as_posix()},target=/src,readonly',
                        IMAGE,'python3','/src/build/front-arrival/trace/trace.py','--native'],capture_output=True,text=True,timeout=45)
    assert run.returncode==0,run.stderr
    native_trace=json.loads(run.stdout)
    ea=native_trace['cases']['E-to-A']['draws']
    assert len(ea)==24 and ea[-1]=={'frame':17,'flip_x':1,'x':293,'y':243,'delay_ticks':80}
    assert ea[-2]=={'frame':27,'flip_x':0,'x':300,'y':242,'delay_ticks':6}
    for group in wait_turn:
        if group['label'].endswith(' wait'):
            node=group['label'][0]
            for row in group['rows']:
                observed=native_trace['cases'][f'wait-{node}-{row["heading"]}']['draws']
                assert observed==[{'frame':row['frame'],'flip_x':int(row['flip_x']),'x':row['x'],'y':row['y'],'delay_ticks':80}]
    story=[{k:v for k,v in s.items() if k in ('scene','source','description','start_spot','start_heading','end_spot','end_heading','day','flags')}
           for s in inventory['story_entries'] if s['start_heading'] in ('HDG_SW','HDG_SE') or s['end_heading'] in ('HDG_SW','HDG_SE')]
    associated=[{'scene':s['scene'],'description':s['description'],'ttm_references':[r for r in s['ttm_references'] if any(u['resource']==r['resource'] and u['tag']==r['tag'] for u in uses)]}
                for s in inventory['ads_scenes']]
    associated=[s for s in associated if s['ttm_references']]
    sources=['src/data/walk_data.h','src/data/story_data.h','src/engine/walk.c','src/engine/calcpath.c','src/engine/ads.c','src/engine/events.c',
             'docs/knowledge-base/port-inventory.json','docs/knowledge-base/original-extractor-reference.json','art/cartoon/pack.json']
    report={'schema_version':1,'source_commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
        'scope':'Read-only table, original-byte and actual C state-machine trace. No artwork generation, runtime rendering or human approval.',
        'source_lf_sha256':{p:lfsha((root/p).read_bytes()) for p in sources},
        'archive_sha256':sha((root/'assets/scrantic_data.zip').read_bytes()),
        'original_executable_sha256':sha(exe),'original_table_offset_hex':'0x188EA','original_rows_equal':489,
        'decoder_probe_sha256':sha(args.probe.read_bytes()),'decoded_ttm_hashes_checked':{'port':41,'original':41},
        'headings':dict(enumerate(HEADINGS)),'family':families,'wait_turn_table':wait_turn,
        'frame017_table_uses':[dict(group=g['label'],**r) for g in groups for r in g['rows'] if r['frame']==17],
        'story_heading_uses':story,'port_ttm_draw_uses':uses,'original_ttm_draw_uses':original_uses,'ads_scene_associations':associated,
        'frame017_ttm_resource_counts':dict(sorted(Counter(u['resource'] for u in uses if u['frame']==17).items())),
        'source_references':{
            'same_spot_last_turn_wait_group':{'path':'src/engine/walk.c','lines':[75,112,173]},
            'ordinary_and_arrival_delays':{'path':'src/engine/walk.c','lines':[212,214]},
            'logical_draw_origin':{'path':'src/engine/walk.c','lines':[188,194]},
            'nominal_tick_milliseconds':{'path':'src/engine/events.c','lines':[217]},
            'public_walk_island_offsets':{'path':'src/engine/ads.c','lines':[1102,1107,1108,1112]}},
        'script_attribution_limit':'TTM slots/delays follow linear decoded command order, not every runtime branch. Cross-tag loads can be required; ADS associations establish static references, not whole-scene rendering parity.',
        'original_port_limit':'All decoded TTM hashes match preserved inventory. SJLEAVES original has an extra SET_DELAY0 in tag3; preceding linear delays are port semantic values, not measured original timing.',
        'native_trace':native_trace,'container_image_id':image_id,
        'timing':'walkAnimate ordinary6/arrival80 ticks; events.c multiplies by20ms. Background scheduling can introduce additional display captures. Stationary negative-direction turns may repeat the final pose for6 ticks before its80-tick hold; preserve observed behavior.',
        'placement':'Logical draw origin is stored x minus1, with y unchanged; actual drawing then adds island offsets and multiplies by style scale2. Mirrored017 uses the same asset, not a separately generated left/right PNG.',
        'review_order':['017 against supplied-original 017 and accepted adjacent front walk; then actual E-to-A 23 travel poses plus017 arrival.',
                        'Front stationary sweep heading1->7 and7->1 at A:017 and016, both mirrored orientations, retain exact per-call timing.',
                        'Actual seed2 A1->E5 departure starts010,009,003 then side walking004. New003/009/010 must form a coherent arms-free counterpart to waits000/017/016; the full ordinary heading ring also uses accepted023 and new012.',
                        'Complete eight-heading wait/turn ring: add rear012/015 and retain accepted018/023; review at A then placement spot-checks B-F.',
                        'Review selected TTM story usages separately, especially017 stationary poses and SJLEAVES; do not infer story approval from the walk API.'],
        'minimum_scopes':{'immediate_E_to_A_stop_new_frames':[17],
                          'front_hemisphere_wait_and_ordinary_turn_new_frames':[0,3,9,10,16,17],
                          'complete_eight_heading_family_new_frames':[0,3,9,10,12,15,16,17],
                          'complete_family_retained_frames':[18,23]}}
    output=root/'build/front-arrival/trace/trace.json'
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'output':'build/front-arrival/trace/trace.json','sha256':sha(output.read_bytes()),
                     'new_frames':[f['frame'] for f in families if f['status']=='needs-new-art'],
                     'frame017_uses':len(report['frame017_table_uses']),'port_ttm_uses':len(uses),
                     'actual_C_cases':len(native_trace['cases'])}))


if __name__=='__main__': main()
