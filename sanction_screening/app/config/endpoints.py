"""API endpoints and data sources for sanctions lists"""

# OFAC (Office of Foreign Assets Control - US Treasury)
OFAC_SDN_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"
OFAC_CONSOLIDATED_URL = "https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml"

# UN (United Nations Security Council)
UN_CONSOLIDATED_URL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"

# HMT (Her Majesty's Treasury - UK)
HMT_CONSOLIDATED_URL = "https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv"

# EU (European Union)
EU_CONSOLIDATED_URL = "https://webgate.ec.europa.eu/europeaid/fsd/fsf/public/files/csvFullSanctionsList/content"

# Headers for API requests
REQUEST_HEADERS = {
    "User-Agent": "SLST-Compliance-Tool/1.0",
    "Accept": "application/xml,text/csv,*/*"
}