import os
import zipfile
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

class EPUBReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_dir = "temp_epub_extract"
        self.content = {}
        
    def extract_epub(self):
        """Extract EPUB file to a temporary directory"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
    
    def parse_container(self):
        """Parse container.xml to find the OPF file location"""
        container_path = os.path.join(self.temp_dir, 'META-INF', 'container.xml')
        if not os.path.exists(container_path):
            raise FileNotFoundError("container.xml not found in the EPUB file")
            
        tree = ET.parse(container_path)
        root = tree.getroot()
        
        # Find the rootfile with the OPF content
        for elem in root.iter('{urn:oasis:names:tc:opendocument:xmlns:container}rootfile'):
            if elem.get('media-type') == 'application/oebps-package+xml':
                return os.path.join(self.temp_dir, elem.get('full-path'))
    
    def parse_opf(self, opf_path):
        """Parse the OPF file to get book metadata and content"""
        opf_dir = os.path.dirname(opf_path)
        
        # Parse the OPF file
        tree = ET.parse(opf_path)
        root = tree.getroot()
        
        # Register namespaces
        namespaces = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        # Extract metadata
        metadata = {}
        for meta in root.findall('.//dc:title', namespaces):
            metadata['title'] = meta.text
        for meta in root.findall('.//dc:creator', namespaces):
            metadata['author'] = meta.text
        for meta in root.findall('.//dc:language', namespaces):
            metadata['language'] = meta.text
            
        # Find the spine (reading order)
        spine = root.find('.//opf:spine', namespaces)
        itemrefs = spine.findall('.//opf:itemref', namespaces)
        
        # Get manifest items
        manifest = {}
        for item in root.findall('.//opf:manifest/opf:item', namespaces):
            item_id = item.get('id')
            href = item.get('href')
            media_type = item.get('media-type', '')
            manifest[item_id] = {
                'href': os.path.normpath(os.path.join(opf_dir, href)),
                'media_type': media_type
            }
        
        # Extract text content in reading order
        content_parts = []
        for itemref in itemrefs:
            item_id = itemref.get('idref')
            if item_id in manifest:
                item = manifest[item_id]
                if item['media_type'] == 'application/xhtml+xml':
                    with open(item['href'], 'r', encoding='utf-8') as f:
                        html_content = f.read()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        text = soup.get_text(separator='\n', strip=True)
                        content_parts.append(text)
        
        metadata['content'] = '\n\n'.join(content_parts)
        return metadata
    
    def read_epub(self):
        """Main method to read an EPUB file"""
        try:
            self.extract_epub()
            opf_path = self.parse_container()
            if not opf_path:
                raise ValueError("Could not find OPF file in the EPUB")
                
            metadata = self.parse_opf(opf_path)
            return metadata
            
        except Exception as e:
            print(f"Error reading EPUB file: {str(e)}")
            return None
            
        finally:
            # Clean up temporary files
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)

# Helper function to detect if a file is an EPUB
def is_epub(file_path):
    """Check if a file is an EPUB by checking its magic number"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(58)  # EPUBCheck uses 58 bytes for signature
            return header.startswith(b'PK\x03\x04') and b'mimetype' in header and b'application/epub+zip' in header
    except:
        return False
