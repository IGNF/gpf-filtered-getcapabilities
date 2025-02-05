import csv
import os
import requests
import xml.etree.ElementTree as ET

namespaces = {}

SERVICES_GETCAP_URLS = {
  "wmts": "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities",
  "wms-r": "https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities",
  "wms-v": "https://data.geopf.fr/wms-v/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities",
  "wfs": "https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities",
}

def register_all_namespaces(filename):
    for _, node in ET.iterparse(filename, events=['start-ns']):
      if node[0] == 'wfs':
        continue
      namespaces[node[0]] = node[1]
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])

def getCapabilities(url):
  response = requests.get(url)
  if response.status_code != 200:
    return False

  with open("originalCapa.xml", "w", encoding="utf-8") as file:
    file.writelines(response.text)

  register_all_namespaces("originalCapa.xml")
  capabilities = ET.parse("originalCapa.xml")
  os.remove("originalCapa.xml")
  return capabilities

def createKeyServiceLayersFile(
  url=["https://data.geopf.fr/annexes/ressources/capabilities/services.csv","https://data.geopf.fr/annexes/ressources/capabilities/services-gpu.csv"],
  filePath="resources_by_key.csv"):
  with requests.Session() as s:
    download = s.get(url[0])
    decoded_content = download.content.decode("latin1")
    reader = csv.DictReader(decoded_content.splitlines(), delimiter=";")
  with requests.Session() as s:
    download_gpu = s.get(url[1])
    decoded_content_gpu = download_gpu.content.decode("latin1")
    reader_gpu = csv.DictReader(decoded_content_gpu.splitlines(), delimiter=";")
  with open(filePath, "w", newline='', encoding="utf-8") as csvFile:
    fieldnames = ["service", "key", "layer"]
    writer = csv.DictWriter(csvFile, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    for row in reader:
      if row["Service"] == "WMTS":
        service = "wmts"
      elif row["Service"] == "WMS Raster":
        service = "wms-r"
      elif row["Service"] == "WMS Vecteur":
        service = "wms-v"
      elif row["Service"] == "WFS":
        service = "wfs"
      else:
        continue

      if row["Thématique"] == "cle personnelle *":
        continue
      if row["Thématique"] == "":
        continue

      newRow = {
        "service": service,
        "key": row["Thématique"],
        "layer": row["Nom technique"].strip()
      }
      writer.writerow(newRow)
      
    for row in reader:
      elif row["Service"] == "WMS Vecteur":
        service = "wms-v"
      elif row["Service"] == "WFS":
        service = "wfs"
      else:
        continue

      newRow = {
        "service": service,
        "key": row["Thématique"],
        "layer": row["Nom technique"].strip()
      }
      writer.writerow(newRow)



def keysServicesLayers(filePath="resources_by_key.csv"):
  rows = []
  keys = []
  with open(filePath, encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",")
    for row in reader:
      rows.append(row)
      if row["key"] not in keys:
        keys.append(row["key"])

  keys_services_layers = {}
  for key in keys:
    keys_services_layers[key] = {}

    for row in rows:
      if row["key"] != key:
        continue
      if row["service"] not in keys_services_layers[key]:
        keys_services_layers[key][row["service"]] = []
      keys_services_layers[key][row["service"]].append(row["layer"])

  return keys_services_layers

def filterWMTSLayers(capabilities, layerList):
  root = capabilities.getroot()
  contents = root.find('Contents', namespaces)
  for layer in contents.findall('Layer', namespaces):
    identifier = layer.find('ows:Identifier', namespaces).text
    if identifier not in layerList:
      contents.remove(layer)

def filterWMSLayers(capabilities, layerList):
  root = capabilities.getroot()
  capability = root.find('Capability', namespaces)
  layerBig = capability.find('Layer', namespaces)
  for layer in layerBig.findall('Layer', namespaces):
    identifier = layer.find('Name', namespaces).text
    if identifier not in layerList:
      layerBig.remove(layer)

def filterWFSLayers(capabilities, layerList):
  root = capabilities.getroot()
  featureTypeList = root.find('FeatureTypeList', namespaces)
  for layer in featureTypeList.findall('FeatureType', namespaces):
    identifier = layer.find('Name', namespaces).text
    if identifier not in layerList:
      featureTypeList.remove(layer)

def createFilteredWMTS(keysServicesLayers, key):
  capabilities = getCapabilities(SERVICES_GETCAP_URLS["wmts"])
  filterWMTSLayers(capabilities, keysServicesLayers[key]["wmts"])
  return capabilities

def createFilteredWMSV(keysServicesLayers, key):
  capabilities = getCapabilities(SERVICES_GETCAP_URLS["wms-v"])
  filterWMSLayers(capabilities, keysServicesLayers[key]["wms-v"])
  return capabilities

def createFilteredWMSR(keysServicesLayers, key):
  capabilities = getCapabilities(SERVICES_GETCAP_URLS["wms-r"])
  filterWMSLayers(capabilities, keysServicesLayers[key]["wms-r"])
  return capabilities

def createFilteredWFS(keysServicesLayers, key):
  capabilities = getCapabilities(SERVICES_GETCAP_URLS["wfs"])
  filterWFSLayers(capabilities, keysServicesLayers[key]["wfs"])
  return capabilities

def writeFilteredGetCap(keysServicesLayers, key, service):
  if service == "wmts":
    capabilities = createFilteredWMTS(keysServicesLayers, key)
  elif service == "wms-v":
    capabilities = createFilteredWMSV(keysServicesLayers, key)
  elif service == "wms-r":
    capabilities = createFilteredWMSR(keysServicesLayers, key)
  elif service == "wfs":
    capabilities = createFilteredWFS(keysServicesLayers, key)
  else:
    print("Unknown service")
    return False

  ET.indent(capabilities, space="  ", level=0)
  capabilities.write("dist/{}/{}.xml".format(service, key), encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
  createKeyServiceLayersFile()
  keyServiceLayersDict = keysServicesLayers()
  for key in keyServiceLayersDict.keys():
    print(key)
    for service in keyServiceLayersDict[key].keys():
      writeFilteredGetCap(keyServiceLayersDict, key, service)
