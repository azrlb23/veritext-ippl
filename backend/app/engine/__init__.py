from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.tier1_lexical import (
    WinnowingLexicalEngine,
    LexicalAnalysisResult,
    SentenceLexicalMatch,
)
from app.engine.tier2_semantic import (
    SemanticEngine,
    SemanticAnalysisResult,
    SentenceSemanticMatch,
)
from app.engine.tier3_stylometric import (
    StylometricEngine,
    StylometricAnalysisResult,
    StylometricSentenceAnomaly,
)
from app.engine.tier4_aggregator import (
    HybridAggregator,
    HybridAuditResult,
    HeatmapAnnotationData,
    MatchedSourceData,
)
from app.engine.reference_corpus import (
    ReferenceCorpusBank,
    BUILTIN_REFERENCE_PAPERS,
)

__all__ = [
    "SentenceSpan",
    "TextPreprocessor",
    "WinnowingLexicalEngine",
    "LexicalAnalysisResult",
    "SentenceLexicalMatch",
    "SemanticEngine",
    "SemanticAnalysisResult",
    "SentenceSemanticMatch",
    "StylometricEngine",
    "StylometricAnalysisResult",
    "StylometricSentenceAnomaly",
    "HybridAggregator",
    "HybridAuditResult",
    "HeatmapAnnotationData",
    "MatchedSourceData",
    "ReferenceCorpusBank",
    "BUILTIN_REFERENCE_PAPERS",
]
