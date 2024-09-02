Hi! I'm Varun Venkatadri, the author and owner of all the code and concepts in this repository.

This is a Wikipedia Speedrunning Program I call VectorRunner.

Wikipedia Speedrunning is a game that revolves around getting from one wikipedia article to another via only
clicking on the links in the article that lead to another wikipedia page. The one who can get to the final page the in the least number of links in between wins!

For example, with a starting page of Apple and the end goal of Genghis Khan, we can click on the link for the wikipedia page for Central Asia in the first paragraph of the Apple article. Then we click on Mongolia in the 
Central Asia article and then Genghis Khan. We've reached the end goal in 3 clicks, and our route is Apple->
Central Asia -> Mongolia -> Genghis Khan.

Now, if we were competing with someone and they somehow got from Apple to Genghis Khan in 2 clicks, they would
have won.

That's how Wikipedia Speedrunning works. Any links that lead to non-wikipedia articles are not allowed, nor
are any links in the 'See Also' and 'References' sections.

Now, I'm going to talk about how I've implemented VectorRunner to do wikipedia speedrunning.

This program uses vector embeddings. I won't explain how they work here, if you wish to know more
I suggest you watch some videos or read up on it - its quite fascinating.

The way VectorRunner works is that it gets all the links on a wiki page, then gets embeddings for all those pages' titles, then queries them to find the wikipedia page with the title that most closely matches that of the goal page. Once it selects the most similar page, it repeats the process with that pages' links and so
on until it reaches the end goal page. 

I've thought about this whole process graphically - as in the starting page and ending pages are nodes in a graph, and the program has to map out a route between them. When I initially looked at it this way, my first
thought was to use Dijkstra's algorithm or some modified version of it to traverse through the graph to find the shortest route. Doing a breadth-first or depth-first search seemed unreasonable as the graph in this process
essentially doesn't exist until the search algorithm runs.

The reason why I say this is because I am not using WikiData nor do I intend to map out the entirety of wikipedia myself, so the graph in this case is what I call an 'in-building' graph. In such a case, the graph
essentially doesn't exist until the program maps it out.

I think of it similar to a baby without object permanace. For the baby, nothing exists until it sees
it, and then once that thing leaves the baby's field of vision it stops existing. Until the search algorithm maps out the route, the graph itself deosn't exist. Once the route has been mapped, the program stops executing
and the graph ceases to exist.

So then, how exactly does one solve the problem of finding the shortest path between 2 nodes when the graph itself doesn't exist?

I solved this by virtue of the context of this particular problem. In the case of Wikipedia Speedrunning, the
nodes are the various wiki pages we traverse as part of the route from the starting node to the ending node.
But, what exactly are the edges here? 

I realized that when a person is participating in a wikipedia speedrun and sees a link to a wiki article, their
measurement for checking whether or not to click on said link and go to that wikipedia page is how 'close' that
page is to the end page. When I say close here, I mean in terms of semantics and conceptually. I.e. are the concepts that relate to, or the meaning of, the topic of this page similar to the end page I want to get to?

Thus, in essence, the edges between each node is their semantic and conceptual similarity. The best way I know
of to capture such edge values in way a program can understand it is to represent the nodes as vectors, and thus
the distance between the vectors of those 2 nodes is the edge distance between those 2 nodes.

However, in the case of Wikipedia speedrunning, we have an interesting situation, where we don't acutally care
about the edge distances between adjacent nodes. We only care about the edge distance between the nodes in front
of us and the end node.

So what I've come up with is basically a heavily modified, semantic version of Dijkstra's algorithm, where
instead of measuring the shortest edge to take by checking the edge length from the current node to it's neighbors, I'm checking the edge length between the neighbors of the current node to the end node.
Then I traverse to the node which has the shortest distance to the end node, thus filling out the graph and finding the shortest route simultaneously.

This is a unique pathfinding algorithm that can be used when the edge lengths between neighboring nodes are unknown, but every single node's distance to the end node is known.

For vector database storage and querying this program uses PineCone. For embeddings this program uses OpenAI's
text-embedding-3-small with 1536 dimensional vectors.

I've also made it so that as the program runs, it will store and keep vectors in the database between executions and thus avoid repeatedly getting the vectors for the same data.


Additional Notes:

NOTE 1: Batching the embeddings might be useful, however to my knowledge, the way OpenAI has currently implemented the feature requires constantly writing to and reading from a file which may reduce any performance gain from batching. 
The file I/O cannot be done asynchronously or on a different thread, as only once the links are written to a file can they be then sent to get embeddings as a batch. Until the embeddings have been retreived, the program cannot progress.

NOTE 2: Currently, the program doesn't function as intended. The general concept and algorithm work fine, but the program unitentionally uses links in the 'External Links' template in wiki pages. This is strictly not allowed in Wikipedia Speedrunning, but I haven't been able to find a way to restrict the program such that it doesn't use that section.
