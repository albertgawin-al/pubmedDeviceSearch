import requests, gzip, os, shutil, datetime
import xml.etree.ElementTree as ET


def downloadFolder(index):
    url = f"https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed23n{index:04d}.xml.gz"
    filename = url.split("/")[-1]
    dataPath = "./data/" + filename[:-3]
    compressedPath = "./compressedData/" + filename
    
    try:
        print("    Downloading folder", filename)
        if os.path.exists(compressedPath) == False and os.path.exists(dataPath) == False:
            with open(compressedPath, "wb") as f:
                r = requests.get(url)
                if (r.status_code == 200):
                    f.write(r.content)
            f.close()
    except EOFError or FileNotFoundError:
        print("Downloading error occured.")
        print("Removing file and folder.")
        removeFile(index)
        removeFolder(index)

        print("Downloading again.")
        downloadFolder(index)


def extractFolder(index):
    filename = f"pubmed23n{index:04d}.xml.gz"
    dataPath = "./data/" + filename[:-3]
    compressedPath = "./compressedData/" + filename

    try:
        print("    Extracting folder", filename)
        if os.path.exists(dataPath) == False:
            with gzip.open(compressedPath, 'rb') as f_in:
                with open(dataPath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            f_in.close()
            f_out.close()
    except EOFError or FileNotFoundError:
        print("Extracting error occured.")
        removeFile(index)
        removeFolder(index)

        print("Extracting again.")
        downloadFolder(index)
        extractFolder(index)


def removeFolder(index):
    filename = f"pubmed23n{index:04d}.xml.gz"
    path = "./data/" + filename

    print("    Removing folder", filename)
    if os.path.exists(path) == True:
        os.remove(path)
        

def checkIfYear(index, element, element2):
    filename = f"pubmed23n{index:04d}.xml"
    path = "./data/" + filename

    startTag, startTag2 = f'<{element}', f'<{element2}'
    endTag2 = f'</{element2}>'
    startTagIdentified = False
    capturedRecords = list()
    capturedLine = ''
    with open(path, encoding="utf8") as f:
        for line in f:
            if startTag in line:
                startTagIdentified = True
            if startTagIdentified and startTag2 in line:
                capturedLine += line
                if int(capturedLine.split('>')[1].split('</')[0]) >= int('2020'):
                    print("    Article found.")
                    return True
            if endTag2 in line:
                capturedRecords.append(capturedLine)
                startTagIdentified = False
                capturedLine = ''
        
        print("    Article not found.")
        return False


def removeFile(index):
    filename = f"pubmed23n{index:04d}.xml"
    path = "./data/" + filename

    print("    Removing file", filename)
    if os.path.exists(path) == True:
        os.remove(path)


start = 1
end = 1167

for i in range(start, end):
    print(f"[{i:04d}/1166]")
    downloadFolder(i)
    extractFolder(i)

    if checkIfYear(i, 'DateRevised', 'Year') == False:
        removeFolder(i)

    removeFile(i)
