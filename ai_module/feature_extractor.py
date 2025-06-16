import torch
import numpy as np
from typing import Dict, List, Set
import networkx as nx
from llvmlite import ir
import re

class FeatureExtractor:
    """Extracts features from LLVM IR for machine learning models."""
    
    def __init__(self, config: Dict = None):
        """Initialize the feature extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.instruction_types = {
            'alloca', 'load', 'store', 'add', 'sub', 'mul',
            'sdiv', 'udiv', 'srem', 'urem', 'and', 'or', 'xor',
            'shl', 'lshr', 'ashr', 'icmp', 'fcmp', 'phi', 'call',
            'select', 'getelementptr', 'bitcast', 'zext', 'sext'
        }
        
    def extract_features(self, ir_code: str) -> torch.Tensor:
        """Extract features from IR code.
        
        Args:
            ir_code: LLVM IR code as string
            
        Returns:
            Tensor of features
        """
        # Parse IR code into blocks
        blocks = self._parse_blocks(ir_code)
        
        # Extract different types of features
        instruction_features = self._extract_instruction_features(blocks)
        cfg_features = self._extract_cfg_features(blocks)
        memory_features = self._extract_memory_features(blocks)
        
        # Combine all features
        combined = np.concatenate([
            instruction_features,
            cfg_features,
            memory_features
        ])
        
        return torch.FloatTensor(combined)
    
    def _parse_blocks(self, ir_code: str) -> List[str]:
        """Parse IR code into basic blocks."""
        blocks = []
        current_block = []
        
        for line in ir_code.split('\n'):
            line = line.strip()
            if line.endswith(':'):  # New block
                if current_block:
                    blocks.append('\n'.join(current_block))
                current_block = [line]
            elif line:
                current_block.append(line)
        
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _extract_instruction_features(self, blocks: List[str]) -> np.ndarray:
        """Extract features related to instruction types and patterns."""
        # Count instruction types
        instruction_counts = {itype: 0 for itype in self.instruction_types}
        
        for block in blocks:
            for line in block.split('\n'):
                for itype in self.instruction_types:
                    if f'%{itype}' in line or f' {itype} ' in line:
                        instruction_counts[itype] += 1
        
        # Create feature vector
        features = []
        
        # Instruction type frequencies
        total_instructions = sum(instruction_counts.values()) or 1
        features.extend([count / total_instructions for count in instruction_counts.values()])
        
        # Instruction patterns
        features.extend([
            self._count_pattern(blocks, r'load.*store'),  # Load-store patterns
            self._count_pattern(blocks, r'alloca.*load'),  # Allocation-load patterns
            self._count_pattern(blocks, r'call.*call'),   # Consecutive calls
            self._count_pattern(blocks, r'icmp.*br'),     # Branch conditions
        ])
        
        return np.array(features, dtype=np.float32)
    
    def _extract_cfg_features(self, blocks: List[str]) -> np.ndarray:
        """Extract features from the control flow graph."""
        # Build CFG
        cfg = nx.DiGraph()
        current_block = None
        
        for block in blocks:
            # Get block label
            label = block.split(':')[0].strip()
            cfg.add_node(label)
            
            if current_block:
                # Add edge from previous block
                cfg.add_edge(current_block, label)
            
            # Check for branches
            if 'br' in block:
                # Extract branch targets
                targets = re.findall(r'label %(\w+)', block)
                for target in targets:
                    cfg.add_edge(label, target)
            
            current_block = label
        
        # Extract graph features
        features = [
            len(cfg.nodes),  # Number of basic blocks
            len(cfg.edges),  # Number of edges
            nx.number_of_selfloops(cfg),  # Number of loops
            len(list(nx.simple_cycles(cfg))),  # Number of cycles
            nx.number_connected_components(cfg.to_undirected()),  # Connected components
        ]
        
        # Calculate average shortest path length for the largest strongly connected component
        if len(cfg.nodes) > 1:
            largest_scc = max(nx.strongly_connected_components(cfg), key=len)
            if len(largest_scc) > 1:
                scc_graph = cfg.subgraph(largest_scc)
                features.append(nx.average_shortest_path_length(scc_graph))
            else:
                features.append(0)
        else:
            features.append(0)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_memory_features(self, blocks: List[str]) -> np.ndarray:
        """Extract features related to memory operations."""
        features = []
        
        # Count memory operations
        alloca_count = sum(line.count('alloca') for block in blocks for line in block.split('\n'))
        load_count = sum(line.count('load') for block in blocks for line in block.split('\n'))
        store_count = sum(line.count('store') for block in blocks for line in block.split('\n'))
        gep_count = sum(line.count('getelementptr') for block in blocks for line in block.split('\n'))
        
        total_mem_ops = alloca_count + load_count + store_count + gep_count or 1
        
        features.extend([
            alloca_count / total_mem_ops,
            load_count / total_mem_ops,
            store_count / total_mem_ops,
            gep_count / total_mem_ops,
            load_count / (store_count if store_count > 0 else 1),  # Load/store ratio
        ])
        
        return np.array(features, dtype=np.float32)
    
    def _count_pattern(self, blocks: List[str], pattern: str) -> float:
        """Count occurrences of a pattern in the IR code."""
        count = 0
        for block in blocks:
            count += len(re.findall(pattern, block, re.MULTILINE))
        return float(count) 