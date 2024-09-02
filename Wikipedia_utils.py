import wikipedia
import Pinecone_utils
import OpenAI_utils

#TODO: stop creating so many wikipedia.page objects, can reuse here


def get_links(wikipage: str) -> list:
    
    return wikipedia.page(title = wikipage, auto_suggest = False).links


def get_point(start : bool) -> str:
    
    #start = True when getting start point wiki page, False when getting end point wiki page
    
    point :str = "starting" if start else "ending"
    
    pointtitle : str = input(f"Enter the title of the {point} wikipedia page: ")

    search : list[str] = wikipedia.search(pointtitle)

    #check if page exists
    if(len(search) == 0):
                    
        print("This page doesn't exist. Please try another.")
        return get_point(start)

    #if starting page, check if dead-end
    if (start):
        
        if (len(get_links(search[0])) == 0):

            print("The page you provided is a dead-end, i.e. it has no links. Please try another.")
            return get_point(start)
        
    return search[0]


def check_next(possibilities : list[str], route : list[str]) -> tuple[str, list[str]]:
    
    nextMid : str = ""
    nextMid_links : list[str] = []
    
    for node in possibilities:
        
        #check if node will lead to a loop
        
        if(node in route):
            
            continue
        
        #check if node is a dead end
        
        try:
                
            links : list[str] = get_links(node)
            
            if(len(links) == 0):
                
                continue
        
        except:
            
            continue
        
        #if all good, set nextMid and nextMid_links then exit loop
        
        nextMid, nextMid_links = node, links
        break
    
    return (nextMid, nextMid_links)
        

def check_ascii(text):
    
    for c in text:
        
        if (ord(c) > 127):
            
            return False    
        
    return True    
    
    
def get_next(mNode : str, mLinks : list[str], eVector : list[float], route : list[str], index : Pinecone_utils.Index) -> tuple[str, list[str]]:
    
    #make all titles ascii only
    for i in range(len(mLinks)-1, -1, -1):
        
        if(not check_ascii(mLinks[i])):
            
            mLinks.pop(i)
    
    print(f"Inserting links for {mNode}")
    
    Pinecone_utils.insert_vectors_from_data(parent_page = mNode, filetext = mLinks, index = index)
    
    print(f"Querying {mNode}'s links") #NOTE: REMOVE AFTER TESTING
    
    possible_next_nodes : list[str] = Pinecone_utils.query_pinecone_index(input_vector = eVector, parent_page = mNode, index = index)
    
    return check_next(possibilities = possible_next_nodes, route = route) #Limitation: when check_next finds all links to be dead-ends.


def trace_route(startpoint : str, endpoint :str, index : Pinecone_utils.Index) -> dict[str, str]:
    
    mid_node : str = startpoint
    mid_links : list[str] = get_links(startpoint)
    end_node : str = endpoint
    end_vector : list[float] = OpenAI_utils.get_embedding(end_node)
    
    route : dict[str, str] = { mid_node : wikipedia.page(title = mid_node).url }
    
    while(mid_node != end_node):
        
        mid_node, mid_links = get_next(mNode = mid_node, mLinks = mid_links, eVector = end_vector, route = route, index = index)
        
        route[mid_node] = wikipedia.page(title = mid_node, auto_suggest = False).url
        
    return route
    