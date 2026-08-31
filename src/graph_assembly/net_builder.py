"""net_builder.py: Disjoint Set Union (DSU) Electrical Net Reconstruction."""

from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict
from src.common.schemas import Component, WireSegment, SkeletonGraphData
from src.wire_tracing.endpoint_matching import EndpointMatcher
from src.common.utils import euclidean_dist


class DisjointSetUnion:
    """Standard DSU / Union-Find with path compression and union by rank."""

    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}

    def find(self, item: str) -> str:
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0
            return item
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, item1: str, item2: str) -> None:
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 != root2:
            if self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            elif self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1


class NetBuilder:
    """Assembles electrical nets by linking wire paths, junctions, and matched terminals."""

    def __init__(self, endpoint_matcher: Optional[EndpointMatcher] = None):
        self.matcher = endpoint_matcher or EndpointMatcher()

    def build_nets(
        self,
        components: List[Component],
        skeleton_data: SkeletonGraphData
    ) -> Dict[str, List[str]]:
        """Constructs electrical nets mapping net_id -> list of terminal references ('CompID.TermID')."""
        dsu = DisjointSetUnion()
        matched_terminals: Set[str] = set()

        # 1. Match start and end of each wire segment to components or junctions
        for wire in skeleton_data.wire_segments:
            start_pt = wire.start_point
            end_pt = wire.end_point

            # Match start endpoint
            m_start = self.matcher.match_endpoint_to_terminals(start_pt, wire.points, components)
            start_node_key = f"{m_start[0]}.{m_start[1]}" if m_start else f"wire_{wire.id}_start"
            if m_start:
                matched_terminals.add(start_node_key)

            # Match end endpoint
            m_end = self.matcher.match_endpoint_to_terminals(end_pt, wire.points[::-1], components)
            end_node_key = f"{m_end[0]}.{m_end[1]}" if m_end else f"wire_{wire.id}_end"
            if m_end:
                matched_terminals.add(end_node_key)

            # Wire segment unites its two ends
            dsu.union(start_node_key, end_node_key)

            # 2. Check if wire ends touch junctions
            for junc in skeleton_data.junctions:
                if euclidean_dist(start_pt, junc.position) < 10.0:
                    dsu.union(start_node_key, f"junc_{junc.id}")
                if euclidean_dist(end_pt, junc.position) < 10.0:
                    dsu.union(end_node_key, f"junc_{junc.id}")

        # 3. Group terminals by root net in DSU
        groups = defaultdict(list)
        for term_ref in sorted(matched_terminals):
            root = dsu.find(term_ref)
            groups[root].append(term_ref)

        # 4. Form canonical NET1, NET2, ... dictionary
        nets: Dict[str, List[str]] = {}
        net_idx = 1
        for root, term_list in sorted(groups.items(), key=lambda x: x[0]):
            if len(term_list) >= 2:
                # True electrical net connecting 2 or more terminals
                net_id = f"NET{net_idx}"
                nets[net_id] = sorted(term_list)
                net_idx += 1
            elif len(term_list) == 1:
                # Floating/single-terminal net
                net_id = f"NET{net_idx}"
                nets[net_id] = term_list
                net_idx += 1

        # 5. Update connected_net attribute on component terminals
        term_to_net = {}
        for nid, t_list in nets.items():
            for t_ref in t_list:
                term_to_net[t_ref] = nid

        for comp in components:
            for term in comp.terminals:
                ref = f"{comp.id}.{term.id}"
                term.connected_net = term_to_net.get(ref, None)

        return nets
