from app.engine.ai_detector import GeminiAIDetector
from app.engine.preprocessor import SentenceSpan, TextPreprocessor
from app.engine.reference_corpus import (
    BUILTIN_REFERENCE_PAPERS,
    ReferenceCorpusBank,
)
from app.engine.tier1_lexical import (
    LexicalAnalysisResult,
    SentenceLexicalMatch,
    WinnowingLexicalEngine,
)
from app.engine.tier2_semantic import (
    SemanticAnalysisResult,
    SemanticEngine,
    SentenceSemanticMatch,
)
from app.engine.tier3_stylometric import (
    StylometricAnalysisResult,
    StylometricEngine,
    StylometricSentenceAnomaly,
)
from app.engine.tier4_aggregator import (
    HeatmapAnnotationData,
    HybridAggregator,
    HybridAuditResult,
    MatchedSourceData,
)
from app.engine.web_scanner import GeminiWebScanner, WebMatchResult

__all__ = [
    "BUILTIN_REFERENCE_PAPERS",
    "GeminiAIDetector",
    "GeminiWebScanner",
    "HeatmapAnnotationData",
    "HybridAggregator",
    "HybridAuditResult",
    "LexicalAnalysisResult",
    "MatchedSourceData",
    "ReferenceCorpusBank",
    "SemanticAnalysisResult",
    "SemanticEngine",
    "SentenceLexicalMatch",
    "SentenceSemanticMatch",
    "SentenceSpan",
    "StylometricAnalysisResult",
    "StylometricEngine",
    "StylometricSentenceAnomaly",
    "TextPreprocessor",
    "WebMatchResult",
    "WinnowingLexicalEngine",
]
