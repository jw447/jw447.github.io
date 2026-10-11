"""Describe content changes without including sensitive contact values."""
def summarize_changes(before, after):
    changed = [name for name in before if before[name] != after[name]]
    lines = []
    for name in changed:
        old, new = before[name], after[name]
        if isinstance(old, dict) and isinstance(new, dict):
            fields = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
            lines.append(f"- {name}: update " + ', '.join(fields))
        elif isinstance(old, list) and isinstance(new, list):
            def key(item):
                return item.get('id') or item.get('name') or item.get('title') or item.get('text')
            a = {key(x): x for x in old}; b = {key(x): x for x in new}
            for k in b:
                if k not in a: lines.append(f"- {name}: add {k}")
                elif a[k] != b[k]:
                    fields = sorted(f for f in set(a[k]) | set(b[k]) if a[k].get(f) != b[k].get(f))
                    lines.append(f"- {name}: update {k} ({', '.join(fields)})")
            for k in a:
                if k not in b: lines.append(f"- {name}: remove {k}")
            if set(a) == set(b) and all(a[k] == b[k] for k in a): lines.append(f"- {name}: reorder entries")
        else: lines.append(f"- {name}: update content")
    return 'Update ' + ', '.join(changed) + '\n\n' + '\n'.join(lines)
