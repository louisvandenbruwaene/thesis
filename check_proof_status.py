"""Check proof ownership and status in the thesis's mathematical environments."""

import re

KINDS = "theorem|proposition|lemma|corollary|claim|construction|conjecture"
EVENT = re.compile(r"\\(begin|end)\{(" + KINDS + r"|proof)\}|\\(?:sub)*section\*?\{")
TITLE = re.compile(r"\s*(\[(?:[^][]|\[[^]]*\])*\])?")
LABEL = re.compile(r"\s*\\label\{([^}]+)\}")


def strip_comments(source):
    # An even number of preceding backslashes leaves % as a comment marker.
    return re.sub(r"(?<!\\)((?:\\\\)*)%[^\n]*", r"\1", source)


def check_proof_status(sources, proof_source="chapters/app_proofs.tex"):
    statements, proofs, errors = {}, {}, []
    for filename, raw in sources.items():
        source = strip_comments(raw)
        stack, pending = [], None
        for event in EVENT.finditer(source):
            action, kind = event.groups()
            if action is None:  # A new section cannot inherit an inline proof owner.
                pending = None
                continue
            if action == "begin":
                header = TITLE.match(source, event.end())
                title = (header.group(1) or "")[1:-1]
                start = header.end()
                label_match = LABEL.match(source, start)
                label = label_match.group(1) if label_match else None
                owner = None
                if kind == "proof":
                    targets = re.findall(r"\\Cref\{([^}]+)\}", title)
                    # A named proof belongs exclusively to its explicit target.
                    owner = [x.strip() for t in targets for x in t.split(",")] if targets else ([pending] if pending else [])
                pending = None
                stack.append((kind, title, label, start, owner))
            elif not stack or stack[-1][0] != kind:
                errors.append(f"UNBALANCED PROOF ENVIRONMENT: {filename}: {kind}")
            else:
                _, title, label, start, owner = stack.pop()
                if kind == "proof":
                    if filename == proof_source and source[start:event.start()].strip():
                        for target in owner:
                            proofs.setdefault(target, []).append(title)
                    pending = None
                else:
                    if label:
                        statements[label] = (kind, title)
                    elif kind == "conjecture":
                        errors.append(f"UNLABELLED CONJECTURE: {filename}")
                    pending = label
        if stack:
            errors.append(f"UNCLOSED PROOF ENVIRONMENT: {filename}: {stack[-1][0]}")

    for label, (kind, title) in statements.items():
        if r"\aimedal" in title or r"\conditional" in title:
            if kind != "conjecture" or "with proof" not in title:
                errors.append(f"UNQUALIFIED PROOF STATUS: {label}")
        if kind != "conjecture":
            continue
        expected = "Conditional proof" if r"\conditional" in title else "Proposed proof"
        headings = proofs.get(label, [])
        if "with proof" in title and not headings:
            errors.append(f"CONJECTURE WITHOUT PROOF: {label}")
        for heading in headings:
            if not heading.startswith(expected):
                errors.append(f"PROOF STATUS DESYNC: {label}: {heading}")
    return errors
