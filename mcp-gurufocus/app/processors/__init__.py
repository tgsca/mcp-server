# __init__.py für das Processors-Subpaket
# financials_api/processors/__init__.py
"""
Prozessoren für die Verarbeitung von Finanzdaten.
"""

from .stock_processor import StockProcessor
from .financials_processor import FinancialsProcessor
from .analyst_processor import AnalystProcessor
from .segments_processor import SegmentsProcessor
from .news_processor import NewsProcessor
from .report_generator import ReportGenerator
