import xml.etree.ElementTree as ET
import csv
import sys

SRC_NS = 'http://www.srcML.org/srcML/src'
CPP_NS = 'http://www.srcML.org/srcML/cpp'

FTN_UNIT = f'{{{SRC_NS}}}unit'
FTN_INCLUDE = f'{{{CPP_NS}}}include'
FTN_FILE = f'{{{CPP_NS}}}file'
FTN_CALL = f'{{{SRC_NS}}}call'
FTN_NAME = f'{{{SRC_NS}}}name'
FTN_CLASS = f'{{{SRC_NS}}}class'
FTN_STRUCT = f'{{{SRC_NS}}}struct'
FTN_SUPER = f'{{{SRC_NS}}}super'

ET.register_namespace('cpp', CPP_NS)
ET.register_namespace('src', SRC_NS)

def extract_dependencies(xml_file_path, output_csv_path):
    print(f"Verarbeite Datei: {xml_file_path} ...")
    
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Source', 'Target', 'Type'])

            current_file = "unknown"
            
            context = ET.iterparse(xml_file_path, events=("start", "end"))
            context = iter(context)
            
            try:
                event, root = next(context) 
            except StopIteration:
                print("Fehler: XML Datei ist leer.")
                return

            for event, elem in context:
                
                if event == "start":
                    if elem.tag == FTN_UNIT and 'filename' in elem.attrib:
                        current_file = elem.attrib['filename']
                        
                if event == "end":
                    
                    if elem.tag == FTN_INCLUDE:
                        file_tag = elem.find(FTN_FILE)
                        if file_tag is not None and file_tag.text:
                            dep_target = file_tag.text.strip('"<> ')
                            writer.writerow([current_file, dep_target, "include"])
                        elem.clear()

                    elif elem.tag == FTN_CLASS or elem.tag == FTN_STRUCT:
                        class_name_tag = elem.find(f'{FTN_NAME}')
                        source_name = class_name_tag.text if class_name_tag is not None else "Anonymous"

                        super_tag = elem.find(FTN_SUPER)
                        if super_tag is not None:
                            base_name_tag = super_tag.find(f'.//{FTN_NAME}')
                            if base_name_tag is not None and base_name_tag.text:
                                base_name = base_name_tag.text.strip()
                                writer.writerow([f"{current_file}::{source_name}", base_name, "inherit"])
                        
                        elem.clear()

                    elif elem.tag == FTN_CALL:
                        name_tag = elem.find(FTN_NAME)
                        if name_tag is not None and name_tag.text:
                            writer.writerow([current_file, name_tag.text, "call"])
                        elem.clear()

                    elif elem.tag == FTN_UNIT:
                        elem.clear()
                        if root is not None:
                            root.clear()

            if root is not None:
                root.clear()
            print(f"Fertig. Ergebnisse gespeichert in: {output_csv_path}")

    except FileNotFoundError:
        print(f"Fehler: Datei '{xml_file_path}' nicht gefunden.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung: python opencv_parser.py <input_xml> <output_csv>")
        sys.exit(1)
    
    extract_dependencies(sys.argv[1], sys.argv[2])