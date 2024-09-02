'''VectorRunner'''

from Wikipedia_utils import get_point, trace_route
from Pinecone_utils import create_pinecone_index
from pinecone import Index

#Create Index

index_name = "wikipedia-speedrunning-vectors"

index : Index = create_pinecone_index(index_name)

#Get start and end nodes

start_node : str = get_point(True)

print(f"Starting Page: {start_node}")

end_node : str = get_point(False)

print(f"Ending Page: {end_node}\n")

#trace route

route = trace_route(startpoint = start_node, endpoint = end_node, index = index)

#print route

print(f"\nThe route taken from {start_node} to {end_node}:")

for key,value in route.items():
    
    print(f"Title: {key} | URL : {value}")