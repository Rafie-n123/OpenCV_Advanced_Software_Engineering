import xml.etree.ElementTree as ET
import csv
import sys

SRC_NS = 'http://www.srcML.org/srcML/src'
CPP_NS = 'http://www.srcML.org/srcML/cpp'

UNIT = f'{{{SRC_NS}}}unit' # in which file are we
INCLUDE = f'{{{CPP_NS}}}include' # include statement
FILE = f'{{{CPP_NS}}}file' # which file is included
CALL = f'{{{SRC_NS}}}call' # function call
NAME = f'{{{SRC_NS}}}name' # name of the function that is called
CLASS = f'{{{SRC_NS}}}class' # definition of a class (Source of inheritance)
STRUCT = f'{{{SRC_NS}}}struct' # definition of a struct (Source of inheritance)
SUPER = f'{{{SRC_NS}}}super' # inheritance list (contains the Parent/Target class)

ET.register_namespace('cpp', CPP_NS)
ET.register_namespace('src', SRC_NS)

def extract_dependencies(xml_file_path, output_csv_path):
    print(f"Processing file: {xml_file_path} ...")
    
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
                print("Error: XML file empty.")
                return

            for event, elem in context:
                
                if event == "start":
                    if elem.tag == UNIT and 'filename' in elem.attrib:
                        current_file = elem.attrib['filename']
                        
                if event == "end":
                    
                    if elem.tag == INCLUDE:
                        file_tag = elem.find(FILE)
                        if file_tag is not None and file_tag.text:
                            dep_target = file_tag.text.strip('"<> ')
                            writer.writerow([current_file, dep_target, "include"])
                        elem.clear()

                    elif elem.tag == CLASS or elem.tag == STRUCT:
                        class_name_tag = elem.find(f'{NAME}')
                        source_name = class_name_tag.text if class_name_tag is not None else "Anonymous"

                        super_tag = elem.find(SUPER)
                        if super_tag is not None:
                            base_name_tag = super_tag.find(f'.//{NAME}')
                            if base_name_tag is not None and base_name_tag.text:
                                base_name = base_name_tag.text.strip()
                                writer.writerow([f"{current_file}::{source_name}", base_name, "inherit"])
                        
                        elem.clear()

                    elif elem.tag == CALL:
                        name_tag = elem.find(NAME)
                        if name_tag is not None and name_tag.text:
                            writer.writerow([current_file, name_tag.text, "call"])
                        elem.clear()

                    elif elem.tag == UNIT:
                        elem.clear()
                        if root is not None:
                            root.clear()

            if root is not None:
                root.clear()
            print(f"Done. Results saved in:  {output_csv_path}")

    except FileNotFoundError:
        print(f"Error: File '{xml_file_path}' not found.")
    except Exception as e:
        print(f"An Error ocurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Use: python opencv_parser.py <input_xml> <output_csv>")
        sys.exit(1)
    
    extract_dependencies(sys.argv[1], sys.argv[2])