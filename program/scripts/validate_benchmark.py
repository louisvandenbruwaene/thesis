"""Independently validate saved witnesses using NetworkX, not the thesis checker."""

import argparse
import itertools
import json
from pathlib import Path
import sys
import time

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.equal_budget_benchmark import atomic_json, digest, now


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def validate(record):
    trial, witness = record["trial"], record["witness"]
    n, directed = trial["n"], trial["directed"]
    split = trial["separation"] == "vertex"
    network = nx.DiGraph()
    incoming, outgoing = [0]*n, [0]*n
    vin = lambda v: ("in", v) if split else ("v", v)
    vout = lambda v: ("out", v) if split else ("v", v)
    for v in range(n):
        network.add_node(vin(v))
        network.add_node(vout(v))
        if split:
            network.add_edge(vin(v), vout(v), capacity=1)
    if trial["hypergraph"]:
        edges = witness["hyperedges"]
        value, seen = len(edges), set()
        for index, edge in enumerate(edges):
            tails, heads = edge if directed else (edge, edge)
            for group in (tails, heads):
                if not group or any(not integer(v) or not 0 <= v < n for v in group):
                    raise ValueError("Invalid hyperedge members")
                if len(group) != len(set(group)):
                    raise ValueError("Repeated member in a hyperedge")
            if directed and (len(tails) != 1 or set(tails) & set(heads)):
                raise ValueError("Expected a disjoint forward tail/head split")
            if len(set(tails) | set(heads)) != 3:
                raise ValueError("Expected rank three")
            key = (tuple(sorted(tails)), tuple(sorted(heads)))
            if trial["simple"] and key in seen:
                raise ValueError("Repeated hyperedge in simple witness")
            seen.add(key)
            entry, exit_node = ("gate-in", index), ("gate-out", index)
            network.add_edge(entry, exit_node, capacity=1)
            for v in tails:
                network.add_edge(vout(v), entry, capacity=value+1)
                outgoing[v] += 1
            for v in heads:
                network.add_edge(exit_node, vin(v), capacity=value+1)
                incoming[v] += 1
    else:
        matrix = witness["multiplicity_matrix"]
        if len(matrix) != n or any(len(row) != n for row in matrix):
            raise ValueError("Incorrect matrix dimensions")
        for u, row in enumerate(matrix):
            for v, count in enumerate(row):
                if not integer(count) or count < 0 or (u == v and count):
                    raise ValueError("Invalid multiplicity")
                if trial["simple"] and count > 1:
                    raise ValueError("Repeated edge in simple witness")
                if not directed and count != matrix[v][u]:
                    raise ValueError("Asymmetric undirected matrix")
                if count:
                    network.add_edge(vout(u), vin(v), capacity=count)
                    outgoing[u] += count
                    incoming[v] += count
        value = sum(outgoing) if directed else sum(outgoing)//2
    if value != record["value"]:
        raise ValueError("Witness objective does not match saved count")
    pairs = itertools.permutations(range(n), 2) if directed else itertools.combinations(range(n), 2)
    # Endpoint degrees are proved upper bounds. Skip only pairs unable to raise
    # the exact maximum already measured, not pairs assumed to meet the cap.
    pairs = sorted(((min(outgoing[u], incoming[v]), u, v) for u, v in pairs), reverse=True)
    maximum = 0
    for bound, u, v in pairs:
        if bound <= maximum:
            continue
        measured = nx.maximum_flow_value(network, vout(u), vin(v),
                                         flow_func=nx.algorithms.flow.edmonds_karp)
        maximum = max(maximum, measured)
        if maximum >= trial["m"]:
            raise ValueError("Witness violates the route cap")
    if maximum != record["max_connectivity"]:
        raise ValueError("Independent connectivity disagrees with saved measurement")
    return dict(value=value, max_connectivity=maximum)


def audit(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    paths = [directory / "trials" / (t["id"] + ".json") for t in manifest["trials"]]
    paths += sorted((directory / "replacements" / "trials").glob("*.json"))
    entries, start = [], time.monotonic()
    for index, path in enumerate(paths):
        record = json.loads(path.read_text())
        result = validate(record)
        entries.append(dict(path=str(path.relative_to(directory)), sha256=digest(path), **result))
        if (index+1) % 32 == 0:
            print(f"Validated {index+1}/{len(paths)} witnesses", flush=True)
    atomic_json(directory / "witness_audit.json", dict(
        created_utc=now(), verifier_sha256=digest(__file__), networkx=nx.__version__,
        method="Independent per-copy gate construction and NetworkX Edmonds-Karp",
        original_manifest_sha256=digest(directory / "manifest.json"),
        elapsed_seconds=time.monotonic()-start, records=entries))
    print(f"All {len(entries)} saved witnesses passed independent validation", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    audit(parser.parse_args().directory)
