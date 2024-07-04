class Node:
    def __init__(self, productId, count=1, sibling=None, parent=None):
        self.productId = productId
        self.count = count
        self.sibling = sibling
        self.parent = parent
        self.children = []

    def __repr__(self):
        return "{}:{} -> {}".format(
            self.productId,
            self.count,
            ",".join(list(map(lambda n: n.productId, self.children))),
        )

    def equals(self, productId):
        return self.productId == productId

    def increment(self):
        self.count += 1

    def insert(self, productId):
        node = next(filter(lambda n: n.equals(productId), self.children), None)
        if node is None:
            node = Node(productId, parent=self)
            self.children.append(node)
        else:
            node.increment()

        ",".join(list(map(lambda n: n.productId, node.children)))
        return node


class FPTree:
    def __init__(self, headerTable, minSup):
        self.headerTable = headerTable
        self.ascHeaderKeys = self.initAscHeaderKeys()
        self.rootNode = Node("root")
        self.nodePointerMap = self.initNodePointerMap()
        self.minSup = minSup
        self.freqItems = []

    def __repr__(self):
        outList = []
        self.strNodeDeps(self.rootNode, outList)
        return "\n".join(outList)

    def strNodeDeps(self, node, outList):
        outList.append(repr(node))
        for n in node.children:
            self.strNodeDeps(n, outList)

    def insert(self, transaction):
        curNode = self.rootNode
        for productId in transaction:
            curNode = curNode.insert(productId)
            self.nodePointerMap[productId].add(curNode)

    def insertTransactions(self, transactions):
        sortedTransactions = self.sortTransactions(transactions)
        for t in sortedTransactions:
            self.insert(t)

    def sortTransactions(self, transactions):
        sortedTransactions = []
        for t in transactions:
            sortedTransactions.append(self.sortTransaction(t))

        return sortedTransactions

    def sortTransaction(self, transaction):
        filtered = list(filter(lambda x: x in self.headerTable, transaction))
        # Sort alphabetically (or numerically) first to ensure items
        # with same support appear in same order across transactions
        filtered.sort(reverse=True)
        filtered.sort(reverse=True, key=lambda x: self.headerTable[x])

        return filtered

    def get_freq_items(self):
        freqItems = []
        freqItemCache = {}
        for key in self.ascHeaderKeys:
            keyItems = self._mine_conditional_tree(key, freqItemCache)
            freqItems.extend(keyItems)

        return freqItems

    def _mine_conditional_tree(self, key, freqItemCache):
        prefixPaths = self._build_prefix_path_for_key(key)
        freqItems = []

        # Iterate through pointers for this key, which make up all the leaves of the conditional tree.
        for suffixNode in self.nodePointerMap[key]:
            itemSetQueue = [[suffixNode]]

            # A conditional tree is made up of prefix paths which we mine here, starting with our suffix node,
            # adding 1 ancestor node and testing its support, if its frequent we add it to the queue and do this
            # again until all combinations for a prefix path have been exhausted.
            while len(itemSetQueue) > 0:
                candidateItemSetPrefix = itemSetQueue.pop()
                # Create a flat list of just the product ids for the freq items list
                candidateFreqItemSetPrefix = list(
                    map(lambda node: node.productId, candidateItemSetPrefix)
                )
                curPatternNode = candidateItemSetPrefix[-1].parent

                # For the current candidate prefix, create a candidate item set by appending each
                # parent of the highest node in the itemset and checking if its frequent.
                while curPatternNode.productId != "root":
                    # Append node to form the full candidate item set to support test
                    candidateItemSet = candidateItemSetPrefix + [curPatternNode]
                    candidateFreqItemSet = candidateFreqItemSetPrefix + [
                        curPatternNode.productId
                    ]
                    cacheKey = "".join(candidateFreqItemSet)

                    if cacheKey not in freqItemCache:
                        # Sum count across all prefix paths to get support
                        itemSetSupport = self._calc_support_for_item_set(
                            prefixPaths, candidateFreqItemSet, suffixNode
                        )
                        if itemSetSupport >= self.minSup:
                            freqItems.append(candidateFreqItemSet)
                            itemSetQueue.append(candidateItemSet)
                            freqItemCache[cacheKey] = True
                        else:
                            freqItemCache[cacheKey] = False

                    curPatternNode = curPatternNode.parent

        return freqItems

    def _calc_support_for_item_set(self, prefixPaths, candidateFreqItemSet, suffixNode):
        itemSetSupport = 0

        # Need to check if items in set are contained in other prefix paths and then count up the
        # suffix nodes to get the total support across the conditional sub tree.
        for prefixPath in prefixPaths:
            productIdsNotInPrefixPath = list(
                filter(
                    lambda productId: productId not in prefixPath, candidateFreqItemSet
                )
            )
            if len(productIdsNotInPrefixPath) == 0:
                itemSetSupport += prefixPath[suffixNode.productId]

        return itemSetSupport

    def _build_prefix_path_for_key(self, key):
        prefixPaths = []
        for p in self.nodePointerMap[key]:
            path = {}
            curNode = p
            while curNode.productId != "root":
                path[curNode.productId] = curNode.count
                curNode = curNode.parent

            prefixPaths.append(path)

        return prefixPaths

    def initNodePointerMap(self):
        return dict(map(lambda kv: (kv[0], set()), self.headerTable.items()))

    def initAscHeaderKeys(self):
        alphaSortedHeader = sorted(self.headerTable.items(), key=lambda kv: kv[0])
        supSortedHeader = sorted(alphaSortedHeader, key=lambda kv: kv[1])
        return list(map(lambda t: t[0], supSortedHeader))