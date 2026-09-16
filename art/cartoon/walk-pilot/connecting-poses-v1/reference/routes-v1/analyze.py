"""Source-only route analysis; compare interpretation with retained C traces.

No historical helpers or native binaries are executed by this script.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FIRST_GLIBC_SEED2 = 1505335290  # Retained profile route-plan and compiled trace evidence.


def sha(data):
    return hashlib.sha256(data).hexdigest()


def array(text, name):
    body = text.split(name, 1)[1].split('=', 1)[1].split('};', 1)[0]
    return [int(n) for n in re.findall(r'-?\d+', re.sub(r'//[^\n]*', '', body))]


data_text = (ROOT/'src/data/walk_data.h').read_text()
flat = array(data_text, 'walkData[][4]')
ROWS = [flat[n:n+4] for n in range(0, len(flat), 4)]
assert len(ROWS) == 489
BOOK = array(data_text, 'walkDataBookmarks[6][6]')
TURNS = array(data_text, 'walkDataBookmarksTurns[NUM_OF_NODES]')
START = array(data_text, 'walkDataStartHeadings[NUM_OF_NODES][NUM_OF_NODES]')
END = array(data_text, 'walkDataEndHeadings[NUM_OF_NODES][NUM_OF_NODES]')
MATRIX = array((ROOT/'src/data/calcpath_data.h').read_text(), 'walkMatrix[NUM_OF_NODES+1][NUM_OF_NODES][NUM_OF_NODES]')


def routes(a, b):
    found = []
    def visit(prev, cur, path):
        if cur == b:
            found.append(path)
            return
        for nxt in range(6):
            if MATRIX[prev*36+cur*6+nxt] and nxt not in path:
                visit(cur, nxt, path+[nxt])
    visit(6, a, [a])
    return found or [[a, b]]


def interpret(args):
    a, h, z, zh = args
    alternatives = routes(a,z)
    path = alternatives[FIRST_GLIBC_SEED2 % len(alternatives)]
    path_index = 0
    final = False
    arrived = False
    if a == z:
        nxt, nh, final = -1, zh, True
    else:
        path_index += 1
        nxt = path[path_index]
        nh = START[a*6+nxt]
    diff = (nh-h)&7
    inc = (1 if diff<4 else -1) if diff else 0
    result = []
    index = None
    for step in range(1024):
        if arrived:
            break
        if nh != -1:
            if ((nh-h)&7)>1:
                h = (h+inc)&7
                index = TURNS[a]+h+(9 if final else 0)
                role = 'final-wait-turn' if final else 'ordinary-turn'
            elif a != z:
                nh = -1
                index = BOOK[a*6+nxt]
                role = 'travel'
            else:
                index = TURNS[z]+zh+9
                arrived = True
                role = 'arrival-wait'
        else:
            index += 1
            role = 'travel'
            if not ROWS[index][1]:
                h = END[a*6+nxt]
                a = nxt
                if a != z:
                    path_index += 1
                    nxt = path[path_index]
                    nh = START[a*6+nxt]
                else:
                    nh, final = zh, True
                diff = (nh-h)&7
                inc = (1 if diff<4 else -1) if diff else 0
                h = (h+inc)&7
                index = TURNS[a]+h
                role = 'waypoint-turn'
                if final:
                    index += 9
                    role = 'arrival-wait' if h==zh else 'final-wait-turn'
                    if h==zh:
                        arrived = True
        flip,x,y,frame = ROWS[index]
        result.append({'frame':frame,'flip_x':flip,'x':x-1,'y':y,'delay_ticks':80 if arrived else 6,
                       'row':index,'spot':'ABCDEF'[a],'heading':h,'role':role})
    else:
        raise AssertionError('interpretation did not finish')
    return {'api_arguments':list(args),'selected_path':''.join('ABCDEF'[n] for n in path),
            'alternatives':[''.join('ABCDEF'[n] for n in p) for p in alternatives],
            'draws':result,'public_call_ms':20*(6+sum(r['delay_ticks'] for r in result[1:]))}


def main():
    retained_path = ROOT/'art/cartoon/walk-pilot/front-arrival-v1/trace/trace.json'
    retained = json.loads(retained_path.read_text())
    comparison = []
    for label, case in retained['native_trace']['cases'].items():
        calculated = interpret(case['api_arguments'])
        reduced = [{k:r[k] for k in ('frame','flip_x','x','y','delay_ticks')} for r in calculated['draws']]
        assert reduced == case['draws'], label
        comparison.append(label)
    groups=[]
    row_index=0
    for line_no,line in enumerate(data_text.splitlines(),1):
        m=re.fullmatch(r'\s*\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\},\s*(?://\s*(.*))?',line)
        if not m: continue
        if m[5]: groups.append({'name':m[5],'rows':[]})
        if int(m[2]) and int(m[4]) in (9,10,12):
            groups[-1]['rows'].append({'table_row':row_index,'source_line':line_no,'raw':[int(m[i]) for i in range(1,5)],'origin':[int(m[2])-1,int(m[3])]})
        row_index+=1
    table_uses=[g for g in groups if g['rows']]
    candidate_args = {
        'minimal-front-arc-DC':(3,3,2,7), 'minimal-rear-arc-DE':(3,6,4,2),
        'reverse-front-DE':(3,7,4,2), 'reverse-rear-FC':(5,3,2,6),
        'waypoint-front-DCF':(3,7,5,3), 'waypoint-rear-BAE':(1,3,4,5),
        'front-right-FC':(5,1,2,6), 'front-left-FA':(5,7,0,2),
        'rear-clockwise-FD':(5,2,3,5), 'rear-counterclockwise-FE':(5,6,4,3),
        'travel-CB':(2,1,1,1),'travel-DF':(3,1,5,1),'travel-EC':(4,7,2,6),
        'waypoint-DCA':(3,7,0,2),'waypoint-FCD':(5,6,3,4),
        'historical-AE':(0,1,4,5),
    }
    clips={name:interpret(args) for name,args in candidate_args.items()}
    for case in clips.values():
        args=case['api_arguments']
        case['prime_api_arguments']=[args[0],args[1],args[0],args[1]]
        case['including_prime_ms']=case['public_call_ms']+120
        case['target_contexts']=[{'index':i,'before':case['draws'][max(0,i-1):i], 'target':row,'after':case['draws'][i+1:i+2]} for i,row in enumerate(case['draws']) if row['frame'] in (9,10,12)]
    waypoints=[]
    for prev in range(6):
        for cur in range(6):
            for nxt in range(6):
                if BOOK[prev*6+cur]<0 or not MATRIX[prev*36+cur*6+nxt]: continue
                before_h=END[prev*6+cur]
                after_h=START[cur*6+nxt]
                d=(after_h-before_h)&7
                increment=(1 if d<4 else -1) if d else 0
                h=(before_h+increment)&7
                heads=[h]
                while ((after_h-h)&7)>1:
                    h=(h+increment)&7
                    heads.append(h)
                row_ids=[TURNS[cur]+h for h in heads]
                if any(ROWS[r][3] in (9,10,12) for r in row_ids):
                    waypoints.append({'context':''.join('ABCDEF'[n] for n in (prev,cur,nxt)), 'inbound_heading':before_h,'outbound_heading':after_h,
                                      'ordinary_turn_rows':[{'row':r,'raw':ROWS[r]} for r in row_ids]})
    ttms=[r for r in retained['port_ttm_draw_uses'] if r['frame'] in (9,10,12)]
    with zipfile.ZipFile(ROOT/'assets/scrantic_data.zip') as zf:
        inventory=json.loads((ROOT/'docs/knowledge-base/port-inventory.json').read_text())
        assert sha(zf.read('data/RESOURCE.MAP'))==inventory['inputs']['port_map_sha256']
        assert sha(zf.read('data/RESOURCE.001'))==inventory['inputs']['port_volume_sha256']
    source_names=['src/engine/walk.c','src/engine/calcpath.c','src/data/walk_data.h','src/data/calcpath_data.h','src/engine/ads.c','src/engine/events.c','src/engine/graphics.c']
    source_records=[]
    for name in source_names:
        data=(ROOT/name).read_bytes()
        lf=sha(data.decode().replace('\r\n','\n').replace('\r','\n').encode())
        old=retained['source_lf_sha256'].get(name)
        if old is not None: assert old==lf,name
        source_records.append({'path':name,'sha256':sha(data),'lf_sha256':lf,'matches_retained_trace_source':old==lf if old else None})
    result={'schema_version':1,'commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
            'scope':'Read-only source interpretation checked against all116 preserved actual-C traces. No new native C execution/rendering or original binary timing claim.',
            'retained_trace':{'path':retained_path.relative_to(ROOT).as_posix(),'sha256':sha(retained_path.read_bytes()),'cases_matched':len(comparison)},
            'source_records':source_records,'baseline_archive_sha256':sha((ROOT/'assets/scrantic_data.zip').read_bytes()),
            'table_uses':table_uses,'permitted_waypoint_target_contexts':waypoints,'candidate_clips':clips,
            'seed2_direct_routes':{''.join('ABCDEF'[n] for n in (a,b)):[''.join('ABCDEF'[n] for n in p) for p in routes(a,b)] for a in range(6) for b in range(6) if a!=b and routes(a,b)[FIRST_GLIBC_SEED2%len(routes(a,b))]==[a,b]},
            'ttm_draw_uses':ttms,'ttm_counts_by_frame':dict(Counter(str(r['frame']) for r in ttms)),
            'ttm_limit':retained['script_attribution_limit'],'original_ttm_limit':retained['original_port_limit']}
    (OUT/'route-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Retained actual-C cases matched:',len(comparison))
    for name,c in clips.items():
        leading=' '.join(f"{r['frame']:03}{'m' if r['flip_x'] else ''}" for r in c['draws'][:6])
        print(name,c['api_arguments'],c['selected_path'],'draws',len(c['draws']),'ms',c['including_prime_ms'],'lead',leading,'targets',[(r['index'],r['target']['frame'],r['target']['role']) for r in c['target_contexts']])
    print('DIRECT',result['seed2_direct_routes'])
    print('WAYPOINTS',json.dumps(waypoints))


if __name__=='__main__': main()
