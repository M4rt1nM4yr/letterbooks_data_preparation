import os
import glob

# Define the replacement dictionary
replace_dict = {
    'å': 'ä',                      # å to ä
    u'\u0065\u0308': u'\u00eb',    # ë to ë
    u'\u0045\u0308': u'\u00cb',    # Ë to Ë
    u'\u0079\u0308': u'\u00ff',    # ÿ to ÿ
    u'\u0059\u0308': u'\u0178',    # Ÿ to Ÿ
    u'\u006f\u0308': '\u00f6',     # ö to ö
    u'\u0077\u0308': u'\u1e85',    # ẅ to ẅ
    u'\u0057\u0308': u'\u1e84',    # Ẅ to Ẅ
    u'\u0061\u0308': u'\u00e4',    # ä to ä
    u'\u0041\u0308': u'\u00c4',    # Ä to Ä
    u'u\u0308': u'\u00fc',         # ü to ü
    u'U\u0308': u'\u00dc',         # Ü to Ü
    "`": "",                       # ` to ""
}

# Function to replace characters in the text using the dictionary
def replace_characters(text):
    for old, new in replace_dict.items():
        text = text.replace(old, new)
    return text

# Function to process all .xml files in a given folder
def process_xml_files(folder_path):
    # Get all .xml files in the specified folder
    xml_files = glob.glob(os.path.join(folder_path, '*.xml'))

    for file_path in xml_files:
        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace characters
        new_content = replace_characters(content)

        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

        print(f"Processed file: {file_path}")

# Folder path where your .xml files are located
folder_paths = [
        'basic/Band2',
        'basic/Band3',
        'basic/Band4',
        'basic/Band5',
    ]

for folder_path in folder_paths:

    # Call the function to process all XML files in the folder
    process_xml_files(folder_path)

