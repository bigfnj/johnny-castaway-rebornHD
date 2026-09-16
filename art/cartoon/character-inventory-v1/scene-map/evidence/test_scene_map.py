"""Bounded smoke/regression fixtures for static attribution, not playback tests."""
import argparse
import copy
import importlib.util
import json
import os
import tempfile
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('scene_map',Path(os.environ.get('SCENE_MAP_HELPER',HERE/'build_scene_map.py')))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.ROOT=HERE.parents[3]

def fixture(commands):
    return {'X.TTM':{'type':'TTM','decoded_sha256':'a'*64,'tags':[],
        '_commands':[{'command':name,'args':args,'offset':i*10,'tag':1} for i,(name,args) in enumerate(commands)]}}

class Smoke(unittest.TestCase):
    def test_unique_mapping_and_flip(self):
        r=m.static_sites(fixture([('SET_BMP_SLOT',[2]),('LOAD_IMAGE',['JOHNWALK.BMP']),
            ('DRAW_SPRITE_FLIP',[65535,4,35,2])]))
        s=r['draw_sites'][0]
        self.assertEqual((s['resource'],s['draw'],s['flip']),('JOHNWALK.BMP',[-1,4,35,2],True))
    def test_complete_resource_report(self):
        r=json.loads((HERE/'resource-map.json').read_bytes())
        self.assertEqual(r['summary'],{'bmp_resources':117,'port_bmp_resources':116,'original_bmp_resources':117})
        self.assertEqual([x['resource'] for x in r['resources'] if not x['port_present']],['SA_DEMO.BMP'])

class Regression(unittest.TestCase):
    def test_reused_slot_stays_ambiguous(self):
        r=m.static_sites(fixture([('SET_BMP_SLOT',[0]),('LOAD_IMAGE',['ONE.BMP']),
            ('DRAW_SPRITE',[1,2,3,0]),('LOAD_IMAGE',['TWO.BMP']),('DRAW_SPRITE',[1,2,3,0])]))
        for s in r['draw_sites']:
            self.assertIsNone(s['resource'])
            self.assertEqual(s['resource_candidates'],['ONE.BMP','TWO.BMP'])
        self.assertEqual([s['linear_resource_hint'] for s in r['draw_sites']],['ONE.BMP','TWO.BMP'])
    def test_unassigned_draw_is_explicit(self):
        s=m.static_sites(fixture([('DRAW_SPRITE',[1,2,3,4])]))['draw_sites'][0]
        self.assertEqual(s['attribution'],'unresolved-script-slot')
        self.assertEqual(s['resource_candidates'],[])
    def test_missing_load_selector_is_refused(self):
        with self.assertRaisesRegex(ValueError,'unresolved-load-slot: X.TTM:0'):
            m.static_sites(fixture([('LOAD_IMAGE',['ONE.BMP'])]))
    def test_global_tag_resets_delay_inference(self):
        sites=m.static_sites(fixture([('SET_BMP_SLOT',[0]),('LOAD_IMAGE',['ONE.BMP']),
            ('TAG',[1]),('SET_DELAY',[10]),('DRAW_SPRITE',[1,2,3,0]),
            ('TAG',[2]),('DRAW_SPRITE',[4,5,6,0])]))['draw_sites']
        self.assertEqual(sites[0]['last_same_tag_delay_instruction']['args'],[10])
        self.assertIsNone(sites[1]['last_same_tag_delay_instruction'])
    def test_current_resource_identity_guard(self):
        inv={'port_resources':[{'name':'ONE.BMP','type':'BMP','image_count':1,'payload_sha256':'a'*64}],
            'story_entries':[], 'original_resources':[],'inputs':{'archive_sha256':'c'*64}}
        with self.assertRaisesRegex(ValueError,'current-resource-identity: ONE.BMP'):
            m.resource_report(inv,{'ONE.BMP':{'type':'BMP','name':'ONE.BMP','payload_sha256':'b'*64}},'c'*64)
    def test_original_identity_guard(self):
        root=m.ROOT/'build/character-inventory/scene-map'
        root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            p=Path(directory)
            (p/'RESOURCE.MAP').write_bytes(b'map')
            (p/'RESOURCE.001').write_bytes(b'volume')
            expected={'original_map_sha256':m.sha(b'map'),'original_volume_sha256':m.sha(b'volume')}
            self.assertEqual(len(m.original_identity(p,expected)),2)
            (p/'RESOURCE.MAP').write_bytes(b'changed-map')
            with self.assertRaisesRegex(ValueError,'original-resource-identity: RESOURCE.MAP'):
                m.original_identity(p,expected)
    def test_native_cd_and_no_water_exit_frames(self):
        native=m.native_sites()
        cd=[r for r in native['rows'] if r['group']=='C to D' and not r['sentinel']]
        self.assertEqual([r['row'][3] for r in cd],[11,19,20,21,22,23,32,14,30,31,32,14])
        self.assertEqual([r['index'] for r in cd],list(range(211,223)))
        self.assertTrue(all(r['row'][0]==0 for r in cd))
        self.assertFalse({33,34,35}&{r['row'][3] for r in native['rows'] if not r['sentinel']})
    def test_actual_sites_and_ambiguity_coverage(self):
        p=json.loads((HERE/'static-draw-sites.json').read_bytes())
        rows=[dict(zip(p['draw_site_columns'],r)) for r in p['draw_sites']]
        self.assertEqual(len(rows),15368)
        self.assertEqual(sum(r['resource'] is not None for r in rows),11441)
        self.assertEqual(sum(not r['resource_candidates'] for r in rows),19)
        self.assertEqual({r['ttm'] for r in rows if not r['resource_candidates']},{'GJLILIPU.TTM','GJVIS5.TTM'})
        self.assertTrue(all(r['resource'] is None for r in rows if len(r['resource_candidates'])>1))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['smoke','regression'],required=True);args=p.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Smoke if args.phase=='smoke' else Regression)
    raise SystemExit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
