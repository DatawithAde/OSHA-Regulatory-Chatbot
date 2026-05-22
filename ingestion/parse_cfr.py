import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import re

@dataclass
class CFRSection:
    section_number: str
    section_title: str
    subpart: str
    subpart_title: str
    part: str = "29"
    text: str = ""
    paragraphs: list = field(default_factory=list)

    @property
    def citation(self):
        return f"29 CFR § {self.section_number}"

    @property
    def full_metadata(self):
        return {
            "section_number": self.section_number,
            "section_title": self.section_title,
            "subpart": self.subpart,
            "subpart_title": self.subpart_title,
            "citation": self.citation,
            "source": "29 CFR",
            "part": self.part,
        }

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def get_all_text(element):
    return clean_text(' '.join(element.itertext()))

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

def parse_ecfr_xml(xml_path):
    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    sections = []
    current_subpart = "General"
    current_subpart_title = ""

    for elem in root.iter():
        tag = strip_ns(elem.tag)

        if tag == 'DIV':
            div_type = elem.get('TYPE', '').upper()

            if div_type == 'SUBPART':
                head = elem.find('HEAD')
                if head is not None:
                    head_text = get_all_text(head)
                    match = re.match(r'Subpart\s+([A-Z]+)\s*[—\-]\s*(.*)', head_text)
                    if match:
                        current_subpart = match.group(1)
                        current_subpart_title = match.group(2).strip()
                    else:
                        current_subpart_title = head_text

            elif div_type == 'SECTION':
                section_number = ""
                section_title = ""
                paragraphs = []

                head = elem.find('HEAD')
                if head is not None:
                    head_text = get_all_text(head)
                    match = re.match(r'[§\s]*(\d+\.\d+\w*)\s*(.*)', head_text)
                    if match:
                        section_number = match.group(1).strip()
                        section_title = match.group(2).strip().rstrip('.')

                if not section_number:
                    continue

                for child in elem.iter():
                    child_tag = strip_ns(child.tag)
                    if child_tag in ('P', 'FP', 'FP-1', 'FP-2'):
                        para = get_all_text(child)
                        if para and len(para) > 10:
                            paragraphs.append(para)

                full_text = f"§ {section_number} - {section_title}\n\n" + '\n\n'.join(paragraphs)
                sections.append(CFRSection(
                    section_number=section_number,
                    section_title=section_title,
                    subpart=current_subpart,
                    subpart_title=current_subpart_title,
                    text=full_text,
                    paragraphs=paragraphs,
                ))

    if len(sections) == 0:
        print("  Trying N-attribute fallback...")
        for elem in root.iter():
            tag = strip_ns(elem.tag)
            if tag in ('DIV6', 'DIV7', 'DIV8'):
                n_val = elem.get('N', '')
                if re.match(r'\d+\.\d+', n_val):
                    head = elem.find('HEAD')
                    section_title = get_all_text(head).rstrip('.') if head is not None else ""
                    paragraphs = []
                    for child in elem.iter():
                        child_tag = strip_ns(child.tag)
                        if child_tag in ('P', 'FP', 'FP-1'):
                            para = get_all_text(child)
                            if para and len(para) > 10:
                                paragraphs.append(para)
                    full_text = f"§ {n_val} - {section_title}\n\n" + '\n\n'.join(paragraphs)
                    sections.append(CFRSection(
                        section_number=n_val,
                        section_title=section_title,
                        subpart=current_subpart,
                        subpart_title=current_subpart_title,
                        text=full_text,
                        paragraphs=paragraphs,
                    ))

    print(f"Parsed {len(sections)} sections")
    return sections