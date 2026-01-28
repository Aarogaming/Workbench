#!/usr/bin/env python3
"""
AAS-287: AI Context Summarization
Efficient extraction and compression of relevant contextual information
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import time


class SummarizationStrategy(Enum):
    """Different strategies for context summarization"""
    EXTRACTIVE = "extractive"
    ABSTRACTIVE = "abstractive"
    HYBRID = "hybrid"
    HIERARCHICAL = "hierarchical"


class SalienceModel(Enum):
    """Salience calculation models"""
    TF_IDF = "tfidf"
    PAGERANK = "pagerank"
    SEMANTIC = "semantic"
    RECENCY = "recency"


@dataclass
class ContextItem:
    """Single piece of context information"""
    content: str
    source: str
    timestamp: float = 0.0
    importance: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """Compare by importance"""
        return self.importance < other.importance


@dataclass
class SummaryConfig:
    """Configuration for summarization"""
    strategy: SummarizationStrategy = SummarizationStrategy.HYBRID
    salience_model: SalienceModel = SalienceModel.TF_IDF
    compression_ratio: float = 0.3
    min_length: int = 10
    max_length: int = 500
    preserve_order: bool = True
    include_metadata: bool = True


class ContextSummarizer:
    """Main summarization engine"""

    def __init__(self, config: Optional[SummaryConfig] = None):
        """Initialize summarizer with configuration"""
        self.config = config or SummaryConfig()
        self.context_history: List[ContextItem] = []

    def add_context(
            self, content: str, source: str,
            importance: float = 1.0,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add new context item"""
        item = ContextItem(
            content=content,
            source=source,
            timestamp=time.time(),
            importance=importance,
            metadata=metadata or {}
        )
        self.context_history.append(item)

    def _calculate_salience(
            self, items: List[ContextItem]) -> Dict[int, float]:
        """Calculate salience scores for context items"""
        salience = {}

        if self.config.salience_model == SalienceModel.RECENCY:
            max_time = max(
                (item.timestamp for item in items), default=0)
            for i, item in enumerate(items):
                time_delta = max_time - item.timestamp + 1
                salience[i] = item.importance / (1 + time_delta)

        elif self.config.salience_model == SalienceModel.SEMANTIC:
            for i, item in enumerate(items):
                base_imp = item.importance
                kw_count = len(item.metadata.get('keywords', []))
                kw_boost = kw_count * 0.1
                salience[i] = base_imp + kw_boost

        else:
            for i, item in enumerate(items):
                word_count = len(item.content.split())
                unique = len(set(item.content.split()))
                uniqueness = unique / (word_count + 1)
                salience[i] = item.importance * uniqueness

        return salience

    def _extract_summary(
            self, items: List[ContextItem],
            target_length: int) -> List[ContextItem]:
        """Extract most salient items"""
        salience = self._calculate_salience(items)

        sorted_idx = sorted(
            salience.keys(),
            key=lambda x: salience[x],
            reverse=True)

        selected = []
        total_length = 0
        for idx in sorted_idx:
            item = items[idx]
            item_length = len(item.content.split())
            if total_length + item_length <= target_length:
                selected.append(item)
                total_length += item_length
            if total_length >= target_length * 0.8:
                break

        if self.config.preserve_order:
            selected.sort(key=lambda x: items.index(x))

        return selected

    def _abstract_summary(
            self, items: List[ContextItem],
            target_length: int) -> str:
        """Generate abstract summary (simplified)"""
        selected = self._extract_summary(items, target_length)
        summaries = []

        for item in selected:
            sentences = item.content.split('.')
            if sentences[0]:
                summaries.append(sentences[0].strip())

        return '. '.join(summaries[:3]) + '.'

    def summarize(
            self,
            items: Optional[List[ContextItem]] = None
    ) -> Dict[str, Any]:
        """Generate summary of context"""
        context = items or self.context_history
        if not context:
            return {
                'summary': '',
                'strategy': self.config.strategy.value,
                'item_count': 0,
                'compression_ratio': 1.0
            }

        original_length = sum(
            len(item.content.split()) for item in context)
        target_length = max(
            self.config.min_length,
            int(original_length * self.config.compression_ratio)
        )
        target_length = min(target_length, self.config.max_length)

        if self.config.strategy == SummarizationStrategy.EXTRACTIVE:
            selected = self._extract_summary(context, target_length)
            summary_text = ' '.join(item.content for item in selected)

        elif self.config.strategy == SummarizationStrategy.ABSTRACTIVE:
            summary_text = self._abstract_summary(
                context, target_length)
            selected = context

        else:
            selected = self._extract_summary(context, target_length)
            summary_text = ' '.join(item.content for item in selected)

        final_length = len(summary_text.split())
        compression = original_length / (final_length + 1)

        result = {
            'summary': summary_text,
            'strategy': self.config.strategy.value,
            'item_count': len(selected),
            'compression_ratio': compression,
            'original_tokens': original_length,
            'summary_tokens': final_length
        }

        if self.config.include_metadata:
            result['sources'] = list(
                set(item.source for item in selected))
            result['metadata'] = [item.metadata for item in selected]

        return result

    def hierarchical_summarize(self) -> Dict[str, Any]:
        """Multi-level hierarchical summarization"""
        level1_config = SummaryConfig(compression_ratio=0.5)
        level1 = ContextSummarizer(level1_config)

        for item in self.context_history:
            level1.add_context(
                item.content, item.source,
                item.importance, item.metadata)

        level1_summary = level1.summarize()
        level1_items = [
            ContextItem(
                content=level1_summary['summary'],
                source='level1_summary',
                importance=2.0
            )
        ]

        level2 = ContextSummarizer(self.config)
        for item in level1_items:
            level2.add_context(
                item.content, item.source,
                item.importance, item.metadata)

        level2_result = level2.summarize()
        return {
            'level1': level1_summary,
            'level2': level2_result,
            'total_compression': (
                level1_summary['compression_ratio'] *
                level2_result['compression_ratio']
            )
        }

    def clear(self) -> None:
        """Clear context history"""
        self.context_history.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get summarizer statistics"""
        if not self.context_history:
            return {'total_items': 0, 'total_tokens': 0}

        total_tokens = sum(
            len(item.content.split())
            for item in self.context_history)
        return {
            'total_items': len(self.context_history),
            'total_tokens': total_tokens,
            'avg_importance': (
                sum(item.importance
                    for item in self.context_history) /
                len(self.context_history)
            ),
            'sources': list(
                set(item.source
                    for item in self.context_history))
        }
