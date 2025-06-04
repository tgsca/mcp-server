# __init__.py für das Processors-Subpaket
# financials_api/processors/__init__.py
"""
Prozessoren für die Verarbeitung von Finanzdaten.
"""

from .stock_processor import StockProcessor as StockProcessor
from .financials_processor import FinancialsProcessor as FinancialsProcessor
from .analyst_processor import AnalystProcessor as AnalystProcessor
from .segments_processor import SegmentsProcessor as SegmentsProcessor
from .news_processor import NewsProcessor as NewsProcessor
from .report_generator import ReportGenerator as ReportGenerator
