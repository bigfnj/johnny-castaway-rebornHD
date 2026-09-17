def render(recipe, preview_only):
    base = load_base()
    row = recipe['frames'][0]
    source_path = HERE / row['source']
    pass  # executed control: registration binding removed
    with Image.open(source_path) as image:
        source = image.copy()
    alpha = source.getchannel('A')
    box = alpha.point(lambda v: 255 if v >= 8 else 0).getbbox()
    s, _, tx, _, _, ty = row['affine_forward']
    centers = [(box[0]+.5)*s+tx, (box[1]+.5)*s+ty,
               (box[2]-.5)*s+tx, (box[3]-.5)*s+ty]
    w, h = row['runtime_canvas']
    padded = base.resample(source, [w, h], row['affine_forward'])
    outside = padded.getchannel('A')
    outside.paste(0, (base.PAD, base.PAD, base.PAD+w, base.PAD+h))
    fits = (0 <= centers[0] < centers[2] < w and 0 <= centers[1] < centers[3] < h
            and outside.getextrema()[1] < 8)
    if not preview_only:
        base.require(fits, '003: meaningful source or filtered alpha overhang')
    crop = padded.crop((base.PAD, base.PAD, base.PAD+w, base.PAD+h))
    output_name = row['path'] if fits else 'diagnostic-crop/003.png'
    outputs = {'padded/003.png': base.png(padded), output_name: base.png(crop)}
    prior = json.loads((PARENT / 'recipe-v5.json').read_bytes())
    unchanged = {}
    for old in prior['frames'][:3]:
        data = (PARENT / 'candidates/v5' / old['path']).read_bytes()
        unchanged[old['path']] = sha(data)
        if fits:
            outputs[old['path']] = data
    edges = {'top': (0, 0, padded.width, base.PAD),
             'bottom': (0, base.PAD+h, padded.width, padded.height),
             'left': (0, base.PAD, base.PAD, base.PAD+h),
             'right': (base.PAD+w, base.PAD, padded.width, base.PAD+h)}
    edge_stats = {}
    for edge, bounds in edges.items():
        a = padded.getchannel('A').crop(bounds)
        edge_stats[edge] = {'nonzero_pixels': sum(a.histogram()[1:]),
                            'alpha8_pixels': sum(a.histogram()[8:]),
                            'maximum_alpha': a.getextrema()[1]}
    filtered = padded.getchannel('A').point(lambda v: 255 if v >= 8 else 0).getbbox()
    report = {'schema_version': 1, 'accepted': False,
              'status': 'FIT_PASS_PENDING_NATIVE_REVIEW' if fits else 'REJECTED_MEANINGFUL_OVERHANG',
              'runtime_ready': fits, 'preview_only': preview_only,
              'exporter_sha256': sha(Path(__file__).read_bytes()),
              'reused_exporter_sha256': BASE_SHA, 'parent_recipe_sha256': V5_SHA,
              'recipe_sha256': sha(base.encode(recipe)), 'pillow_version': PIL.__version__,
              'frame': 3, 'source_sha256': row['source_sha256'],
              'runtime_canvas': [w, h], 'affine_forward': row['affine_forward'],
              'source_alpha8_bounds': list(box), 'alpha8_source_centers_hd': centers,
              'filtered_alpha8_bounds_hd': [v-base.PAD for v in filtered],
              'outside_runtime_max_alpha': outside.getextrema()[1],
              'outside_runtime_alpha8_pixels': sum(outside.histogram()[8:]),
              'outside_runtime_nonzero_pixels': sum(outside.histogram()[1:]),
              'outside_by_edge': edge_stats, 'unchanged_v5_props_sha256': unchanged,
              'outputs_sha256': {name: sha(data) for name, data in outputs.items()}}
    return outputs, report
