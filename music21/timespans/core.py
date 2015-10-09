# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Name:         timespans/core.py
# Purpose:      Core AVLTree object.  To be optimized the hell out of.
#
# Authors:      Josiah Wolf Oberholtzer
#               Michael Scott Cuthbert
#
# Copyright:    Copyright © 2013-15 Michael Scott Cuthbert and the music21
#               Project
# License:      LGPL or BSD, see license.txt
#------------------------------------------------------------------------------
'''
These are the lowest level tools for working with self-balancing AVL trees.

There's an overhead to creating an AVL tree, but for a large score it is
absolutely balanced by having O(log n) search times.
'''
from music21.exceptions21 import TimespanException

from music21 import common

#------------------------------------------------------------------------------
class AVLNode(common.SlottedObject):
    r'''
    An AVL Tree Node, not specialized in any way, just contains offsets.

    >>> offset = 1.0
    >>> node = timespans.core.AVLNode(offset)
    >>> node
    <Node: Start:1.0 Height:0 L:None R:None>
    >>> n2 = timespans.core.AVLNode(2.0)
    >>> node.rightChild = n2
    >>> node.update()
    >>> node
    <Node: Start:1.0 Height:1 L:None R:0>
    
    Note that nodes cannot rebalance themselves, that's what a Tree is for.
    

    Please consult the Wikipedia entry on AVL trees
    (https://en.wikipedia.org/wiki/AVL_tree) for a very detailed
    description of how this datastructure works.    
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '__weakref__',
        'balance',
        'height',
        'offset',
        'payload',

        'leftChild',
        'rightChild',
        )

    _DOC_ATTR = {
    'balance': '''
        Returns the current state of the difference in heights of the 
        two subtrees rooted on this node.

        This attribute is used to help balance the AVL tree.

        >>> score = timespans.makeExampleScore()
        >>> tree = timespans.streamToTimespanTree(score, flatten=True, 
        ...                    classList=(note.Note, chord.Chord))
        >>> print(tree.debug())
        <Node: Start:3.0 Indices:(0:5:6:12) Length:{1}>
            L: <Node: Start:1.0 Indices:(0:2:3:5) Length:{1}>
                L: <Node: Start:0.0 Indices:(0:0:2:2) Length:{2}>
                R: <Node: Start:2.0 Indices:(3:3:5:5) Length:{2}>
            R: <Node: Start:5.0 Indices:(6:8:9:12) Length:{1}>
                L: <Node: Start:4.0 Indices:(6:6:8:8) Length:{2}>
                R: <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>
                    R: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>


        This tree has one more depth on the right than on the left

        >>> tree.rootNode.balance
        1


        The leftChild of the rootNote is perfectly balanced, while the rightChild is off by
        one (acceptable).

        >>> tree.rootNode.leftChild.balance
        0
        >>> tree.rootNode.rightChild.balance
        1


        The rightChild's children are also (acceptably) unbalanced:

        >>> tree.rootNode.rightChild.leftChild.balance
        0
        >>> tree.rootNode.rightChild.rightChild.balance
        1
        
        You should never see a balance other than 1, -1, or 0.  If you do then
        something has gone wrong.
        ''',
        
        
    'height': r'''
        The height of the subtree rooted on this node.

        This property is used to help balance the AVL tree.

        >>> score = timespans.makeExampleScore()
        >>> tree = timespans.streamToTimespanTree(score, flatten=True, 
        ...              classList=(note.Note, chord.Chord))
        >>> print(tree.debug())
        <Node: Start:3.0 Indices:(0:5:6:12) Length:{1}>
            L: <Node: Start:1.0 Indices:(0:2:3:5) Length:{1}>
                L: <Node: Start:0.0 Indices:(0:0:2:2) Length:{2}>
                R: <Node: Start:2.0 Indices:(3:3:5:5) Length:{2}>
            R: <Node: Start:5.0 Indices:(6:8:9:12) Length:{1}>
                L: <Node: Start:4.0 Indices:(6:6:8:8) Length:{2}>
                R: <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>
                    R: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>

        >>> tree.rootNode.height
        3

        >>> tree.rootNode.rightChild.height
        2

        >>> tree.rootNode.rightChild.rightChild.height
        1

        >>> tree.rootNode.rightChild.rightChild.rightChild.height
        0
        
        Once you hit a height of zero, then the next child on either size should be None
        
        >>> print(tree.rootNode.rightChild.rightChild.rightChild.rightChild)
        None
        ''',
        
    'offset': r'''
        The offset of this node.

        >>> score = timespans.makeExampleScore()
        >>> tree = timespans.streamToTimespanTree(score, flatten=True, classList=(note.Note, chord.Chord))
        >>> print(tree.rootNode.debug())
        <Node: Start:3.0 Indices:(0:5:6:12) Length:{1}>
            L: <Node: Start:1.0 Indices:(0:2:3:5) Length:{1}>
                L: <Node: Start:0.0 Indices:(0:0:2:2) Length:{2}>
                R: <Node: Start:2.0 Indices:(3:3:5:5) Length:{2}>
            R: <Node: Start:5.0 Indices:(6:8:9:12) Length:{1}>
                L: <Node: Start:4.0 Indices:(6:6:8:8) Length:{2}>
                R: <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>
                    R: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>

        >>> tree.rootNode.offset
        3.0

        >>> tree.rootNode.leftChild.offset
        1.0

        >>> tree.rootNode.rightChild.offset
        5.0
        ''',
    'leftChild': r'''
        The left child of this node.

        After setting the left child you need to do a node update. with node.update()

        >>> score = timespans.makeExampleScore()
        >>> tree = timespans.streamToTimespanTree(score, flatten=True, classList=(note.Note, chord.Chord))
        >>> print(tree.rootNode.debug())
        <Node: Start:3.0 Indices:(0:5:6:12) Length:{1}>
            L: <Node: Start:1.0 Indices:(0:2:3:5) Length:{1}>
                L: <Node: Start:0.0 Indices:(0:0:2:2) Length:{2}>
                R: <Node: Start:2.0 Indices:(3:3:5:5) Length:{2}>
            R: <Node: Start:5.0 Indices:(6:8:9:12) Length:{1}>
                L: <Node: Start:4.0 Indices:(6:6:8:8) Length:{2}>
                R: <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>
                    R: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>

        >>> print(tree.rootNode.leftChild.debug())
        <Node: Start:1.0 Indices:(0:2:3:5) Length:{1}>
            L: <Node: Start:0.0 Indices:(0:0:2:2) Length:{2}>
            R: <Node: Start:2.0 Indices:(3:3:5:5) Length:{2}>
        ''',
    'rightChild':   r'''
        The right child of this node.

        After setting the right child you need to do a node update. with node.update()

        >>> score = timespans.makeExampleScore()
        >>> tree = timespans.streamToTimespanTree(score, flatten=True, classList=(note.Note, chord.Chord))
        >>> print(tree.rootNode.debug())
        <Node: Start:3.0 Indices:(0:5:6:12) Length:{1}>
            L: <Node: Start:1.0 Indices:(0:2:3:5) Length:{1}>
                L: <Node: Start:0.0 Indices:(0:0:2:2) Length:{2}>
                R: <Node: Start:2.0 Indices:(3:3:5:5) Length:{2}>
            R: <Node: Start:5.0 Indices:(6:8:9:12) Length:{1}>
                L: <Node: Start:4.0 Indices:(6:6:8:8) Length:{2}>
                R: <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>
                    R: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>

        >>> print(tree.rootNode.rightChild.debug())
        <Node: Start:5.0 Indices:(6:8:9:12) Length:{1}>
            L: <Node: Start:4.0 Indices:(6:6:8:8) Length:{2}>
            R: <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>
                R: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>

        >>> print(tree.rootNode.rightChild.rightChild.debug())
        <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>
            R: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>

        >>> print(tree.rootNode.rightChild.rightChild.rightChild.debug())
        <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>
        '''

    }
    
    ### INITIALIZER ###

    def __init__(self, offset, payload=None):
        self.balance = 0
        self.height = 0        
        self.offset = offset
        self.payload = payload

        self.leftChild = None
        self.rightChild = None


    ### SPECIAL METHODS ###

    def __repr__(self):
        lcHeight = None
        if self.leftChild:
            lcHeight = self.leftChild.height
        rcHeight = None
        if self.rightChild:
            rcHeight = self.rightChild.height
            
        return '<Node: Start:{} Height:{} L:{} R:{}>'.format(
            self.offset,
            self.height,
            lcHeight,
            rcHeight
            )

    ### PRIVATE METHODS ###

    def debug(self):
        '''
        Get a debug of the Node:
        
        >>> score = timespans.makeExampleScore()
        >>> tree = timespans.streamToTimespanTree(score, flatten=True, classList=(note.Note, chord.Chord))
        >>> rn = tree.rootNode        
        >>> print(rn.debug())
        <Node: Start:3.0 Indices:(0:5:6:12) Length:{1}>
            L: <Node: Start:1.0 Indices:(0:2:3:5) Length:{1}>
                L: <Node: Start:0.0 Indices:(0:0:2:2) Length:{2}>
                R: <Node: Start:2.0 Indices:(3:3:5:5) Length:{2}>
            R: <Node: Start:5.0 Indices:(6:8:9:12) Length:{1}>
                L: <Node: Start:4.0 Indices:(6:6:8:8) Length:{2}>
                R: <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>
                    R: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>
        '''
        return '\n'.join(self._getDebugPieces())

    def _getDebugPieces(self):
        r'''
        Return a list of the debugging information of the tree (used for debug):
        
        >>> score = timespans.makeExampleScore()
        >>> tree = timespans.streamToTimespanTree(score, flatten=True, classList=(note.Note, chord.Chord))
        >>> rn = tree.rootNode
        >>> rn._getDebugPieces()
        ['<Node: Start:3.0 Indices:(0:5:6:12) Length:{1}>', 
        '\tL: <Node: Start:1.0 Indices:(0:2:3:5) Length:{1}>',
        '\t\tL: <Node: Start:0.0 Indices:(0:0:2:2) Length:{2}>', 
        '\t\tR: <Node: Start:2.0 Indices:(3:3:5:5) Length:{2}>', 
        '\tR: <Node: Start:5.0 Indices:(6:8:9:12) Length:{1}>', 
        '\t\tL: <Node: Start:4.0 Indices:(6:6:8:8) Length:{2}>', 
        '\t\tR: <Node: Start:6.0 Indices:(9:9:11:12) Length:{2}>', 
        '\t\t\tR: <Node: Start:7.0 Indices:(11:11:12:12) Length:{1}>']        
        '''        
        result = []
        result.append(repr(self))
        if self.leftChild:
            subresult = self.leftChild._getDebugPieces()
            result.append('\tL: {}'.format(subresult[0]))
            result.extend('\t' + x for x in subresult[1:])
        if self.rightChild:
            subresult = self.rightChild._getDebugPieces()
            result.append('\tR: {}'.format(subresult[0]))
            result.extend('\t' + x for x in subresult[1:])
        return result

    def update(self):
        '''
        Updates the height and balance attributes of the nodes.
        
        Must be called whenever .leftChild or .rightChild are changed.
        
        Does not balance itself! just used for the next balancing operation.
        
        Returns None
        '''        
        leftHeight = -1
        rightHeight = -1
        if self.leftChild is not None:
            leftHeight = self.leftChild.height
        if self.rightChild is not None:
            rightHeight = self.rightChild.height
        self.height = max(leftHeight, rightHeight) + 1
        self.balance = rightHeight - leftHeight


#----------------------------------------------------------------------------

class AVLTree(object):
    r'''
    Data structure for working with timespans.node.AVLNode objects.
    
    To be subclassed in order to do anything useful with music21 objects.
    '''
    __slots__ = (
        '__weakref__',
        'rootNode',
        )
    nodeClass = AVLNode
    
    def __init__(self):
        self.rootNode = None

    def __iter__(self):
        r'''
        Iterates through all the nodes in the offset tree in left to right order.

        >>> tsList = [(0,2), (0,9), (1,1), (2,3), (3,4), (4,9), (5,6), (5,8), (6,8), (7,7)]
        >>> tss = [timespans.Timespan(x, y) for x, y in tsList]
        >>> tree = timespans.trees.TimespanTree()
        >>> tree.insert(tss)

        >>> for x in tree:
        ...     x
        ...
        <Timespan 0 2>
        <Timespan 0 9>
        <Timespan 1 1>
        <Timespan 2 3>
        <Timespan 3 4>
        <Timespan 4 9>
        <Timespan 5 6>
        <Timespan 5 8>
        <Timespan 6 8>
        <Timespan 7 7>
        '''
        def recurse(node):
            if node is not None:
                if node.leftChild is not None:
                    for n in recurse(node.leftChild):
                        yield n
                yield node
                if node.rightChild is not None:
                    for n in recurse(node.rightChild):
                        yield n
                        
        return recurse(self.rootNode)


    def insertAtOffset(self, offset):
        '''
        creates a new node at offset and sets the rootNode
        appropriately
        
        >>> avl = timespans.core.AVLTree()
        >>> avl.insertAtOffset(20)
        >>> avl.rootNode
        <Node: Start:20 Height:0 L:None R:None>        
        
        >>> avl.insertAtOffset(10)
        >>> avl.rootNode
        <Node: Start:20 Height:1 L:0 R:None>

        >>> avl.insertAtOffset(5)
        >>> avl.rootNode
        <Node: Start:10 Height:1 L:0 R:0>
        
        >>> avl.insertAtOffset(30)
        >>> avl.rootNode
        <Node: Start:10 Height:2 L:0 R:1>
        >>> avl.rootNode.leftChild
        <Node: Start:5 Height:0 L:None R:None>
        >>> avl.rootNode.rightChild
        <Node: Start:20 Height:1 L:None R:0>
        
        >>> avl.rootNode.rightChild.rightChild
        <Node: Start:30 Height:0 L:None R:None>
        '''
        def recurse(node, offset):
            '''
            this recursively finds the right place for the new node
            and either creates a new node (if it is in the right place)
            or rebalances the nodes above it and tells those nodes how
            to set their new roots.
            '''
            if node is None:
                # if we get to the point where a node does not have a
                # left or right child, make a new node at this offset...
                return self.nodeClass(offset)
            
            if offset < node.offset:
                node.leftChild = recurse(node.leftChild, offset)
                node.update()
            elif node.offset < offset:
                node.rightChild = recurse(node.rightChild, offset)
                node.update()
            return self._rebalance(node)            
        
        self.rootNode = recurse(self.rootNode, offset)


    def debug(self):
        r'''
        Gets string representation of the timespan collection.

        Useful only for debugging its internal node structure.

        >>> tsList = [(0,2), (0,9), (1,1), (2,3), (3,4), (4,9), (5,6), (5,8), (6,8), (7,7)]
        >>> tss = [timespans.Timespan(x, y) for x, y in tsList]
        >>> tree = timespans.trees.TimespanTree()
        >>> tree.insert(tss)

        >>> print(tree.debug())
        <Node: Start:3 Indices:(0:4:5:10) Length:{1}>
            L: <Node: Start:1 Indices:(0:2:3:4) Length:{1}>
                L: <Node: Start:0 Indices:(0:0:2:2) Length:{2}>
                R: <Node: Start:2 Indices:(3:3:4:4) Length:{1}>
            R: <Node: Start:5 Indices:(5:6:8:10) Length:{2}>
                L: <Node: Start:4 Indices:(5:5:6:6) Length:{1}>
                R: <Node: Start:6 Indices:(8:8:9:10) Length:{1}>
                    R: <Node: Start:7 Indices:(9:9:10:10) Length:{1}>
        '''
        if self.rootNode is not None:
            return self.rootNode.debug()
        return ''

    def _rebalance(self, node):
        r'''
        Rebalances the subtree rooted on`node`.

        Returns the original node.
        '''
        if node is not None:
            if node.balance > 1:
                if 0 <= node.rightChild.balance:
                    node = self._rotateRightRight(node)
                else:
                    node = self._rotateRightLeft(node)
            elif node.balance < -1:
                if node.leftChild.balance <= 0:
                    node = self._rotateLeftLeft(node)
                else:
                    node = self._rotateLeftRight(node)
            if node.balance < -1 or node.balance > 1:
                raise TimespanException('Somehow Nodes are still not balanced. node.balance %r must be between -1 and 1')
        return node
    
    def _rotateLeftLeft(self, node):
        r'''
        Rotates a node left twice.

        Used internally by TimespanTree during tree rebalancing.

        Returns a node.
        '''
        nextNode = node.leftChild
        node.leftChild = nextNode.rightChild
        node.update()
        nextNode.rightChild = node
        nextNode.update()

        return nextNode

    def _rotateLeftRight(self, node):
        r'''
        Rotates a node right twice.

        Used internally by TimespanTree during tree rebalancing.

        Returns a node.
        '''
        node.leftChild = self._rotateRightRight(node.leftChild)
        node.update()
        nextNode = self._rotateLeftLeft(node)
        return nextNode

    def _rotateRightLeft(self, node):
        r'''
        Rotates a node right, then left.

        Used internally by TimespanTree during tree rebalancing.

        Returns a node.
        '''
        node.rightChild = self._rotateLeftLeft(node.rightChild)
        node.update()
        nextNode = self._rotateRightRight(node)
        return nextNode

    def _rotateRightRight(self, node):
        r'''
        Rotates a node left, then right.

        Used internally by TimespanTree during tree rebalancing.

        Returns a node.
        '''
        nextNode = node.rightChild
        node.rightChild = nextNode.leftChild
        node.update()
        nextNode.leftChild = node
        nextNode.update()
        return nextNode

    def getNodeByOffset(self, offset):
        r'''
        Searches for a node whose offset is `offset` in the subtree
        rooted on `node`.

        Used internally by TimespanTree.

        Returns a Node object or None
        '''
        def recurse(offset, node):
            if node is not None:
                if node.offset == offset:
                    return node
                elif node.leftChild and offset < node.offset:
                    return recurse(offset, node.leftChild)
                elif node.rightChild and node.offset < offset:
                    return recurse(offset, node.rightChild)
            return None
    
        return recurse(offset, self.rootNode)


    def _getNodeAfter(self, offset):
        r'''
        Gets the first node after `offset`.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> n1 = tree._getNodeAfter(0.5)
        >>> n1
        <Node: Start:1.0 Indices:(7:7:11:11) Length:{4}>
        >>> n2 = tree._getNodeAfter(0.6)
        >>> n2 is n1
        True
        '''
        def recurse(node, offset):
            if node is None:
                return None
            result = None
            if node.offset <= offset and node.rightChild:
                result = recurse(node.rightChild, offset)
            elif offset < node.offset:
                result = recurse(node.leftChild, offset) or node
            return result
        result = recurse(self.rootNode, offset)
        if result is None:
            return None
        return result
    
    def getOffsetAfter(self, offset):
        r'''
        Gets start offset after `offset`.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> tree.getOffsetAfter(0.5)
        1.0

        Returns None if no succeeding offset exists.

        >>> tree.getOffsetAfter(35) is None
        True

        Generally speaking, negative offsets will usually return 0.0

        >>> tree.getOffsetAfter(-999)
        0.0
        '''
        node = self._getNodeAfter(offset)
        if node:            
            return node.offset
        else:
            return None

    def _getNodeBefore(self, offset):
        '''
        Finds the node immediately before offset.
        
        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> tree._getNodeBefore(100)  # last node in piece
        <Node: Start:35.0 Indices:(161:161:165:165) Length:{4}>
        '''
        
        def recurse(node, offset):
            if node is None:
                return None
            result = None
            if node.offset < offset:
                result = recurse(node.rightChild, offset) or node
            elif offset <= node.offset and node.leftChild:
                result = recurse(node.leftChild, offset)
            return result
        result = recurse(self.rootNode, offset)
        if result is None:
            return None
        return result
    
    def getOffsetBefore(self, offset):
        r'''
        Gets the start offset immediately preceding `offset` in this
        offset-tree.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> tree.getOffsetBefore(100)
        35.0

        Return None if no preceding offset exists.

        >>> tree.getOffsetBefore(0) is None
        True
        '''
        node = self._getNodeBefore(offset)
        if node is None:
            return None
        return node.offset

    def _remove(self, node, offset):
        r'''
        Removes a node at `offset` in the subtree rooted on `node`.

        Used internally by TimespanTree.

        Returns a node which represents the new rootNote.
        '''
        if node is not None:
            if node.offset == offset:
                ### got the right node!
                if node.leftChild and node.rightChild:
                    nextNode = node.rightChild
                    while nextNode.leftChild: # farthest left child of the right child.
                        nextNode = nextNode.leftChild
                    node.offset = nextNode.offset
                    node.payload = nextNode.payload
                    node.rightChild = self._remove(node.rightChild, nextNode.offset)
                    node.update()
                else:
                    node = node.leftChild or node.rightChild
            elif node.offset > offset:
                node.leftChild = self._remove(node.leftChild, offset)
                node.update()
            elif node.offset < offset:
                node.rightChild = self._remove(node.rightChild, offset)
                node.update()
        return self._rebalance(node)

#-------------------------------#
if __name__ == '__main__':
    import music21
    music21.mainTest()