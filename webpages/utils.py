
import metadata_parser

def getOGMetaData(url):
    
    webpage = metadata_parser.MetadataParser(url=url, search_head_only=True)

    print(webpage.metadata)
    
    return