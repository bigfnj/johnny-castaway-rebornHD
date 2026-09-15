#!/usr/bin/env python3
"""Inventory local RESOURCE scripts, scheduler entries and implementation limits.

The production decompressor probe supplies decoded bytes. Original commercial
files are read locally; only names, counts, hashes and derived facts are output.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import difflib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ADS_OPS = {
    0x1070: ('IF_LASTPLAYED_LOCAL', 2), 0x1330: ('IF_UNKNOWN_1', 2),
    0x1350: ('IF_LASTPLAYED', 2), 0x1360: ('IF_NOT_RUNNING', 2),
    0x1370: ('IF_IS_RUNNING', 2), 0x1420: ('AND', 0), 0x1430: ('OR', 0),
    0x1510: ('PLAY_SCENE', 0), 0x1520: ('ADD_SCENE_LOCAL', 5),
    0x2005: ('ADD_SCENE', 4), 0x2010: ('STOP_SCENE', 3), 0x2014: ('UNKNOWN_5', 0),
    0x3010: ('RANDOM_START', 0), 0x3020: ('NOP', 1), 0x30ff: ('RANDOM_END', 0),
    0x4000: ('UNKNOWN_6', 3), 0xf010: ('FADE_OUT', 0), 0xf200: ('GOSUB_TAG', 1),
    0xffff: ('END', 0), 0xfff0: ('END_IF', 0),
}
TTM_OPS = {
    0x001f: 'SAVE_BACKGROUND', 0x0080: 'DRAW_BACKGROUND', 0x0110: 'PURGE',
    0x0ff0: 'UPDATE', 0x1021: 'SET_DELAY', 0x1051: 'SET_BMP_SLOT',
    0x1061: 'SET_PALETTE_SLOT', 0x1101: 'LOCAL_TAG', 0x1111: 'TAG',
    0x1121: 'TTM_UNKNOWN_1', 0x1201: 'GOTO_TAG', 0x2002: 'SET_COLORS',
    0x2012: 'SET_FRAME1', 0x2022: 'TIMER', 0x4004: 'SET_CLIP_ZONE',
    0x4110: 'FADE_OUT', 0x4120: 'FADE_IN', 0x4204: 'COPY_ZONE_TO_BG',
    0x4214: 'SAVE_IMAGE1', 0xa002: 'DRAW_PIXEL', 0xa054: 'SAVE_ZONE',
    0xa064: 'RESTORE_ZONE', 0xa0a4: 'DRAW_LINE', 0xa104: 'DRAW_RECT',
    0xa404: 'DRAW_CIRCLE', 0xa504: 'DRAW_SPRITE', 0xa510: 'DRAW_SPRITE1',
    0xa524: 'DRAW_SPRITE_FLIP', 0xa530: 'DRAW_SPRITE3', 0xa601: 'CLEAR_SCREEN',
    0xb606: 'DRAW_SCREEN', 0xc020: 'LOAD_SAMPLE', 0xc030: 'SELECT_SAMPLE',
    0xc040: 'DESELECT_SAMPLE', 0xc051: 'PLAY_SAMPLE', 0xc060: 'STOP_SAMPLE',
    0xf01f: 'LOAD_SCREEN', 0xf02f: 'LOAD_IMAGE', 0xf05f: 'LOAD_PALETTE',
}
FLAGS = {'FINAL': 1, 'FIRST': 2, 'ISLAND': 4, 'LEFT_ISLAND': 8,
         'VARPOS_OK': 16, 'LOWTIDE_OK': 32, 'NORAFT': 64, 'HOLIDAY_NOK': 128}
LIMITS = {
    'ADS:IF_UNKNOWN_1': ('ignored', 'Condition is read and logged but not evaluated.', 'src/engine/ads.c', 'case 0x1330:'),
    'ADS:UNKNOWN_5': ('unhandled', 'No playback switch case; default logs the opcode as a tag.', 'src/engine/ads.c', 'static void adsPlayChunk'),
    'ADS:UNKNOWN_6': ('ignored', 'Three arguments are read but have no playback effect.', 'src/engine/ads.c', 'case 0x4000:'),
    'ADS:FADE_OUT': ('ignored', 'Script fade command logs only; story-level fades are a separate path.', 'src/engine/ads.c', 'case 0xf010:'),
    'ADS:AND': ('structural_noop', 'Logged only; surrounding condition handling is specialized.', 'src/engine/ads.c', 'case 0x1420:'),
    'TTM:DRAW_BACKGROUND': ('ignored', 'Playback logs only; no draw or image-slot release.', 'src/engine/ttm.c', 'case 0x0080:'),
    'TTM:SET_PALETTE_SLOT': ('ignored', 'Palette slot argument has no effect.', 'src/engine/ttm.c', 'case 0x1061:'),
    'TTM:TTM_UNKNOWN_1': ('ignored', 'Region identifier is read but not stored.', 'src/engine/ttm.c', 'case 0x1121:'),
    'TTM:SET_FRAME1': ('ignored', 'Arguments are read and logged only.', 'src/engine/ttm.c', 'case 0x2012:'),
    'TTM:TIMER': ('approximate', 'Uses the arithmetic mean of both arguments; source explicitly questions this formula.', 'src/engine/ttm.c', 'case 0x2022:'),
    'TTM:SET_DELAY': ('modified', 'Values below four ticks are clamped to four.', 'src/engine/ttm.c', 'case 0x1021:'),
    'TTM:SAVE_IMAGE1': ('stub', 'Playback calls grSaveImage1, whose body does not save anything.', 'src/engine/graphics.c', 'void grSaveImage1'),
    'TTM:SAVE_ZONE': ('stub', 'grSaveZone does not save the requested zone.', 'src/engine/graphics.c', 'void grSaveZone'),
    'TTM:RESTORE_ZONE': ('partial', 'Drops the entire saved layer rather than restoring the requested rectangle.', 'src/engine/graphics.c', 'void grRestoreZone'),
    'TTM:CLEAR_SCREEN': ('partial', 'Clears the full layer; ignores the supplied saved-region identifier.', 'src/engine/ttm.c', 'case 0xA601:'),
    'TTM:DRAW_SCREEN': ('ignored', 'Six arguments are read and logged without drawing.', 'src/engine/ttm.c', 'case 0xB606:'),
    'TTM:LOAD_PALETTE': ('ignored', 'Palette filename is read and logged only.', 'src/engine/ttm.c', 'case 0xF05F:'),
}

# Reviewed family associations, not a reconstruction of every fan-described
# outcome. Short source IDs expand to stable scene-catalog IDs below. A tag
# description can identify an action family without proving the whole story.
FAN_FAMILIES = [
    ('sleep', 'common:sleep common:pirate-sleep', 'BUILDING.ADS#3 BUILDING.ADS#4 BUILDING.ADS#6', 'GJGULIVR.TTM:9,58,68'),
    ('fishing', 'common:fish common:rod-handedness', 'FISHING.ADS#1 FISHING.ADS#2 FISHING.ADS#7 FISHING.ADS#8', 'MJFISH.TTM:10 MJFISHC.TTM:2'),
    ('food', 'common:eat common:cook-fish common:eat-boot common:octopus-struggle', 'BUILDING.ADS#7', 'MJFIRE.TTM:70,72,74,75,76,78'),
    ('reading', 'common:read reading:book reading:interruption', 'ACTIVITY.ADS#6 ACTIVITY.ADS#7', 'MJREAD.TTM:22,24'),
    ('washing', 'common:wash swimming:bath-equipment swimming:water-temperature swimming:wash swimming:audience-cover swimming:dress swimming:fist', 'ACTIVITY.ADS#8', 'MJBATH.TTM:3,8,14,36,38,39,45'),
    ('jogging', 'common:jog', 'WALKSTUF.ADS#3', 'MJJOG.TTM:5,12,15'),
    ('sand-building', 'common:sand-work', 'BUILDING.ADS#1', 'MJSAND.TTM:3,5,7,8'),
    ('raft-building', 'common:raft-build', 'WALKSTUF.ADS#2', 'MJRAFT.TTM:3,4'),
    ('fire-variants', 'common:fire-two-rubs common:fire-three-rubs common:fire-four-rubs common:fire-after-abandon', 'BUILDING.ADS#5', 'MJFIRE.TTM:38,40,41'),
    ('coconut-bounces', 'common:coconut-right common:coconut-left', 'VISITOR.ADS#4', 'MJCOCO.TTM:19,20'),
    ('coconut-spin', 'common:coconut-head-spin', 'VISITOR.ADS#6', 'MJCOCO.TTM:34'),
    ('coconut-food', 'common:coconut-catch', 'VISITOR.ADS#7', 'MJCOCO.TTM:23,25'),
    ('messages', 'common:message-send common:message-return common:message-found common:message-day-two-thought common:thought-rescue common:thought-island common:thought-time common:thought-person unusual:thought-clock', 'JOHNNY.ADS#2 JOHNNY.ADS#3 JOHNNY.ADS#4 JOHNNY.ADS#5', 'SJMSSGE.TTM:6,9,10,20,21,22,23,24,33'),
    ('fishing-catches', 'fishing:boot-return fishing:boot-keep fishing:crab-return fishing:starfish-return fishing:crab-nose fishing:green-fish-catch fishing:plank fishing:lifebelt fishing:small-octopus fishing:unusual-storage fishing:lifebelt-left-artifact fishing:shark-tow fishing:green-fish-spray fishing:rod-handedness', 'FISHING.ADS#1 FISHING.ADS#2 FISHING.ADS#4 FISHING.ADS#6 FISHING.ADS#7 FISHING.ADS#8', 'MJFISH.TTM:24,31,32,33,34,35,36,37,41 MJFISHC.TTM:42,53,55,57,61,62,63'),
    ('large-octopus', 'fishing:large-octopus-chase fishing:large-octopus-theft annivers:octopus-decorations', 'FISHING.ADS#3', 'GJCATCH2.TTM:1,2'),
    ('diving', 'swimming:palm-dive swimming:judged-dive swimming:belly-flop swimming:crab-scoring', 'ACTIVITY.ADS#1 ACTIVITY.ADS#4', 'GJDIVE.TTM:7,8,9,13 MJDIVE.TTM:1'),
    ('clothes-gull', 'swimming:shorts-theft seagull:shorts-theft seagull:hat-nest', 'ACTIVITY.ADS#11', 'MJBATH.TTM:29,31,32'),
    ('bathing-shark', 'swimming:shark-bite swimming:shark-injury swimming:leg-fakeout', 'MISCGAG.ADS#2', 'SHARK1.TTM:2,3'),
    ('reading-gull', 'seagull:book-theft seagull:head-perch seagull:night-head seagull:night-book', 'ACTIVITY.ADS#10 ACTIVITY.ADS#12', 'MJREAD.TTM:96,101,103,107,112,113'),
    ('pirate-gull', 'seagull:pirate-chest-nest pirates:sleep-capture pirates:chest-egg pirates:silent-sleep pirates:gull-absent', 'BUILDING.ADS#4 BUILDING.ADS#6', 'GJGULIVR.TTM:60,61,67,68'),
    ('mary-glimpse', 'mermaid:identity mermaid:unseen mermaid:unseen-boot mermaid:unseen-teeth', 'MARY.ADS#2', 'SJGLIMPS.TTM:106,107,108'),
    ('mary-invitation', 'mermaid:gift-shells mermaid:gift-lifebelt mermaid:dinner-thought mermaid:traffic-light-thought', 'MARY.ADS#3', 'SASKDATE.TTM:117,119,125,130,134,150'),
    ('mary-date', 'mermaid:formal-date mermaid:date-conversation mermaid:date-dance', 'MARY.ADS#1', 'SMDATE.TTM:16,21,25,28,29,31'),
    ('mary-breakup', 'mermaid:raft-question mermaid:raft-refusal', 'MARY.ADS#4', 'SBREAKUP.TTM:33,34,35'),
    ('mary-farewell', 'mermaid:goodbye leaving:departure-equipment leaving:departure-visitors', 'MARY.ADS#5', 'SJLEAVES.TTM:3,4'),
    ('office', 'mermaid:office-dream unusual:office-dream', 'JOHNNY.ADS#6', 'SJWORK.TTM:3,4,7,8'),
    ('castle-pirates', 'pirates:castle-landing pirates:castle-capture pirates:tree-retreat pirates:miniature-planes pirates:fall', 'BUILDING.ADS#2', 'MJSAND.TTM:35,36,37,46,48,50,52,57,84'),
    ('suzy-bottle', 'leaving:suzy-identity leaving:bottle-fantasy', 'SUZY.ADS#1', 'SUZYCITY.TTM:6,7,14'),
    ('suzy-reunion', 'leaving:resort leaving:reunion-affection leaving:reunion-awkward leaving:reunion-gum leaving:ear-pull leaving:room-inset leaving:impress-suzy', 'SUZY.ADS#2', 'SJMSUZY.TTM:3,4,7'),
    ('telescope', 'visitors:telescope', 'STAND.ADS#15 STAND.ADS#16 VISITOR.ADS#1', 'MJTELE.TTM:12,13,29,32 GJVIS3.TTM:52'),
    ('passing-travelers', 'visitors:biplane visitors:helicopter visitors:aircraft-notice visitors:aircraft-signal visitors:aircraft-missed visitors:woman-dog-boat visitors:water-skier visitors:unnoticed-passers', 'VISITOR.ADS#1', 'GJVIS3.TTM:50,57,59,60,61,63'),
    ('party-boat', 'visitors:party-departure visitors:party-return', 'WALKSTUF.ADS#1', 'WOULDBE.TTM:8,9,11,15'),
    ('cargo-ship', 'visitors:ship-distant visitors:ship-close visitors:ship-signal', 'VISITOR.ADS#3', 'GJVIS6.TTM:5,6,7,8,9'),
    ('coconut-aircraft', 'visitors:coconut-crash unusual:coconut-crash', 'VISITOR.ADS#5', 'GJVIS5.TTM:3,5,9'),
    ('rain-dance-visitors', 'visitors:photographers', 'ACTIVITY.ADS#9', 'GJNAT3.TTM:12,13,14,15'),
    ('rain-dance', 'unusual:rain-dance', 'ACTIVITY.ADS#5 ACTIVITY.ADS#9', 'GJNAT1.TTM:28,31,32,33,34'),
    ('melting', 'unusual:melting', 'MISCGAG.ADS#1', 'GJHOT.TTM:3,6,7'),
    ('ending', 'unusual:ending-inset', 'JOHNNY.ADS#1', 'MEANWHIL.TTM:1 THEEND.TTM:1,4,5,6'),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text_digest(data):
    """Hash strict UTF-8 with CRLF and CR converted to LF; retain all else."""
    return digest(data.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').encode('utf-8'))


def u16(data, offset):
    return struct.unpack_from('<H', data, offset)[0]


def u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def cstring(data, offset, limit=40):
    end = data.index(0, offset, min(len(data), offset + limit))
    return data[offset:end].decode('ascii'), end + 1


def resource_catalog(map_bytes, volume):
    volume_name, pos = cstring(map_bytes, 6, 13)
    count = u16(map_bytes, pos)
    pos += 2
    if pos + count * 8 != len(map_bytes):
        raise ValueError('RESOURCE.MAP entry count does not cover its exact length')
    result = {}
    for index in range(count):
        offset = u32(map_bytes, pos + index * 8 + 4)
        name = volume[offset:offset + 13].split(b'\0')[0].decode('ascii')
        size = u32(volume, offset + 13)
        payload = volume[offset + 17:offset + 17 + size]
        if name in result or len(payload) != size:
            raise ValueError(f'Invalid or duplicate resource: {name}')
        result[name] = {'name': name, 'type': name.rsplit('.', 1)[-1],
                        'offset': offset, 'payload_bytes': size,
                        'payload_sha256': digest(payload), '_payload': payload}
    return volume_name, result


def metadata(resource):
    data, kind = resource['_payload'], resource['type']
    if kind == 'BMP':
        if data[8:12] != b'INF:':
            raise ValueError(resource['name'] + ': missing BMP INF chunk')
        resource['image_count'] = u16(data, 16)
    elif kind == 'SCR':
        resource['dimensions'] = [u16(data, 16), u16(data, 18)]
    elif kind in ('ADS', 'TTM'):
        pos = 21 if kind == 'ADS' else 23
        if kind == 'TTM':
            resource['declared_page_count'] = u16(data, 21)
        bindings = []
        if kind == 'ADS':
            if data[pos:pos + 4] != b'RES:':
                raise ValueError(resource['name'] + ': missing RES chunk')
            count = u16(data, pos + 8)
            pos += 10
            for _ in range(count):
                slot = u16(data, pos)
                name, pos = cstring(data, pos + 2)
                bindings.append({'slot': slot, 'resource': name})
        expected = b'SCR:' if kind == 'ADS' else b'TT3:'
        if data[pos:pos + 4] != expected:
            raise ValueError(resource['name'] + ': missing script chunk')
        raw_size = u32(data, pos + 4)
        resource.update(compression_method=data[pos + 8], script_bytes=u32(data, pos + 9))
        resource['_compressed'] = data[pos + 13:pos + 8 + raw_size]
        pos += 8 + raw_size
        if kind == 'TTM':
            if data[pos:pos + 4] != b'TTI:':
                raise ValueError(resource['name'] + ': missing TTI chunk')
            pos += 8
        if data[pos:pos + 4] != b'TAG:':
            raise ValueError(resource['name'] + ': missing TAG chunk')
        count, pos = u16(data, pos + 8), pos + 10
        tags = []
        for _ in range(count):
            tag = u16(data, pos)
            description, pos = cstring(data, pos + 2)
            tags.append({'id': tag, 'description': description})
        resource['tags'] = tags
        if bindings:
            resource['bindings'] = bindings


def compressed_parts(resource):
    data = resource['_compressed']
    if resource['compression_method'] != 1:
        return [(data, resource['script_bytes'])]
    # The existing probe accepts hex argv. Split only independent RLE packets
    # to stay below Windows' command-line limit; every byte is still decoded by
    # the production implementation, including literals and repeated packets.
    parts, start, pos, size = [], 0, 0, 0
    while pos < len(data):
        control = data[pos]
        consumed = 2 if control & 128 else 1 + control
        if pos + consumed > len(data):
            raise ValueError(resource['name'] + ': truncated RLE packet')
        pos += consumed
        size += control & 127 if control & 128 else control
        if pos - start >= 8000:
            parts.append((data[start:pos], size))
            start, size = pos, 0
    if pos > start:
        parts.append((data[start:pos], size))
    if sum(size for _, size in parts) != resource['script_bytes']:
        raise ValueError(resource['name'] + ': RLE size differs from header')
    return parts


def decode(resource, probe):
    output = []
    for compressed, size in compressed_parts(resource):
        result = subprocess.run([str(probe), str(resource['compression_method']),
                                 compressed.hex(), str(size)],
                                capture_output=True, text=True, timeout=30)
        match = re.search(r'^RESULT ([0-9a-f]+) consumed=(\d+)$', result.stdout, re.M)
        if result.returncode or not match:
            raise ValueError(f"{resource['name']}: decompressor failed: {result.stdout}{result.stderr}")
        part = bytes.fromhex(match[1])
        if len(part) != size or int(match[2]) != len(compressed):
            raise ValueError(resource['name'] + ': incomplete decompression')
        output.append(part)
    data = b''.join(output)
    resource['decoded_sha256'] = digest(data)
    commands, pos, tag = [], 0, 0
    while pos < len(data):
        start, code = pos, u16(data, pos)
        pos += 2
        if resource['type'] == 'ADS':
            name, nargs = ADS_OPS.get(code, ('TAG', 0))
            if name == 'TAG':
                tag = code
            args = [u16(data, pos + 2 * i) for i in range(nargs)]
            pos += 2 * nargs
        else:
            name, nargs = TTM_OPS.get(code, f'UNKNOWN_{code:04X}'), code & 15
            if nargs == 15:
                argument, end = cstring(data, pos, 256)
                pos = end + ((end - pos) & 1)
                args = [argument]
            else:
                args = [u16(data, pos + 2 * i) for i in range(nargs)]
                pos += 2 * nargs
            if name == 'TAG':
                tag = args[0]
        if pos > len(data):
            raise ValueError(resource['name'] + ': command exceeds decoded bytes')
        commands.append({'offset': start, 'opcode': f'{code:04X}', 'command': name,
                         'tag': tag, 'args': args})
    resource['_commands'] = commands
    resource['command_counts'] = dict(sorted(Counter(c['command'] for c in commands).items()))
    resource['script_tag_ids'] = sorted({c['tag'] for c in commands if c['command'] == 'TAG'})
    resource['local_tag_ids'] = sorted({c['args'][0] for c in commands if c['command'] == 'LOCAL_TAG'})
    resource['loaded_resources'] = sorted({c['args'][0] for c in commands
                                           if c['command'] in ('LOAD_IMAGE', 'LOAD_SCREEN', 'LOAD_PALETTE')})
    resource['played_samples'] = sorted({c['args'][0] for c in commands if c['command'] == 'PLAY_SAMPLE'})


def scheduler(root):
    result, excluded = [], []
    text = (root / 'src/data/story_data.h').read_text(encoding='utf-8')
    for number, line in enumerate(text.splitlines(), 1):
        match = re.search(r'\{\s*"([A-Z0-9_]+\.ADS)"\s*,\s*(\d+)\s*,(.*?)\}', line)
        if not match:
            continue
        fields = [part.strip() for part in match[3].split(',')]
        item = {'scene': f'{match[1]}#{match[2]}', 'ads': match[1], 'tag': int(match[2]),
                'source': f'src/data/story_data.h:{number}'}
        if line.lstrip().startswith('//'):
            item['reason_from_source'] = line.split('//')[-1].strip()
            excluded.append(item)
            continue
        flags = [flag.strip() for flag in fields[-1].split('|')]
        item.update(day=int(fields[-2]), flags=flags, flags_value=sum(FLAGS[f] for f in flags),
                    start_spot=fields[0], start_heading=fields[1],
                    end_spot=fields[2], end_heading=fields[3],
                    eligible_days=[int(fields[-2])] if int(fields[-2]) else list(range(1, 12)),
                    scheduler_status='statically_eligible', runtime_reachability_proven=False,
                    original_render_parity_proven=False)
        result.append(item)
    declared = int(re.search(r'#define NUM_SCENES\s+(\d+)', text)[1])
    if len(result) != declared:
        raise ValueError('Story parser count differs from NUM_SCENES')
    # Every non-final entry has a high-tide, unmoved-island final predecessor
    # that imposes no LOWTIDE_OK/VARPOS_OK filter. This is a constructive static
    # witness, not an assertion that any particular random run visits it.
    for item in result:
        if 'FINAL' not in item['flags']:
            item['leadup_witnesses'] = {}
            for day in item['eligible_days']:
                finals = [s for s in result if day in s['eligible_days'] and 'FINAL' in s['flags']
                          and 'ISLAND' in s['flags'] and not
                          {'FIRST', 'LEFT_ISLAND', 'VARPOS_OK'}.intersection(s['flags'])]
                if not finals:
                    raise ValueError(item['scene'] + ': no eligible final predecessor')
                item['leadup_witnesses'][str(day)] = finals[0]['scene']
    return result, excluded


def line_reference(root, filename, needle, playback=False):
    lines = (root / filename).read_text(encoding='utf-8').splitlines()
    start = next((i for i, line in enumerate(lines) if 'static void adsPlayChunk(' in line), 0) if playback else 0
    return f'{filename}:{next(i + 1 for i in range(start, len(lines)) if needle in lines[i])}'


def enrich(root, resources, scenes, excluded):
    by_scene = {s['scene']: s for s in scenes}
    ads_tags, used_ttm = [], set()
    for name, resource in resources.items():
        if resource['type'] != 'ADS':
            continue
        blocks = defaultdict(list)
        for command in resource['_commands']:
            blocks[command['tag']].append(command)
        bindings = {b['slot']: b['resource'] for b in resource.get('bindings', [])}
        for tag in resource['tags']:
            scene_id = f"{name}#{tag['id']}"
            visited, todo = set(), [tag['id']]
            while todo:
                current = todo.pop()
                if current in visited:
                    continue
                visited.add(current)
                todo += [c['args'][0] for c in blocks[current] if c['command'] == 'GOSUB_TAG']
            commands = [c for key in sorted(visited) for c in blocks[key]]
            refs = []
            for c in commands:
                if c['command'] in ('ADD_SCENE', 'ADD_SCENE_LOCAL'):
                    args = c['args'][1:] if c['command'] == 'ADD_SCENE_LOCAL' else c['args']
                    ref = {'resource': bindings.get(args[0], f'UNBOUND_SLOT_{args[0]}'), 'tag': args[1]}
                    target = resources.get(ref['resource'], {})
                    ref['target_present'] = ref['tag'] in target.get('script_tag_ids', []) + target.get('local_tag_ids', [])
                    ref['description'] = next((t['description'] for t in target.get('tags', []) if t['id'] == ref['tag']), None)
                    if ref not in refs:
                        refs.append(ref)
            incoming = [f'{name}#{c["tag"]}' for c in resource['_commands']
                        if c['command'] == 'GOSUB_TAG' and c['args'][0] == tag['id']]
            status = 'story_entry' if scene_id in by_scene else 'helper_via_gosub' if incoming else 'not_selected_by_story'
            record = {'scene': scene_id, 'description': tag['description'], 'status': status,
                      'gosub_callers': sorted(set(incoming)), 'gosub_closure': sorted(visited),
                      'ttm_references': refs, 'ads_command_counts': dict(sorted(Counter(c['command'] for c in commands).items())),
                      'direct_cli_available': True, 'original_render_parity_proven': False}
            raw = [{k: v for k, v in c.items() if k not in ('offset', 'tag')}
                   for c in blocks[tag['id']] if c['command'] != 'TAG']
            record['block_commands_sha256'] = digest(json.dumps(raw, sort_keys=True).encode())
            ads_tags.append(record)
            if scene_id in by_scene:
                by_scene[scene_id].update(description=tag['description'], ttm_references=refs)
                used_ttm.update(r['resource'] for r in refs)
    support = []
    for kind, table, file in [('ADS', ADS_OPS, 'src/engine/ads.c'), ('TTM', TTM_OPS, 'src/engine/ttm.c')]:
        playback = (root / file).read_text(encoding='utf-8')
        playback = playback[playback.index('static void adsPlayChunk('):] if kind == 'ADS' else playback[playback.index('void ttmPlay('):]
        for code, value in sorted(table.items()):
            name = value[0] if kind == 'ADS' else value
            occurrences = [{'resource': r['name'], 'count': r['command_counts'][name],
                            'tags': sorted({c['tag'] for c in r['_commands'] if c['command'] == name})}
                           for r in resources.values() if r['type'] == kind and r['command_counts'].get(name)]
            key = f'{kind}:{name}'
            if key in LIMITS:
                status, note, evidence_file, needle = LIMITS[key]
                evidence = line_reference(root, evidence_file, needle, kind == 'ADS')
            elif not re.search(rf'case\s+0x{code:04x}\s*:', playback, re.I):
                status, note = 'unhandled', 'No playback switch case; decoded arguments are consumed without an operation.'
                evidence = line_reference(root, file, 'switch (opcode)', kind == 'ADS')
            else:
                status, note = 'implemented_unverified_parity', 'Playback contains handling; original-engine behavior has not been compared scene by scene.'
                evidence = line_reference(root, file, next(line.strip() for line in playback.splitlines() if re.search(rf'case\s+0x{code:04x}\s*:', line, re.I)), kind == 'ADS')
            support.append({'language': kind, 'opcode': f'{code:04X}', 'command': name,
                            'status': status, 'note': note, 'source': evidence,
                            'occurrences': occurrences, 'total': sum(o['count'] for o in occurrences)})
    return ads_tags, support, sorted(r['name'] for r in resources.values() if r['type'] == 'TTM' and r['name'] not in used_ttm)


def dump_validation(exe, archive, root):
    with tempfile.TemporaryDirectory(prefix='johnny-inventory-dump-') as temporary:
        work = Path(temporary)
        shutil.copyfile(archive, work / 'scrantic_data.zip')
        result = subprocess.run([str(exe), 'dump'], cwd=work, capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise ValueError('Production dump failed: ' + result.stdout + result.stderr)
        expected = {}
        for line in (root / 'tests/golden-dump.sha256').read_text(encoding='utf-8').splitlines():
            checksum, name = line.split('  ', 1)
            expected[name] = checksum
        actual = {p.relative_to(work / 'dump').as_posix(): digest(p.read_bytes())
                  for p in (work / 'dump').rglob('*') if p.is_file()}
        mismatches = sorted(name for name in set(expected) | set(actual) if expected.get(name) != actual.get(name))
        if mismatches:
            raise ValueError(f'Golden dump differs in {len(mismatches)} files: {mismatches[:5]}')
        return {'status': 'all_hashes_match', 'files': len(actual),
                'counts_by_directory': dict(sorted(Counter(name.split('/')[0] for name in actual).items())),
                'golden_lf_utf8_sha256': text_digest((root / 'tests/golden-dump.sha256').read_bytes()),
                'scope': 'Port decoder regression only; not original executable rendering parity.'}


def public(resource):
    return {k: v for k, v in resource.items() if not k.startswith('_')}


def command_changes(original, port):
    key = lambda c: json.dumps({k: v for k, v in c.items() if k != 'offset'}, sort_keys=True)
    a, b = original['_commands'], port['_commands']
    changes = []
    for action, i, j, k, l in difflib.SequenceMatcher(None, [key(c) for c in a], [key(c) for c in b], autojunk=False).get_opcodes():
        if action != 'equal':
            changes.append({'action': action, 'original_commands': a[i:j], 'port_commands': b[k:l]})
    return changes


def fan_crosswalk(root, resources, scenes):
    path = root / 'docs/knowledge-base/scene-catalog.json'
    catalog = json.loads(path.read_text(encoding='utf-8'))
    by_id = {entry['id']: entry for entry in catalog['entries']}
    assigned, groups = set(), []
    for family, ids, ads, tags in FAN_FAMILIES:
        ids = ['fan:' + short for short in ids.split()]
        for identity in ids:
            by_id[identity]  # Resolve the reviewed ID; stale or mistyped IDs fail visibly.
        evidence = []
        for token in tags.split():
            name, numbers = token.split(':')
            descriptions = {t['id']: t['description'] for t in resources[name]['tags']}
            evidence += [{'resource': name, 'tag': int(number), 'description': descriptions[int(number)]}
                         for number in numbers.split(',')]
        groups.append({'id': family, 'status': 'candidate_family', 'catalog_ids': ids,
                       'ads_scenes': ads.split(), 'resource_tag_evidence': evidence,
                       'basis': 'Named resource tags and active ADS dependencies identify an action family. Exact fan-described outcomes, timing, side, object details and conditional variants remain unverified.',
                       'original_render_parity_proven': False})
        assigned.update(ids)
    for entry in catalog['entries']:
        if entry['kind'] == 'story_day':
            scene = next(s for s in scenes if s['day'] == entry['story_day'])
            groups.append({'id': 'story-day-' + str(entry['story_day']), 'status': 'story_day_alignment',
                           'catalog_ids': [entry['id']], 'ads_scenes': [scene['scene']],
                           'source': scene['source'], 'basis': 'The named chapter and scheduler day align. Additional events mentioned in the fan summary are not all part of this ADS scene.',
                           'original_render_parity_proven': False})
            assigned.add(entry['id'])
    context = [e['id'] for e in catalog['entries'] if e['kind'] == 'context_claim']
    context += ['fan:common:walk', 'fan:common:raft-reset']
    groups.append({'id': 'scheduler-context', 'status': 'context_source', 'catalog_ids': context,
                   'sources': [line_reference(root, 'src/engine/story.c', 'void storyPlay('),
                               line_reference(root, 'src/engine/story.c', 'static void storyCalculateIslandFromScene('),
                               line_reference(root, 'src/engine/ads.c', 'void adsPlayWalk(')],
                   'basis': 'Source locations for day, tide, night, raft stage, inter-scene walking and transitions. Fan timing estimates, tide-specific catches and night-only outcomes are not proved by this association.',
                   'original_render_parity_proven': False})
    assigned.update(context)
    calendar = {'new-year': ['12-29', '01-01'], 'saint-patrick': ['03-15', '03-17'],
                'halloween': ['10-29', '10-31'], 'christmas': ['12-23', '12-25']}
    for name, window in calendar.items():
        identity = 'fan:annivers:' + name
        groups.append({'id': 'calendar-' + name, 'status': 'calendar_source_alignment',
                       'catalog_ids': [identity], 'sources': ['src/engine/story.c', 'src/engine/island.c'],
                       'reviewed_port_date_window_inclusive': window,
                       'fan_window_matches_reviewed_source': by_id[identity]['reported_date_window_inclusive'] == window,
                       'basis': 'The inclusive calendar window was manually compared with story.c; island.c selects decorations. Original decorative animation behavior is not established.',
                       'original_render_parity_proven': False})
        assigned.add(identity)
    faults = [e['id'] for e in catalog['entries'] if e['kind'] == 'reported_legacy_fault']
    groups.append({'id': 'legacy-fault-reports', 'status': 'unverified_legacy_fault', 'catalog_ids': faults,
                   'basis': 'Reports about the old Windows program are neither a port reproduction nor a required animation specification.',
                   'original_render_parity_proven': False})
    assigned.update(faults)
    return {'catalog_lf_utf8_sha256': text_digest(path.read_bytes()), 'catalog_observations': len(by_id),
            'scope': 'Grouped candidates cover source observations, not distinct animation counts or original visual parity. All fan records retain secondary_unverified status.',
            'groups': groups, 'observations_by_status': dict(sorted(Counter(g['status'] for g in groups for _ in g['catalog_ids']).items())),
            'unmapped_catalog_ids': sorted(set(by_id) - assigned),
            'unmapped_meaning': 'No sufficiently specific resource or source association established. This is an open identification task, not evidence that the animation is missing.'}


def markdown(report):
    summary = report['summary']
    resources = report['port_resources']
    scenes = report['ads_scenes']
    schedules = {s['scene']: s for s in report['story_entries']}
    def link(ref):
        filename, line = ref.rsplit(':', 1)
        return f'[{ref}](../../{filename}#L{line})'
    lines = [
        '# Port resource and scene inventory', '',
        'This inventory separates resource presence, static scheduler eligibility, and proven rendering behavior. '
        'It compares the bundled archive with the user-provided local original RESOURCE.MAP and RESOURCE.001. '
        'It does not execute or redistribute the original binary, and does not claim visual parity with it.', '',
        'The reproducible facts are in [port-inventory.json](port-inventory.json). Full decoded script bodies '
        'and binary assets are not stored in this report.', '',
        '## What is present', '',
        '| Resource kind | Port | Local original |', '|---|---:|---:|',
    ]
    for kind in sorted(set(summary['port_resource_types']) | set(summary['original_resource_types'])):
        lines.append(f"| {kind} | {summary['port_resource_types'].get(kind, 0)} | {summary['original_resource_types'].get(kind, 0)} |")
    missing = ', '.join(f'`{name}`' for name in summary['missing_port_resources']) or 'none'
    same = Counter(r['name'].rsplit('.', 1)[-1] for r in report['resource_comparison'] if r.get('decoded_script_identical'))
    changed = [r for r in report['resource_comparison'] if r.get('decoded_script_identical') is False]
    lines += ['', f'Original resource names absent from the port: {missing}. '
              'The role of an omitted resource is not established by its name alone. '
              'A resource omission does not establish a missing animation.', '',
              f"The port contains {summary['bitmap_frames']:,} legacy bitmap frames and {summary['port_resource_types']['SCR']} packed screens. "
              f"The fresh headless production dump matched all {report['golden_dump']['files']:,} checked-in golden hashes. "
              'These hashes establish port decoder regression coverage, not original rendering equivalence.', '',
              f"Decoded streams identical to the original: {same['ADS']} of {summary['port_resource_types']['ADS']} ADS; "
              f"{same['TTM']} of {summary['port_resource_types']['TTM']} TTM. "
              'The JSON compares each script\'s tag descriptions and resource bindings separately. '
              'Changed decoded command sequences follow; differences exclude offsets shifted by another edit.', '']
    for resource in changed:
        for change in resource['command_changes']:
            detail = '; '.join(f"{side}: " + ', '.join(f"{c['command']} {c['args']} at byte {c['offset']} (tag {c['tag']})" for c in change[side + '_commands'])
                               for side in ('original', 'port') if change[side + '_commands'])
            lines.append(f"- `{resource['name']}` {change['action']}: {detail}.")
    lines += ['', 'The inventory makes no claim about why a script was changed.', '',
              'Raw image payloads differ between distributions. The JSON records hashes and screen dimensions; '
              'compressed-payload differences alone do not establish pixel differences.', '',
              'For sound payload coverage, see the separately reproduced '
              '[original NE audio comparison](original-ne-audio.json) and '
              '[original reference](original-reference.md#complete-embedded-audio-comparison). '
              'All 23 declared original RIFF payloads match bundled WAV prefixes. The original PLAY_SAMPLE '
              'identifier mapping remains unresolved; filename gaps such as 11 and 13 do not establish lost audio.', '',
              '## Scheduler eligibility', '',
              f"There are {summary['ads_tags']} ADS tag records and {summary['story_entries']} direct story entries. "
              'The table entries are statically eligible on their stated story days. A scene eligible for selection '
              'is not guaranteed to be chosen during any finite run.', '',
              'For each story sequence, the scheduler first chooses a FINAL entry. Unless that entry also has FIRST, '
              'it chooses ordinary lead-in scenes filtered by tide, island movement, day, and FIRST status. '
              'The lead-in loop re-evaluates its random bound on each iteration. Story day advances once when the saved '
              'calendar day differs from today, then wraps after day 11; it does not advance once per scene. '
              'Night changes the backdrop between 21:00 and 05:59; it is not an ADS selection flag. '
              'See [story.c](../../src/engine/story.c) and [story_data.h](../../src/data/story_data.h).', '',
              'Each JSON story entry includes a constructive static predecessor for non-final scenes. '
              'The predecessor can use high tide and an unmoved island, imposing no extra eligibility flags. '
              'This is a source-based eligibility witness, not an original scheduler comparison or a playback trace.', '',
              '| Story day | Day-specific scene | Original tag description |', '|---:|---|---|']
    for scene in sorted(report['story_entries'], key=lambda s: (s['day'], s['scene'])):
        if scene['day']:
            lines.append(f"| {scene['day']} | `{scene['scene']}` | {scene['description']} |")
    lines += ['', '`BUILDING.ADS#9` (FIRE (NIGHT)) is command-for-command identical to #5; '
              '`BUILDING.ADS#8` (EAT (NIGHT)) is identical to #7. The scheduler comments out those aliases. '
              '`STAND.ADS#14` (STAND INIT) is invoked through GOSUB_TAG and is not a missing standalone scene.', '',
              '## ADS scene catalog', '',
              'Descriptions below come from original resource metadata. TTM references include explicit ADD_SCENE '
              'and ADD_SCENE_LOCAL operations plus transitive ADS GOSUB helpers. They are a conservative dependency '
              'inventory; conditions and random branches are not claimed to execute on every visit.', '',
              '| ADS tag | Description | Story day / role | TTM dependencies |', '|---|---|---|---|']
    for scene in sorted(scenes, key=lambda s: (s['scene'].split('#')[0], int(s['scene'].split('#')[1]))):
        scheduled = schedules.get(scene['scene'])
        role = (f"day {scheduled['day']}" if scheduled['day'] else 'any day') + (' / final' if 'FINAL' in scheduled['flags'] else ' / lead-in') if scheduled else scene['status']
        deps = ', '.join(f'`{name}`' for name in sorted({r['resource'] for r in scene['ttm_references']}))
        lines.append(f"| `{scene['scene']}` | {scene['description']} | {role} | {deps} |")
    lines += ['', '## TTM resource inventory', '',
              'Declared tag records can describe local labels as well as global entry points. `SASKDATE.TTM` has '
              '40 declared records, including five local labels (129, 133, 140, 146, 151), and 35 global tags. '
              'Those local labels are present; they must not be classified as missing animation tags.', '',
              '| TTM | Declared pages | Global / local labels | Story ADS dependency | Original decoded bytes |',
              '|---|---:|---:|---|---|']
    comparison = {r['name']: r for r in report['resource_comparison']}
    for resource in resources:
        if resource['type'] == 'TTM':
            uses = ', '.join(f'`{s["scene"]}`' for s in scenes if s['scene'] in schedules and any(r['resource'] == resource['name'] for r in s['ttm_references'])) or 'none'
            equal = 'identical' if comparison[resource['name']].get('decoded_script_identical') else 'differs; see JSON'
            lines.append(f"| `{resource['name']}` | {resource['declared_page_count']} | {len(resource['script_tag_ids'])} / {len(resource['local_tag_ids'])} | {uses} | {equal} |")
    unused = ', '.join(f'`{name}`' for name in summary['unreferenced_from_story_ttm_files']) or 'none'
    lines += ['', f'TTM files not referenced by the active story ADS dependency graph: {unused}. '
              'They remain addressable with the direct `ttm` CLI mode. Their presence in the original archive '
              'does not prove the original scheduler used them. Similar actions are named in active scripts '
              '(fire in MJFIRE, reading gulls in MJREAD, tiny-islander scenes in MJSAND/GJGULIVR, '
              'the aircraft encounter in GJVIS5, and coconuts in MJCOCO). Treat these as unused resource variants '
              'until the original control flow or a reliable scene observation proves a distinct omission.', '',
              '## Concrete implementation gaps', '',
              'The following commands actually occur in shipped scripts and have omitted, simplified, or uncertain '
              'semantics in the port. Counts are static occurrences across all 41 TTM or 10 ADS resources. '
              'A command gap is evidence of incomplete interpreter behavior; it does not by itself prove that '
              'a particular visible gag is absent.', '',
              '| Language / command | Occurrences | Current behavior | Source |', '|---|---:|---|---|']
    for entry in report['command_support']:
        if entry['total'] and entry['status'] != 'implemented_unverified_parity':
            lines.append(f"| {entry['language']} `{entry['command']}` | {entry['total']} | {entry['note']} | {link(entry['source'])} |")
    lines += ['', 'Narrow animation investigations supported by these facts:', '',
              '- `GJGULIVR.TTM` contains the only SAVE_ZONE and RESTORE_ZONE pair. Saving is a stub and restoration '
              'drops the whole saved layer, so region restoration needs original-frame comparison.',
              '- Six DRAW_SCREEN operations are ignored: three in MJSAND and one each in GJGULIVR, SASKDATE, and SBREAKUP. '
              'The JSON records their containing tags. These are specific candidates for incomplete visual operations.',
              '- Script fades, palette selection, saved-region identifiers, and image-save requests have no equivalent '
              'operation at their command sites. The separate story transition and initial palette paths must not '
              'be confused with those command implementations.',
              '- TIMER uses an explicitly uncertain averaging formula, while SET_DELAY clamps short delays. '
              'Timing parity remains unproven even when every sprite and script resource is present.', '',
              'Known opcode names with no shipped occurrence are included in JSON with total zero. They are '
              'not evidence of missing shipped animation behavior.', '',
              '## Fan catalog crosswalk', '',
              'The [fan catalog](scene-catalog.md) records secondary observations, not a complete original specification. '
              'The JSON associates its stable IDs with scene families and explicit resource-tag evidence. '
              'A family match establishes an investigation starting point; it does not validate every object, action, '
              'outcome or timing detail mentioned by the fan. No named chapter in the eleven-day fan sequence lacks '
              'a corresponding scheduler day entry, but chapter presence does not prove all variants.', '',
              '| Association | Fan observations |', '|---|---:|']
    crosswalk = report['fan_crosswalk']
    for status, count in crosswalk['observations_by_status'].items():
        lines.append(f'| {status} | {count} |')
    lines.append(f"| unmapped | {len(crosswalk['unmapped_catalog_ids'])} |")
    lines += ['', '| Candidate family | ADS scene identifiers | Observation count |', '|---|---|---:|']
    for group in crosswalk['groups']:
        if group['status'] == 'candidate_family':
            lines.append(f"| {group['id']} | " + ', '.join(f'`{s}`' for s in group['ads_scenes']) + f" | {len(group['catalog_ids'])} |")
    lines += ['', 'Unmapped individual observations: ' + ', '.join(f'`{identity}`' for identity in crosswalk['unmapped_catalog_ids']) + '.', '',
              'These unresolved IDs are identification work, not confirmed missing animations. Exact fire-rubbing counts, '
              'night-specific gull outcomes, unusual catch artifacts, detailed reunion variants, and the Christmas '
              'octopus outcome also remain unverified within their candidate families. The eighteen legacy fault '
              'reports are kept separate from required animation behavior. All four fan calendar windows match the '
              'manually reviewed port date conditions; decorative rendering parity remains unproven.', '',
              '## What testing proves', '',
              'The golden dump covers decoded port assets and textual scripts. Rendering tests exercise selected '
              'sprite, screen, wave, palm, alpha, clipping, and fallback paths. Browser audio timing uses the shipped '
              'GJHOT sample sequence. None of those is an exhaustive original-versus-port scene-frame oracle. '
              'All scene records therefore leave original_render_parity_proven false. '
              'See [tests/BUILD_VALIDATION.md](../../tests/BUILD_VALIDATION.md), '
              '[Invoke-ArtStyleTests.ps1](../../tests/Invoke-ArtStyleTests.ps1), '
              '[test_wave_renderer.py](../../tests/test_wave_renderer.py), '
              '[test_palm_renderer.py](../../tests/test_palm_renderer.py), and '
              '[web-audio-timing.py](../../tests/web-audio-timing.py).', '',
              '## Reproduce', '',
              'Build the current production executable and decompressor probe, then run locally:', '',
              '```powershell', 'python -B tools/inventory_scenes.py `',
              '  --probe build/Release/jc_uncompress_test.exe `', '  --exe build/Release/jc_reborn.exe `',
              '  --original-dir C:/JohnCast/SIERRA/SCRANTIC `',
              '  --output docs/knowledge-base/port-inventory.json', '```', '',
              'The command writes this Markdown companion and JSON metadata. It reads the original resource pair '
              'without copying it into the repository. It uses the real production decompressor, splits large RLE '
              'inputs only at packet boundaries to fit Windows argv limits, and creates a temporary headless dump '
              'of the port archive for comparison with every golden hash. Input and executable hashes are recorded '
              'in JSON; tool and source changes require regeneration.', '']
    lines += ['Schema version 2 identifies text input hashes with `lf_utf8_sha256` in their field names. '
              'For the generator, scene catalog, reviewed source files and golden manifest, decode UTF-8 strictly, '
              'replace CRLF and any remaining CR with LF, then hash the UTF-8 encoding. Preserve the BOM if present, '
              'spaces, trailing blank lines and all other characters. This makes those fingerprints independent '
              'of checkout line endings without hiding content edits. Original resources, archives, executables, '
              'compressed payloads and decoded script bytes retain exact raw-byte SHA-256 hashes. '
              'ADS command-block fingerprints continue to hash their serialized derived command records. '
              'Generated JSON and Markdown use UTF-8 with LF line endings. Scoped `.gitattributes` rules '
              'preserve those exact bytes for the two checked-in inventory reports during Git checkout. '
              'Other source files may use CRLF in a checkout; their fingerprints follow the text policy above.', '']
    lines += ['The command-support explanations and scheduler interpretation are manually reviewed source assessments, '
              'not semantic proofs derived from matching a switch label. Re-review these assessments when their recorded '
              'source hashes change. Run the focused fixture and mutation checks with '
              '`python -B tests/test_scene_inventory.py --mutations`.', '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--probe', required=True, type=Path)
    parser.add_argument('--exe', required=True, type=Path)
    parser.add_argument('--original-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    root, probe, exe = args.root.resolve(), args.probe.resolve(), args.exe.resolve()
    archive = (args.archive or root / 'assets/scrantic_data.zip').resolve()
    with zipfile.ZipFile(archive) as z:
        port_map, port_volume = z.read('data/RESOURCE.MAP'), z.read('data/RESOURCE.001')
        archive_members = [{'name': item.filename, 'bytes': item.file_size} for item in z.infolist() if not item.is_dir()]
    original_map = (args.original_dir / 'RESOURCE.MAP').read_bytes()
    original_volume = (args.original_dir / 'RESOURCE.001').read_bytes()
    _, port = resource_catalog(port_map, port_volume)
    _, original = resource_catalog(original_map, original_volume)
    for label, catalog in [('port', port), ('original', original)]:
        for resource in catalog.values():
            metadata(resource)
            if resource['type'] in ('ADS', 'TTM'):
                decode(resource, probe)
        print(f'{label}: {len(catalog)} resources inventoried', flush=True)
    scenes, excluded = scheduler(root)
    tags, support, unreferenced = enrich(root, port, scenes, excluded)
    comparison = []
    for name in sorted(set(port) | set(original)):
        p, o = port.get(name), original.get(name)
        record = {'name': name, 'port_present': p is not None, 'original_present': o is not None}
        if p and o:
            record['payload_identical'] = p['payload_sha256'] == o['payload_sha256']
            if p['type'] in ('ADS', 'TTM'):
                record['decoded_script_identical'] = p['decoded_sha256'] == o['decoded_sha256']
                record['tags_identical'] = p['tags'] == o['tags']
                record['bindings_identical'] = p.get('bindings') == o.get('bindings')
                if not record['decoded_script_identical']:
                    record['command_changes'] = command_changes(o, p)
        comparison.append(record)
    report = {
        'schema_version': 2,
        'hash_policy': {
            'text_inputs': 'Fields containing lf_utf8_sha256 hash strict UTF-8 text after CRLF and remaining CR are replaced with LF. All other characters, BOMs, whitespace and trailing blank lines are preserved.',
            'raw_bytes': 'Archive, original/port resource-pair, probe/executable, resource-payload and decoded-script hashes remain SHA-256 of exact bytes; no text normalization applies.',
            'derived_records': 'ADS block_commands_sha256 hashes JSON-serialized derived command records with sorted keys, excluding offsets, the containing ADS tag number and TAG commands.',
            'generated_reports': 'JSON and Markdown are emitted as UTF-8 with LF line endings. Scoped .gitattributes rules preserve LF for the two checked-in inventory reports.'},
        'scope': 'Local port and original resource/script inventory; static reachability; no original runtime/render parity assertion.',
        'original_comparison': {'status': 'performed', 'inputs': ['RESOURCE.MAP', 'RESOURCE.001'],
                                'omitted_mode_supported': False},
        'assessment_method': 'Command-support notes and scheduler interpretation are manually reviewed; source hashes identify the reviewed snapshot. Re-review them after source changes.',
        'related_evidence': ['original-ne-audio.json', 'original-reference.md', 'scene-catalog.json'],
        'inputs': {'inventory_tool_lf_utf8_sha256': text_digest(Path(__file__).read_bytes()),
                   'archive_sha256': digest(archive.read_bytes()),
                   'port_map_sha256': digest(port_map), 'port_volume_sha256': digest(port_volume),
                   'original_map_sha256': digest(original_map), 'original_volume_sha256': digest(original_volume),
                   'probe_sha256': digest(probe.read_bytes()), 'engine_sha256': digest(exe.read_bytes()),
                   'source_lf_utf8_sha256': {name: text_digest((root / name).read_bytes()) for name in
                       ['src/data/story_data.h', 'src/engine/story.c', 'src/engine/ads.c',
                        'src/engine/ttm.c', 'src/engine/graphics.c', 'src/engine/resource.c', 'src/engine/dump.c',
                        'src/engine/sound.c', 'src/engine/island.c', 'src/data/walk_data.h']}},
        'summary': {'port_resource_types': dict(sorted(Counter(r['type'] for r in port.values()).items())),
                    'original_resource_types': dict(sorted(Counter(r['type'] for r in original.values()).items())),
                    'story_entries': len(scenes), 'ads_tags': len(tags),
                    'ttm_declared_tags': sum(len(r['tags']) for r in port.values() if r['type'] == 'TTM'),
                    'ttm_global_tags': sum(len(r['script_tag_ids']) for r in port.values() if r['type'] == 'TTM'),
                    'ttm_local_labels': sum(len(r['local_tag_ids']) for r in port.values() if r['type'] == 'TTM'),
                    'bitmap_frames': sum(r.get('image_count', 0) for r in port.values()),
                    'missing_port_resources': sorted(set(original) - set(port)),
                    'unresolved_ads_ttm_references': [{'scene': s['scene'], **r} for s in tags for r in s['ttm_references'] if not r['target_present']],
                    'unreferenced_from_story_ttm_files': unreferenced},
        'golden_dump': dump_validation(exe, archive, root),
        'fan_crosswalk': fan_crosswalk(root, port, scenes),
        'story_entries': scenes, 'commented_story_entries': excluded, 'ads_scenes': tags,
        'command_support': support, 'resource_comparison': comparison,
        'port_resources': [public(port[name]) for name in sorted(port)],
        'original_resources': [public(original[name]) for name in sorted(original)],
        'archive_members': archive_members,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    args.output.with_suffix('.md').write_text(markdown(report), encoding='utf-8', newline='\n')
    print(json.dumps(report['summary'], sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
