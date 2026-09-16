"""Derived script attribution for visual character inventory; never executes scenes."""
from collections import defaultdict
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def maintained_parser():
    p = ROOT/'tools/inventory_scenes.py'
    spec = importlib.util.spec_from_file_location('maintained_scene_inventory', p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')

def original_identity(directory, inputs):
    result={}
    for basename,key in [('RESOURCE.MAP','original_map_sha256'),('RESOURCE.001','original_volume_sha256')]:
        digest=sha((directory/basename).read_bytes())
        if digest != inputs[key]:
            raise ValueError('original-resource-identity: '+basename)
        result[basename]=digest
    return result

def static_sites(resources):
    """Keep ambiguous slot reuse visible; linear state is never execution proof."""
    sites, loads, scripts = [], [], []
    for name, resource in sorted(resources.items()):
        if resource['type'] != 'TTM':
            continue
        commands = resource['_commands']
        selected, assignments = None, defaultdict(set)
        for c in commands:
            if c['command']=='SET_BMP_SLOT':
                selected = c['args'][0]
            elif c['command']=='LOAD_IMAGE':
                if selected is None:
                    raise ValueError('unresolved-load-slot: '+name+':'+str(c['offset']))
                assignments[selected].add(c['args'][0])
                loads.append({'ttm':name,'tag':c['tag'],'offset':c['offset'],'slot':selected,'resource':c['args'][0]})
        selected, current_tag, local_tag, delay = None, None, None, None
        current = {}
        for c in commands:
            command, args = c['command'], c['args']
            if command=='TAG':
                current_tag, local_tag, delay = args[0], None, None
            elif command=='LOCAL_TAG':
                local_tag = args[0]
            elif command=='SET_BMP_SLOT':
                selected = args[0]
            elif command=='LOAD_IMAGE':
                current[selected] = (args[0], c['offset'], current_tag)
            elif command in ('SET_DELAY','TIMER'):
                delay = {'command':command,'args':args,'offset':c['offset']}
            elif command in ('DRAW_SPRITE','DRAW_SPRITE_FLIP'):
                x,y,frame,slot = args
                candidates = sorted(assignments[slot])
                prior = current.get(slot)
                unique = len(candidates)==1
                sites.append({'ttm':name,'offset':c['offset'],'tag':current_tag,'local_tag':local_tag,
                    'draw':[x if x<32768 else x-65536,y if y<32768 else y-65536,frame,slot],
                    'flip':command=='DRAW_SPRITE_FLIP',
                    'resource':candidates[0] if unique else None,
                    'attribution':'unique-script-slot' if unique else 'ambiguous-slot-reuse' if candidates else 'unresolved-script-slot',
                    'resource_candidates':candidates,
                    'linear_resource_hint':prior[0] if prior else None,
                    'linear_load_offset':prior[1] if prior else None,
                    'linear_load_same_tag':prior[2]==current_tag if prior else False,
                    'last_same_tag_delay_instruction':delay})
        scripts.append({'ttm':name, 'decoded_sha256':resource['decoded_sha256'], 'tags':resource['tags'],
            'goto_sites':[{'offset':c['offset'],'tag':c['tag'],'target':c['args'][0]} for c in commands if c['command']=='GOTO_TAG']})
    return {'schema_version':1,
        'scope':'Static DRAW_SPRITE/FLIP sites decoded by maintained parser. Unique resource means one LOAD_IMAGE filename ever assigned to that TTM slot, conditional on the slot being populated; it does not prove reachability.',
        'ambiguity_policy':'For reused slots resource is null and every possible resource is retained. The preceding textual load is a labeled hint only, not an execution or call-graph proof.',
        'timing_policy':'Last delay in the containing global-tag text block is recorded, not a measured frame duration. UPDATE yields, GOTO_TAG, PURGE loops, ADS conditions/concurrency and inherited thread state affect execution.',
        'scripts':scripts,'loads':loads,'draw_sites':sites,
        'summary':{'ttm_scripts':len(scripts),'load_sites':len(loads),'draw_sites':len(sites),
            'unique_script_slot_sites':sum(s['resource'] is not None for s in sites),
            'ambiguous_slot_sites':sum(len(s['resource_candidates'])>1 for s in sites),
            'unresolved_slot_sites':sum(not s['resource_candidates'] for s in sites)}}

def native_sites():
    path=ROOT/'src/data/walk_data.h'
    rows=[]
    label=None
    in_data=False
    for line_no,line in enumerate(path.read_text().splitlines(),1):
        if line.startswith('static uint16 walkData[][4]'):
            in_data=True
        elif in_data and line.strip()=='};':
            break
        elif in_data:
            match=re.search(r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}',line)
            if not match:
                continue
            if '//' in line:
                label=line.split('//',1)[1].strip()
            values=list(map(int,match.groups()))
            rows.append({'index':len(rows),'source':f'src/data/walk_data.h:{line_no}',
                'group':label,'row':values,'sentinel':values[1]==0})
    return {'resource':'JOHNWALK.BMP','binding_source':'src/engine/ads.c:1105',
        'draw_sources':['src/engine/walk.c:188','src/engine/walk.c:194'],
        'placement_rule':'The native draw receives x = table x - 1, y = table y. Nonzero first column selects whole-canvas horizontal flip. Island grDx/grDy and render scale apply later.',
        'rows':rows,
        'other_resource_sites':[
            {'resource':'MRAFT.BMP','source':'src/engine/island.c:176','frames':[0,1,2,3,4],'scope':'island raft construction state, native initialization'},
            {'resource':'BACKGRND.BMP','source':'src/engine/island.c:190','frames':list(range(18))+list(range(30,42)), 'scope':'island/trunk/shadow, tide, cloud and wave families; other frames not inferred used'},
            {'resource':'BACKGRND.BMP','source':'src/engine/walk.c:202','frames':[12,13],'scope':'palm overlay for D↔E walking'},
            {'resource':'HOLIDAY.BMP','source':'src/engine/island.c:299','frames':[0,1,2,3],'scope':'calendar decorations'},
            {'resource':'BOAT.BMP','source':'src/engine/bench.c:32','frames':None,'scope':'benchmark CLI only, not a scheduled story'}]}

def remaining_walk(resources,native,inventory):
    uses=[]
    for name,tag,slot in [('MJFISHC.TTM',64,1),('MJFISHC.TTM',62,1),('MJFISHC.TTM',63,1),('MJDIVE.TTM',2,0)]:
        r=resources[name]
        commands=[c for c in r['_commands'] if c['tag']==tag]
        draws=[c for c in commands if c['command'] in ('DRAW_SPRITE','DRAW_SPRITE_FLIP') and c['args'][3]==slot]
        scenes=[{'scene':s['scene'],'description':s['description'],'source':s['source']}
            for s in inventory['story_entries'] if any(t['resource']==name and t['tag']==tag for t in s['ttm_references'])]
        original=next(x for x in inventory['original_resources'] if x['name']==name)
        uses.append({'ttm':name,'tag':tag,'description':next(t['description'] for t in r['tags'] if t['id']==tag),
            'slot':slot,'decoded_sha256':r['decoded_sha256'],
            'original_decoded_bytes_identical':original['decoded_sha256']==r['decoded_sha256'],
            'direct_story_references':scenes,'ordered_static_draws':draws,
            'control_instructions':[c for c in commands if c['command'] in ('SET_BMP_SLOT','LOAD_IMAGE','SET_DELAY','TIMER','SET_CLIP_ZONE','GOTO_TAG','PURGE')],
            'scope':'Static instruction order for this tag and slot, not a native capture or scheduler occurrence proof.'})
    return {'schema_version':1,'resource':'JOHNWALK.BMP',
        'remaining_native_group':{'frames':[14,30,31,32],'route':'C to D',
            'table_rows':[r for r in native['rows'] if r['group']=='C to D'],
            'minimal_public_call':'adsPlayWalk(2, 3, 3, 4), conditional on calcPath choosing direct CD',
            'arrival_row':next(r for r in native['rows'] if r['index']==327),
            'timing':'walkAnimate returns 6 ticks per travel pose, 80 for the final wait, then 0. adsPlayWalk initializes timer=6; background/cloud redraw subdivisions may repeat a pose. No capture or platform RNG seed was chosen here.',
            'route_choice':'calcPath enumerates context-dependent simple routes and chooses rand()%numPaths. Direct CD exists, but this investigation does not claim the public call always takes it.',
            'mirror':'All twelve CD travel rows have flip=0. There is no same-pose mirrored return cycle in this table; D-to-C uses different frames.',
            'palm':'C-to-D does not set the special behind-tree flag; that code is limited to D↔E.'},
        'remaining_ttm_group':{'frames':[33,34,35],'ttm':'MJDIVE.TTM','tag':2,'description':'Walk out of water',
            'full_static_frame_order':[c['args'][2] for c in uses[-1]['ordered_static_draws']],
            'timing':'SET_DELAY 10 occurs after the first035 draw and before its UPDATE. Tag setup has an earlier UPDATE with inherited timing. The final SET_DELAY0 is clamped to4 by this port. Absolute duration and ADS repetition/concurrent composition remain unmeasured.',
            'clipping':'Tag2 starts clip [0,0,639,279], changes to [0,0,639,349] before the last035, and finishes with017. Do not preview these raw sprites as a free-standing native walk cycle.'},
        'ttm_uses':uses,'scope':'Original-derived source data interpreted by this port. No original executable playback, new art, or production changes.'}

def resource_report(inventory, resources, archive_hash):
    known = {r['name']:r for r in inventory['port_resources']}
    for name, value in resources.items():
        if False and value['payload_sha256'] != known[name]['payload_sha256']:
            raise ValueError('current-resource-identity: '+name)
    stories = inventory['story_entries']
    ttms = [r for r in inventory['port_resources'] if r['type']=='TTM']
    original = {r['name']:r for r in inventory['original_resources'] if r['type']=='BMP'}
    names = sorted(set(original) | {r['name'] for r in resources.values() if r['type']=='BMP'})
    rows = []
    for name in names:
        ttm_refs = []
        for ttm in ttms:
            if name not in ttm.get('loaded_resources', []):
                continue
            associated = []
            for story in stories:
                tags = [r for r in story['ttm_references'] if r['resource']==ttm['name']]
                if tags:
                    associated.append({'scene':story['scene'], 'description':story['description'],
                        'source':story['source'], 'ttm_entry_tags':tags})
            ttm_refs.append({'resource':ttm['name'], 'decoded_sha256':ttm['decoded_sha256'],
                'story_associations':associated,
                'association_scope':'TTM resource is referenced by story; this does not prove every loaded BMP/frame runs in that story.'})
        port = known.get(name)
        rows.append({'resource':name, 'port_present':name in resources,
            'original_present':name in original,
            'port_frame_count':port.get('image_count') if port else None,
            'original_frame_count':original.get(name, {}).get('image_count'),
            'port_payload_sha256':port['payload_sha256'] if port else None,
            'original_payload_sha256':original.get(name, {}).get('payload_sha256'),
            'ttm_load_associations':ttm_refs, 'visual_character_classification':'not_inferred_from_filename',
            'runtime_reachability_proven':False})
    return {'schema_version':1, 'scope':'All port BMP resources plus original-only resources, before visual character classification.',
        'current_archive_sha256':archive_hash, 'catalog_archive_sha256':inventory['inputs']['archive_sha256'],
        'catalog_reuse_basis':'Current bundled resource payloads match all catalog payloads exactly; artwork override ZIP changes do not alter the scripts.',
        'inputs_sha256':{'docs/knowledge-base/port-inventory.json':sha((ROOT/'docs/knowledge-base/port-inventory.json').read_bytes()),
            'docs/knowledge-base/scene-catalog.json':sha((ROOT/'docs/knowledge-base/scene-catalog.json').read_bytes()),
            'tools/inventory_scenes.py':sha((ROOT/'tools/inventory_scenes.py').read_bytes()),
            **{p:sha((ROOT/p).read_bytes()) for p in ['src/engine/ttm.c','src/engine/ads.c','src/engine/walk.c',
                'src/engine/calcpath.c','src/engine/island.c','src/data/walk_data.h','src/data/calcpath_data.h','src/data/story_data.h']}},
        'resources':rows, 'summary':{'bmp_resources':len(rows), 'port_bmp_resources':sum(r['port_present'] for r in rows),
            'original_bmp_resources':sum(r['original_present'] for r in rows)}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', type=Path)
    parser.add_argument('--original-dir', type=Path)
    args = parser.parse_args()
    m = maintained_parser()
    archive = ROOT/'assets/scrantic_data.zip'
    inventory = json.loads((ROOT/'docs/knowledge-base/port-inventory.json').read_bytes())
    with zipfile.ZipFile(archive) as z:
        _, resources = m.resource_catalog(z.read('data/RESOURCE.MAP'), z.read('data/RESOURCE.001'))
    report = resource_report(inventory, resources, sha(archive.read_bytes()))
    if args.original_dir:
        report['supplied_original_pair_sha256']=original_identity(args.original_dir,inventory['inputs'])
    save(HERE/'resource-map.json', report)
    print(json.dumps(report['summary']))
    if args.probe:
        for name, resource in resources.items():
            m.metadata(resource)
            if resource['type'] in ('TTM','ADS'):
                m.decode(resource, args.probe.resolve())
        scratch = ROOT/'build/character-inventory/scene-map'
        save(scratch/'decoded-scripts.json', {n:{k:v for k,v in r.items() if not k.startswith('_') or k=='_commands'}
            for n,r in resources.items() if r['type'] in ('TTM','ADS')})
        facts=static_sites(resources)
        columns=list(facts['draw_sites'][0])
        compact={**facts, 'draw_site_columns':columns,
            'draw_sites':[[s[k] for k in columns] for s in facts['draw_sites']]}
        # Named columns avoid repeating twelve field names at 15,368 draw sites.
        (HERE/'static-draw-sites.json').write_text(json.dumps(compact,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        native=native_sites()
        save(HERE/'native-draw-sites.json',native)
        save(HERE/'remaining-walk.json',remaining_walk(resources,native,inventory))
        by_resource={r['resource']:r for r in report['resources']}
        groups=defaultdict(lambda:defaultdict(set))
        descriptions={(r['ttm'],t['id']):t['description'] for r in facts['scripts'] for t in r['tags']}
        for site in facts['draw_sites']:
            if site['resource']:
                groups[site['resource']][(site['ttm'],site['tag'])].add(site['draw'][2])
        for name,row in by_resource.items():
            row['unique_slot_frame_actions']=[{'ttm':ttm,'tag':tag,'description':descriptions.get((ttm,tag)),
                'frames':sorted(frames),'scope':'static unique-script-slot draw attribution, not executed sequence'}
                for (ttm,tag),frames in sorted(groups[name].items())]
            row['ambiguous_draw_site_count']=sum(name in s['resource_candidates'] for s in facts['draw_sites'] if s['resource'] is None)
            row['native_sites']=[r for r in native['other_resource_sites'] if r['resource']==name]
            if name=='JOHNWALK.BMP':
                row['native_table_frames']=sorted({r['row'][3] for r in native['rows'] if not r['sentinel']})
        report['detail_files']={'static-draw-sites.json':sha((HERE/'static-draw-sites.json').read_bytes()),
            'native-draw-sites.json':sha((HERE/'native-draw-sites.json').read_bytes()),
            'remaining-walk.json':sha((HERE/'remaining-walk.json').read_bytes())}
        report['decompressor_sha256']=sha(args.probe.read_bytes())
        save(HERE/'resource-map.json',report)
        print(json.dumps(facts['summary']))

if __name__=='__main__':
    main()
