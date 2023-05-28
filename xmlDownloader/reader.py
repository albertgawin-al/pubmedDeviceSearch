import os, gzip, shutil, datetime
from xml.etree import ElementTree


def extractFolder(filename):
    compressedPath = "./compressedData/" + filename
    xmlPath = "./xmlData/" + filename[:-3]

    try:
        print("    Extracting folder", filename)
        if os.path.exists(xmlPath) == False:
            with gzip.open(compressedPath, 'rb') as f_in:
                with open(xmlPath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            f_in.close()
            f_out.close()
    except EOFError or FileNotFoundError:
        print(f"Extracting error occured for {filename}")


def fetchArticleText(article):
    fullAbstract = ''
    abstracts = article.findall("Article/Abstract/AbstractText")

    if len(abstracts) == 0: 
        return 'N/A'
    
    for abstract in abstracts:
        if type(abstract.text) == str:
            fullAbstract += ' ' + abstract.text

    return fullAbstract

def fetchMeshHeadings(article):
    meshHeadings = []
    headings = article.findall("MeshHeadingList/MeshHeading/DescriptorName")

    if len(headings) == 0: 
        return 'N/A'

    for heading in headings:
        meshHeadings.append(heading.text)

    return ','.join(meshHeadings)


def saveDataFromXML(filename):
    xmlPath = "./xmlData/" + filename[:-3]
    txtPath = f"data/data_{filename[:-7]}.txt"

    print("    Parsing XML file", filename[:-3])
    root = ElementTree.parse(xmlPath)

    print("    Saving data to ", txtPath)
    with open(txtPath, mode='a', encoding='utf8') as f:
        for article in root.iterfind('PubmedArticle/MedlineCitation'):
            rowData = []
            if int(article.find('DateRevised/Year').text) >= (datetime.date.today().year - 3):
                rowData.append(article.findtext('PMID', default='N/A'))
                rowData.append(article.findtext('DateRevised/Year', default='N/A'))
                rowData.append(article.findtext('Article/ArticleTitle', default='N/A'))
                rowData.append(fetchArticleText(article))
                rowData.append(fetchMeshHeadings(article))

                rowData = [data.replace(';','') for data in rowData]
                f.write(';'.join(rowData) + '\n')
        f.close()


def removeXMLFile(filename):
    xmlPath = "./xmlData/" + filename[:-3]

    print("    Removing file", filename[:-3])
    if os.path.exists(xmlPath) == True:
        os.remove(xmlPath)


compressedPath = "./compressedData/"
paths = os.listdir(compressedPath)

for index, path in enumerate(paths):
    with open(f'data/data_{path[:-7]}.txt', mode='w', encoding='utf8') as f:
        f.write('pmid;year;title;abstract;headings' + '\n')
    f.close()

    print(f'[{index+1}/{len(paths)}]')
    extractFolder(path)
    saveDataFromXML(path)
    removeXMLFile(path)
