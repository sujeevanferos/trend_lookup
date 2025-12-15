
import sys
print(f"Python executable: {sys.executable}")
try:
    import lxml
    print(f"lxml version: {lxml.__version__}")
except ImportError:
    print("lxml not found")

try:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup("<root>test</root>", "xml")
    print("BeautifulSoup XML parsing successful")
except Exception as e:
    print(f"BeautifulSoup XML parsing failed: {e}")
