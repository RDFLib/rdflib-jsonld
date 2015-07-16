
class AutoFrame(object):
    def __init__(self, data):
        self.context = data.get('@context')
        self.graph_key = '@graph'
        self.id_key = '@id'
        self.rev_key = '@reverse'
        self.embedded = set()
        self.itemmap = {}
        self.revmap = {}
        self.reembed = True
        self.pending_revs = []
        for item in data.get(self.graph_key, ()):
            for p, objs in item.items():
                if p == self.id_key:
                    self.itemmap[objs] = item
                else:
                    if not isinstance(objs, list):
                        objs = [objs]
                    for o in objs:
                        if not isinstance(o, dict):
                            continue
                        target_id = o.get(self.id_key)
                        self.revmap.setdefault(target_id, {}
                                ).setdefault(p, []).append(item)

    def run(self, main_id):
        main_item = self.itemmap.get(main_id)
        if not main_item:
            return None
        self.embed(main_id, main_item, set(), self.reembed)
        self.add_reversed()
        if self.context:
            main_item['@context'] = self.context
        return main_item

    def embed(self, item_id, item, embed_chain, reembed):
        self.embedded.add(item_id)
        embed_chain.add(item_id)
        for p, o in item.items():
            item[p] = self.to_embedded(o, embed_chain, reembed)
        revs = self.revmap.get(item_id)
        if revs:
            self.pending_revs.append((item, embed_chain, revs))

    def add_reversed(self):
        for item, embed_chain, revs in self.pending_revs:
            for p, subjs in revs.items():
                for subj in subjs:
                    subj_id = subj.get(self.id_key)
                    if subj_id and subj_id not in embed_chain:
                        if subj_id not in self.embedded:
                            item.setdefault(self.rev_key, {}
                                    ).setdefault(p, []).append(subj)
                            self.embed(subj_id, subj, set(embed_chain), False)

    def to_embedded(self, o, embed_chain, reembed):
        if isinstance(o, list):
            return [self.to_embedded(lo, embed_chain, reembed) for lo in o]
        if isinstance(o, dict):
            o_id = o.get(self.id_key)
            if o_id and o_id not in embed_chain and (
                    reembed or o_id not in self.embedded):
                obj = self.itemmap.get(o_id)
                if obj:
                    self.embed(o_id, obj, set(embed_chain), reembed)
                    return obj
        return o


def autoframe(data, main_id):
    return AutoFrame(data).run(main_id) or data


if __name__ == '__main__':
    import json
    import sys
    import argparse
    args = sys.argv[1:]
    src = args.pop(0)
    main_id = args.pop(0)
    if src == '-':
        fp = sys.stdin
    else:
        fp = open(src)
    data = json.load(fp)
    framed = autoframe(data, main_id)
    sys.stdout.write(json.dumps(framed, indent=2, separators=(',', ': '),
            ensure_ascii=False).encode('utf-8'))
