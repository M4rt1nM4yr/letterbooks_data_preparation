from utils import *
from config import *

print("step 0: establish connection to database")

cursor = retrieve_database()

print("step 0 completed")

print("step 1: copy all page-xml files in dict")

page_xml_dict = {}
file_list = os.listdir(page_xml_source)

for file_name in file_list:
    source_path = os.path.join(page_xml_source, file_name)
    file = open(source_path, "r", encoding="'utf-8")
    page_xml_dict[re.sub('.xml', '', re.sub('ue', 'ü', file_name))] = file.read()

print("step 1 completed")

print("step 2: walk through all tei files, create page-xml for each one, and fill it with the help of the dictionary")
for filename in os.listdir(tei_source):
    if filename.endswith('.xml'):
        # Construct the full path to the XML file
        file_path = os.path.join(tei_source, filename)

        # open and read xml files, remove comments from file
        with open(file_path, 'r', encoding='utf-8') as xml_file:
            xml_content = re.sub(r'<!.*?->', '', xml_file.read())

        # parse the XML content with Beautiful Soup
        soup = BeautifulSoup(xml_content, 'xml')  # Use 'xml' parser for parsing XML

        # retrieve old id from database
        old_id = re.sub('l', '', soup.find("TEI")["xml:id"])

        # check if letter is latin, if so skip
        if old_id in latin_letters:
            continue

        # get writer id(s) from database
        cursor.execute('''SELECT ID_WRITER
        FROM LETTER_WRITER_REF
        WHERE ID_LETTER = ? AND PART = 15''', old_id)
        vals = cursor.fetchall()
        if len(vals) > 0:
            first = True
            for val in vals:
                if first:
                    writerID = str(val[0])
                    first = False
                else:
                    writerID = ','.join([writerID, str(val[0])])
            writer = True
        else:
            # if no writer id is known, print out letter id
            writer = False
            print(soup.find("TEI")["n"])

        # open the page-xml template with beautifulsoup
        with open("page-xml-template.xml", 'r', encoding='utf-8') as xml_file:
            xml_content = xml_file.read()
        page_xml = BeautifulSoup(xml_content, 'xml')

        # walk through all facsimiles (= all pages) in tei file (= in letter)
        for fac in soup.find_all("facsimile"):
            # for facsimile, find corresponding page-xml file and open it
            facs_id = fac["xml:id"]
            imageName = fac.graphic["url"].split('.')[0]
            if imageName not in page_xml_dict.keys():
                continue
            page_soup = BeautifulSoup(page_xml_dict[imageName], 'xml')

            # for all lines in facsimile, find diplomatic text for line in tei, modify and insert into corresponding page-xml file via line-id
            for line in fac.find_all("zone", rendition="Line"):
                if 'xml:id' not in line.attrs:
                    continue
                line_id = line['xml:id']
                page_no = line_id.split('_')[1]
                line_id_page = re.sub('facs_', '', line_id)
                line_id_page = re.sub(page_no + '_', '', line_id_page)

                line_tei = soup.find("ab", facs='#' + line_id)
                if not line_tei:
                    continue

                for add in line_tei.find_all("add"):
                    if add.find("ab", facs=True):
                        add.decompose()

                for gap in line_tei.find_all("gap"):
                    gap.attrs = {}

                insert = ''.join(map(str, line_tei.contents))

                # get rid of any cert attributes:
                insert = re.sub(" cert=\"[a-z]+\"", "", insert)
                # get rid of <l> tags
                insert = re.sub("<add><l>", "<add>", insert)
                insert = re.sub("</l></add>", "</add>", insert)
                # remove <add/>
                insert = re.sub("<add/>", "", insert)
                # remove <lb/>
                insert = re.sub("<lb/>", "", insert)
                # remove <app>
                insert = re.sub("<app>", "", insert)
                insert = re.sub("</app>", "", insert)

                line_page = page_soup.find("TextLine", id=line_id_page)
                if line_page and writer:
                    line_page["writerID"] = writerID
                    uni = line_page.find("Unicode")
                    if uni:
                        uni.clear()
                        uni.append(insert.strip())

            # remove all lines in page-xml that don't have the writerID attribute (so that page-xml will only have the lines belonging to the current letter)
            for line in page_soup.findAll("TextLine"):
                if not "writerID" in line.attrs:
                    line.decompose()
            # get rid of empty regions that are created by removing lines
            for region in page_soup.findAll("TextRegion"):
                if not region.find("TextLine"):
                    region.decompose()

            # get rid of all textequivs without lines
            unicode_lines = [x.find("TextEquiv") for x in page_soup.find_all("TextLine")]
            for reg in page_soup.find_all("TextRegion"):
                equivs = reg.find_all("TextEquiv")
                if len(equivs) > 0:
                    last_equiv = equivs[len(equivs) - 1]
                    if last_equiv not in unicode_lines:
                        last_equiv.decompose()

            # get rid of page header
            page_soup = page_soup.find("Page")

            # insert page-xml into the default file for the letter, thus creating a new page-xml file for the letter
            page_xml.find("PcGts").append(page_soup)

        # find regularised version, add into last textequiv
        normalised = soup.find("div", type="regularised")
        # remove <add>
        for add in normalised.find_all("add"):
            if add.find("ab", facs=True):
                add.decompose()
        # remove <app><q type=.../></app> (footnotes)
        for app in normalised.find_all("app"):
            if app is None:
                continue
            try:
                if "q type=" in str(app):
                    app.decompose()
            except TypeError:
                print("type error: " + filename)

        normalised = ''.join(str(x) for x in normalised.contents)
        # remove reason attribute in <gap>
        normalised = re.sub("gap reason=\"[a-z]+\"", "gap", normalised)
        # remove unecessary whitespaces
        normalised = "<div type=\"regularised\"><TextEquiv><Unicode>" + normalised.strip() + '</Unicode></TextEquiv></div>'
        # add regularised version to the page-xml
        page_xml.find("PcGts").append(reTEIfy(normalised, "div"))

        # create metadata for the page-xml
        page_xml.find("Metadata").append(reTEIfy("<Created>" + retrieve_time() + "</Created", "Created"))

        # expand boundary coordinates for page-xml
        expand_boundaries(page_xml)

        # write tei
        target_dir = "diplomatic-regularised/Band" + band
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(target_dir + "/" + filename, 'w', encoding='utf-8') as file:
            file.write(re.sub('<Unicode></Unicode>', '', re.sub('<Unicode/>', '', re.sub('\n+', '\n',
                                                                                         re.sub('[ ]+', ' ',
                                                                                                re.sub('&lt;', '<',
                                                                                                       re.sub('&gt;',
                                                                                                              '>', str(
                                                                                                               page_xml))))))))

print("step 2 completed")
