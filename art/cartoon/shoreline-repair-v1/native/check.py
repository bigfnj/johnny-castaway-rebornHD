"""Bounded copied-input checks for the new shoreline package and phase guards."""
import argparse
from pathlib import Path
import tempfile
import zipfile

from capture import ROOT, WAVES, native, outside_waves, package_pair, require, save, sha, wave_log


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--phase-probe', type=Path, required=True)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    require(not args.report.exists(), 'fresh check report required')
    log = (args.phase_probe / 'capture.log').read_text()
    record = wave_log(log)
    metadata = native.selected_archive(args.baseline)
    require(len(metadata['new_cartoon_members']) == 4, 'four restored props in test baseline')
    report = {'status': 'PASS', 'phase': args.phase, 'capture_helper_sha256': sha((Path(__file__).parent / 'capture.py').read_bytes()),
              'checker_sha256': sha(Path(__file__).read_bytes()), 'baseline_sha256': sha(args.baseline.read_bytes()),
              'actual_log_sha256': sha((args.phase_probe / 'capture.log').read_bytes()), 'checks': []}
    if args.phase == 'smoke':
        report['checks'] = ['actual native final phases and registered canvases', 'all production payloads and four seasonal additions retained']
    else:
        def refuses(label, call, message):
            try:
                call()
            except ValueError as error:
                require(str(error) == 'seasonal: ' + message, 'named control failure:' + label)
                report['checks'].append({'name': label, 'status': 'FIRED', 'failure': str(error)})
            else:
                raise ValueError('control survived:' + label)
        refuses('wrong_final_frame', lambda: wave_log(log.replace('SHORE DRAW: frame=7 ', 'SHORE DRAW: frame=8 ')), 'final native wave phases 003/007/009')
        refuses('wrong_wave_origin', lambda: wave_log(log.replace('SHORE DRAW: frame=7 x=364 ', 'SHORE DRAW: frame=7 x=365 ')), 'actual wave canvas/origin')
        with zipfile.ZipFile(args.baseline) as archive:
            unchanged = {info.filename: archive.read(info.filename) for info in archive.infolist()}
        selected = dict(unchanged)
        for frame in WAVES:
            # Valid same-canvas HD bytes exercise the replacement branch as a test fixture only.
            selected[f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'] = unchanged[f'data/hd/BMP/BACKGRND.BMP/{frame:03}.png']
        with tempfile.TemporaryDirectory(prefix='shore-guards-') as scratch:
            def archive(name, members, duplicate=None):
                path = Path(scratch) / (name + '.zip')
                with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as target:
                    for key, value in members.items():
                        target.writestr(key, value)
                    if duplicate:
                        target.writestr(duplicate, members[duplicate])
                return path
            good = archive('positive', selected)
            package_pair(args.baseline, good)
            report['checks'].append({'name': 'valid_three_replacement_fixture', 'status': 'PASS', 'scope': 'HD wave bytes in a temporary guard fixture; not proposed artwork.'})
            protected_name = 'data/RESOURCE.MAP'
            bad = dict(selected, **{protected_name: selected[protected_name] + b'changed'})
            bad_path = archive('damaged-retained', bad)
            refuses('retained_payload_changed', lambda: package_pair(args.baseline, bad_path), 'only three selected wave payloads changed')
            bad = dict(selected)
            del bad[protected_name]
            bad_path = archive('missing', bad)
            refuses('retained_member_missing', lambda: package_pair(args.baseline, bad_path), 'candidate member set unchanged')
            bad_path = archive('duplicate', selected, protected_name)
            refuses('duplicate_member', lambda: package_pair(args.baseline, bad_path), 'candidate duplicate members')
            member = 'data/styles/cartoon/BMP/BACKGRND.BMP/003.png'
            bad = dict(selected, **{member: selected['data/styles/cartoon/BMP/BACKGRND.BMP/007.png']})
            bad_path = archive('wrong-canvas', bad)
            refuses('wrong_wave_canvas', lambda: package_pair(args.baseline, bad_path), 'wave fixed canvas:' + member)
            package_pair(args.baseline, good)
        # Preserve the observed scene; change a copied pixel inside the allowed rectangle.
        spec = native.importlib.util.spec_from_file_location('shore_check_codec', native.CODEC)
        codec = native.importlib.util.module_from_spec(spec)
        spec.loader.exec_module(codec)
        before = codec.ppm(args.phase_probe / 'final.ppm')
        inside = bytearray(before)
        inside[(612*1280+540)*3] ^= 1
        outside_waves(before, bytes(inside))
        bad = bytearray(inside)
        bad[0] ^= 1
        refuses('outside_wave_pixel', lambda: outside_waves(before, bytes(bad)), 'changed pixel outside selected wave canvases')
        refuses('no_visible_change', lambda: outside_waves(before, before), 'repair visibly changed native scene')
        outside_waves(before, bytes(inside))
        require(wave_log(log) == record, 'restored native log positive')
        report['positive_readback_after_controls'] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    save(args.report, report)
    print(f"PASS {args.phase}: {len(report['checks'])} checks; executed capture helper {report['capture_helper_sha256']}")


if __name__ == '__main__':
    main()
