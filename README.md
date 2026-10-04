*This project has been created as part of the 42 curriculum by lupalomi*

# Description
This project consist in generate a graph from a map given by the user where a number of drones must reach a goal destination.

To generate the graph, **hubs** and **connections** are created based on the map provided. When a **simulation** begins, all the drones are generated with a route designed using the [Yen's algortihm](https://www.youtube.com/watch?v=bQCewgMFaYQ).  Each turn is represented by a line, and each line shows the movements made by each drone, indicating the drone’s ID and the hub it is heading for. If a drone don't move, doesn't print any movement.

## Hub properties
Each hub has the next properties
- **Color**: Any single-word string is considered a color. However not every single-word string is a color. To implement this, the `rich` library identifies the color and implements it. If the color doesn't exist in the library, a random color is assigned. By default, hubs have no color.

- **Zone**: The only valid zones are these:
    - **Normal**: Default zone with 1 turn movement cost.
    - **Blocked**: Inaccessible zone. Drones must not enter or pass through this zone. Any path using it is invalid.
    - **Restricted**: Movement to this zone costs 2 turns.
    - **Priority**: A preferred zone. Movement to this zone costs 1 turn but should be prioritized in pathfinding.

- **Max drones**: Maximum drones that can occupy this zone simultaneously. By default, is 1.

## Connection Properties
The only property that is available for connections is **Max link capacity** that specifies maximum amount of drones that can traverse this connection simultaneously. By default, the value is 1.

## Algorithm choices
### Dijkstra Algorithm
**Dijkstra's algorithm** finds the shortest path between two hubs by exploring the graph according to the lowest accumulated cost found so far. Whenever a cheaper way to reach a hub is discovered, its cost and previous hub are updated. The process continues until the destination hub is reached and the shortest route can be reconstructed.

### Yen's Algorithm
**Yen's algorithm** finds up to `k` shortest loopless paths between two hubs. It starts with the shortest route found by Dijkstra and then generates alternatives by temporarily blocking hubs or connections at different deviation points of previously found routes. Each alternative is calculated again with Dijkstra, and the best candidates are kept until `k` different routes have been obtained or no more alternatives exist.

### Why not use only Dijkstra instead of Yen?
**Dijkstra's algorithm** only returns one shortest path between two hubs. If every drone used that same route, the simulation could create unnecessary bottlenecks and would not take advantage of alternative paths available in the graph. **Yen's algorithm** solves this limitation by finding several of the shortest alternative routes. This provides more routing options and allows the simulation to distribute drones across different paths instead of depending on a single one.

## Visual representation features

## Example input and expected output

# Instructions

# Resources

#### For Dijkstra Algorithm
- [Dijkstra Algorithm: Video Explanation](https://www.youtube.com/watch?v=bQCewgMFaYQ)

- [Dijkstra Algorithm: Information](https://towardsdev.com/dijkstras-algorithm-explained-the-heart-of-pathfinding-and-optimization-24d927b8adb5)

#### For Yen's Algorithm
- [Yen's Algorithm: Video Explanation](https://www.youtube.com/watch?v=bQCewgMFaYQ)

- [Yen's Algorithm: Information 1](https://www.ultipa.com/docs/graph-algorithms/yens)

- [Yen's Algorithm: Information 2](https://dev.to/whoakarsh/finding-the-k-shortest-paths-using-yens-algorithm-in-python-1gka)

- [Yen's Algorithm: Image Example](https://www.linchenguang.com/2018/01/30/Yen-s-algorithm/)

#### Memory leaks

- [Finding a memory leak in my python code](https://tamir.dev/posts/finding-a-memory-leak-in-my-python-code/)