from collections import deque
import os
from sys import argv, stderr, stdout
from scanner import Scanner

# Constants from other file
SUB = 3
STORE = 4
LOAD = 5
# INTO, COMMA, EOL, EOF shared
LSHIFT = 10
RSHIFT = 14
MULT = 12
ADD = 13

# add constant category that is just number

LOADI = 0
NOP = 1
OUTPUT = 2
ARITHOP = 3
MEMOP = 4
CONSTANT = 5
INTO = 6
COMMA = 7
EOL = 8
EOF = 9
REGISTER = 10
COMMENT = 11

weights = [1, 1, 1, 1, 6, 6, 0, 0, 0, 0, 1, 0, 3, 1, 1]
ERROR = -1
INVALID = -2

# Statuses
NOTREADY = 1
READY = 2
ACTIVE = 3
RETIRED = 4

errorflag = False
wordArr = ["loadI", "nop", "output", "sub", "store", "load", "=>", ',', "\\n",  "", "lshift", "COMMENT", "mult", "add", "rshift"]

maxreg = 0
beeboop = 32768
class IRNode:
    def __init__(self, linenum, sr1: int = None, sr2: int = None, sr3: int = None) -> None:
        self.linenum = linenum
        self.opcode = 0
        self.sr1 = sr1
        self.sr2 = sr2
        self.sr3 = sr3
        self.vr1 = None
        self.vr2 = None
        self.vr3 = None
        self.pr1 = None
        self.pr2 = None
        self.pr3 = None
        self.nu1 = None
        self.nu2 = None
        self.nu3 = None
        self.prev = self
        self.next = self
        pass
    
    def getOpcode(self):
        return self.opcode
    
    def insertAfter(self, node):
        self.next.prev = node
        node.next = self.next
        node.prev = self
        self.next = node
        
    def __str__(self) -> str:
        return f"{wordArr[self.opcode]}     [{self.sr1}], [{self.sr2}], [{self.sr3}], [{self.vr1}], [{self.vr2}], [{self.vr3}], [{self.pr1}], [{self.pr2}], [{self.pr3}], [{self.nu1}], [{self.nu2}], [{self.nu3}]"
    
    def printVR(self):
        if (self.opcode == LOAD):
            print(f"{wordArr[self.opcode]} r{self.vr1} => r{self.vr3}")
        elif (self.opcode == STORE):
            print(f"{wordArr[self.opcode]} r{self.vr1} => r{self.vr2}")
        elif (self.opcode == LOADI):
            print(f"{wordArr[self.opcode]} {self.sr1} => r{self.vr3}")
        elif (self.opcode == ADD or self.opcode == SUB or self.opcode == MULT or self.opcode == LSHIFT or self.opcode == RSHIFT):
            print(f"{wordArr[self.opcode]} r{self.vr1}, r{self.vr2} => r{self.vr3}")
        elif (self.opcode == OUTPUT):
            print(f"{wordArr[self.opcode]} {self.sr1}")
        else:
            print(f"{wordArr[self.opcode]}")
            
    def printPR(self):
        if (self.opcode == LOAD):
            print(f"{wordArr[self.opcode]} r{self.pr1} => r{self.pr3}")
        elif (self.opcode == STORE):
            print(f"{wordArr[self.opcode]} r{self.pr1} => r{self.pr2}")
        elif (self.opcode == LOADI):
            print(f"{wordArr[self.opcode]} {self.sr1} => r{self.pr3}")
        elif (self.opcode == ADD or self.opcode == SUB or self.opcode == MULT or self.opcode == LSHIFT or self.opcode == RSHIFT):
            print(f"{wordArr[self.opcode]} r{self.pr1}, r{self.pr2} => r{self.pr3}")
        elif (self.opcode == OUTPUT):
            print(f"{wordArr[self.opcode]} {self.sr1}")
        else:
            print(f"{wordArr[self.opcode]}")
        
def buildIR(filename):
    scanner = Scanner(filename)
    scanner.readLine()
    ir = parseLine(scanner)
    opcount = 0
    is_error = False
    head = IRNode(-1)
    
    while not scanner.getEOF():
        if ir.getOpcode() != ERROR and ir.getOpcode() != NOP:
            head.prev.insertAfter(ir)
            opcount += 1
        else:
            is_error = True
        ir = parseLine(scanner)
        
    # if is_error == True:
    #     print("Due to syntax errors, run terminates.")
    # else:
    #     node = head
    #     while (node.next != head):
    #         print(node.next)
    #         node = node.next
    return (head, scanner.maxreg, opcount)
            
def parseLine(scanner):
    word = scanner.readWord()
    
    while word[0] == EOL:
        word = scanner.readWord()
        
    node = IRNode(scanner.getLine())
    
    if word[0] == MEMOP:
        node.opcode = word[1]
        word = scanner.readWord()
        if word[0] == REGISTER:
            node.sr1 = word[1]
            word = scanner.readWord()
            if word[0] == INTO:
                word = scanner.readWord()
                if word[0] == REGISTER:
                    if node.opcode == STORE:
                        node.sr2 = word[1]
                    else:
                        node.sr3 = word[1]
                    word = scanner.readWord()
                    if word[0] == EOL:
                        return node
                    else:
                        print("ERROR " + str(node.linenum) + ": Extra words in " + scanner.wordArr[node.opcode] + " operation")
                        node.opcode = ERROR
                        errorFlag = True
                        return node
                else:
                    print("ERROR " + str(node.linenum) + ": Missing second source register in " + scanner.wordArr[node.opcode])
                    node.opcode = ERROR
                    errorFlag = True
                    return node
            else:
                print("ERROR " + str(node.linenum) + ":  Missing '=>' in " + scanner.wordArr[node.opcode])
                node.opcode = ERROR
                errorFlag = True
                return node
        else:
            print("ERROR " + str(node.linenum) + ": missing first source register in " + scanner.wordArr[node.opcode])
            node.opcode = ERROR
            errorFlag = True
            return node
    elif word[0] == LOADI:
        node.opcode = word[1]
        word = scanner.readWord()
        if word[0] == CONSTANT:
            node.sr1 = word[1]
            word = scanner.readWord()
            if word[0] == INTO:
                word = scanner.readWord()
                if word[0] == REGISTER:
                    node.sr3 = word[1]
                    word = scanner.readWord()
                    if word[0] == EOL:
                        return (node)
                    else:
                        print("ERROR " + str(node.linenum) + ": Extra words in " + scanner.wordArr[node.opcode] + " operation")
                        node.opcode = ERROR
                        errorFlag = True
                        return node
                else:
                    print("ERROR " + str(node.linenum) + ": Missing second source register in " + scanner.wordArr[node.opcode])
                    node.opcode = ERROR
                    errorFlag = True
                    return node
            else:
                print("ERROR " + str(node.linenum) + ": Missing '=>' in " + scanner.wordArr[node.opcode])
                node.opcode = ERROR
                errorFlag = True
                return node
        else:
            print("ERROR " + str(node.linenum) + ": missing first constant in " + scanner.wordArr[node.opcode])
            node.opcode = ERROR
            errorFlag = True
            return node
    elif word[0] == ARITHOP:
        node.opcode = word[1]
        word = scanner.readWord()
        if word[0] == REGISTER:
            node.sr1 = word[1]
            word = scanner.readWord()
            if word[0] == COMMA:
                word = scanner.readWord()
                if word[0] == REGISTER:
                    node.sr2 = word[1]
                    word = scanner.readWord()
                    if word[0] == INTO:
                        word = scanner.readWord()
                        if word[0] == REGISTER:
                            node.sr3 = word[1]
                            word = scanner.readWord()
                            if word[0] == EOL:
                                return (node)
                            else:
                                print("ERROR " + str(node.linenum) + ": Extra words in " + scanner.wordArr[node.opcode] + " operation")
                                node.opcode = ERROR
                                errorFlag = True
                                return node
                        else:
                            print("ERROR " + str(node.linenum) + ": Missing third source register in +" + scanner.wordArr[node.opcode])
                            node.opcode = ERROR
                            errorFlag = True
                            return node
                    else:
                        print("ERROR " + str(node.linenum) + ": Missing '=>' in " + scanner.wordArr[node.opcode])
                        node.opcode = ERROR
                        errorFlag = True
                        return node
                else:
                    print("ERROR " + str(node.linenum) + ": Missing second source register in" + scanner.wordArr[node.opcode])
                    node.opcode = ERROR
                    errorFlag = True
                    return node
            else:
                print("ERROR " + str(node.linenum) + ": Missing comma in " + scanner.wordArr[node.opcode])
                node.opcode = ERROR
                errorFlag = True
                return node
        else:
            print("ERROR " + str(node.linenum) + ": Missing first source register in " + scanner.wordArr[node.opcode])
            node.opcode = ERROR
            errorFlag = True
            return node
    elif word[0] == OUTPUT:
        node.opcode = word[1]
        word = scanner.readWord()
        if word[0] == CONSTANT:
            node.sr1 = word[1]
            word = scanner.readWord()
            if word[0] == EOL:
                return node
            else:
                print("ERROR " + str(node.linenum) + ": Extra words in " + scanner.wordArr[node.opcode] + " operation")
                node.opcode = ERROR
                errorFlag = True
                return node
        else:
            print("ERROR " + str(node.linenum) + ": Missing constant in " + scanner.wordArr[node.opcode])
            node.opcode = ERROR
            errorFlag = True
            return node
    elif word[0] == NOP:
        node.opcode = word[1]
        word = scanner.readWord()
        if word[0] == EOL:
            return (node)
        else:
            print("ERROR " + str(node.linenum) + ": Extra words in " + scanner.wordArr[node.opcode] + " operation")
            node.opcode = ERROR
            errorFlag = True
            return node
    elif word[0] == EOF:
        node.opcode = EOF
        return node
    elif word[0] == ERROR:
        # We don't print errors twice
        node.opcode = ERROR
        errorFlag = True
        return node
    else:
        print("ERROR  " + str(node.linenum) + ": Invalid starting part of speech, " + scanner.categoryArr[word[0]])
        node.opcode = ERROR
        errorFlag = True
        return node    
vrName1 = 0
k = 0

def main ():
    argslst = argv
    filename = argslst[-1]
    if len(argslst) < 1: 
        print("ERROR: not enough arguments in the command line", file=stderr)
        return

    if "-h" in argslst:
        h_flag()
        return
    if os.path.exists(filename) == False:
        print("ERROR: file does not exists or filepath is missing", file=stderr)
        return
    elif "schedule" in argslst:
        leaves, roots, mappy = buildgraph(filename)
        weightit(roots, mappy)
        schedule(leaves, mappy)
        return
    
        
def h_flag():
    print("Valid Command Line Arguments:")
    print("\n")
    print("Filename: the filename can either be a relative or an absolute path")
    print("-h: produces a list of valid command-line arguments and includes descriptions of all command-line arguments")
    print("schedule <name>: scans, parses, renames, and produces an ILOC program that is equivalent to the input, rearranged so that the amount of cycles needed to execute this code decreases.")

def rename(filename):

    (head, maxreg, blockLength) = buildIR(filename)

    vrName = 0
    sr_to_vr = [INVALID for i in range(maxreg + 1)]
    last_use = [float("inf") for i in range(maxreg + 1)]
    nodeList = [None for i in range(blockLength)]
    listidx = blockLength - 1
    idx = blockLength
    curr = head.prev
    while curr != head:
        if curr.opcode == NOP:
            curr.next.prev = curr.prev
            curr.prev.next = curr.next
            curr = curr.prev
            continue
        if curr.sr3 != None:
            if sr_to_vr[curr.sr3] == INVALID:
                sr_to_vr[curr.sr3] = vrName
                vrName += 1
            curr.vr3 = sr_to_vr[curr.sr3]
            curr.nu3 = sr_to_vr[curr.sr3]
            sr_to_vr[curr.sr3] = INVALID
            last_use[curr.sr3] = float("inf")
        else:
            curr.vr3 = INVALID
        if curr.sr2 != None:
            if sr_to_vr[curr.sr2] == INVALID:
                sr_to_vr[curr.sr2] = vrName
                vrName += 1
            curr.vr2 = sr_to_vr[curr.sr2]
            curr.nu2 = last_use[curr.sr2]
        else:
            curr.vr2 = INVALID
        if curr.sr1 != None and curr.opcode != OUTPUT and curr.opcode != LOADI:
            if sr_to_vr[curr.sr1] == INVALID:
                sr_to_vr[curr.sr1] = vrName
                vrName += 1
            curr.vr1 = sr_to_vr[curr.sr1]
            curr.nu1 = last_use[curr.sr1]
        else: curr.vr1 = INVALID
        if curr.sr1 != None and curr.opcode != OUTPUT and curr.opcode != LOADI:
            last_use[curr.sr1] = idx
        if curr.sr2 != None:
            last_use[curr.sr2] = idx
        idx -= 1
        
        nodeList[listidx] = curr
        print(listidx)
        curr.printVR()
        listidx -= 1
        curr = curr.prev
    # print(nodeList)
    return nodeList, vrName
    #return head, vrName
    # node = head 
    # while (node.next != head):
    #     node.next.printVR()
    #     node = node.next
class ScheduleNode:
    def __init__(self, index) -> None:
        self.index = index
        self.kids = set([])
        self.parents = set([])
        self.status = NOTREADY
        self.weight = 0
        self.startcycle = 0
        pass
    
    
    
def buildgraph(filename):
 
    roots = set()
    leaves = set()
    outputs = set()
    mrs = None
    mro = None

    reads = set()
    nodes, vrName = rename(filename)
    
    map1 = [None for i in range(vrName)]
    for i in range(len(nodes)):
        if nodes[i] == None:
            continue
        if nodes[i].opcode != NOP:
            newnode = ScheduleNode(i)
            
            if nodes[i].vr3 != INVALID:
                map1[nodes[i].vr3] = newnode
                if nodes[i].nu3 == float('inf'):
                    roots.add(newnode)
            if nodes[i].vr1 != INVALID:
                parentNode = map1[nodes[i].vr1]
                parentNode.kids.add((weights[nodes[parentNode.index].opcode], newnode))
                newnode.parents.add((weights[nodes[parentNode.index].opcode], parentNode))
            if nodes[i].vr2 != INVALID:
                parentNode = map1[nodes[i].vr2]
                parentNode.kids.add((weights[nodes[parentNode.index].opcode], newnode))
                newnode.parents.add((weights[nodes[parentNode.index].opcode], parentNode))
        
        if nodes[i].opcode == OUTPUT:
            for item in outputs:
                parentNode = item
                parentNode.kids.add((1, newnode))
                newnode.parents.add((1, parentNode))
            outputs.add(newnode)
            mro = newnode
                
        if nodes[i].opcode == OUTPUT or nodes[i].opcode == LOAD:
            reads.add(newnode)
            storeNode = mrs
            storeNode.kids.add((1, newnode))
            newnode.parents.add((1, storeNode))
            
        if nodes[i].opcode == STORE:
            if mrs != None:
                newnode.parents.add((weights[nodes[i].opcode], parentNode))
                mrs.kids.add((weights[nodes[i].opcode], newnode))
            for read in reads:
                parentNode = read
                parentNode.kids.add((1, newnode))
                
                newnode.parents.add((1, parentNode))
            mrs = newnode
            
        if len(newnode.parents) == 0:
            newnode.status = READY
            leaves.add(newnode)
    if mro != None:
        roots.add(mro)
    
    print("roots")
    for item in roots:
        print(item.index)
        nodes[item.index].printVR()
        
    print("leaves")
    for item in leaves:
        print(item.index)
        nodes[item.index].printVR()
    return leaves, roots, nodes
     
def weightit(roots, map):
    map4 = map
    queue = deque()
    print("GOT IN WEIGHT")
    for root in roots:
        root.weight = 10 * weights[map4[root.index].opcode] + len(root.kids)
        print("WEIGHT OF ROOT IS " + str(root.weight))
        print(root.parents)
        queue.append(root)
    while queue:
        print("yes queue")
        
        node = queue.popleft()
        print("kid of nodes is " + str(node.kids))
        print("NEW LEN QUEUE IS " + str(len(queue)))
        for parent in node.parents:
            print("OLD WEIGHT IS " + str(parent[0]))
            
            newweight = node.weight + 10 * parent[0] + len(parent[1].kids) - len(node.kids)
            if (newweight > parent[1].weight):
                print("weight changed")
                parent[1].weight = newweight
                queue.append(parent[1])
            print("NEW WEIGHT IS " + str(parent[1].weight))
   
def printScheduleNodes(node1, node2):
    str1 = ""
    str2 = ""
    if (node1.opcode == LOAD):
        str1 = (f"{wordArr[node1.opcode]} r{node1.vr1} => r{node1.vr3}")
    elif (node1.opcode == STORE):
        str1 = (f"{wordArr[node1.opcode]} r{node1.vr1} => r{node1.vr2}")
    elif (node1.opcode == LOADI):
        str1 = (f"{wordArr[node1.opcode]} {node1.sr1} => r{node1.vr3}")
    elif (node1.opcode == ADD or node1.opcode == SUB or node1.opcode == MULT or node1.opcode == LSHIFT or node1.opcode == RSHIFT):
        str1 = (f"{wordArr[node1.opcode]} r{node1.vr1}, r{node1.vr2} => r{node1.vr3}")
    elif (node1.opcode == OUTPUT):
        #print("SOMETHING HAPPENS HERE")
        str1 = (f"{wordArr[node1.opcode]} {node1.sr1}")
    else:
        str1 = (f"{wordArr[node1.opcode]}")  
            
    if (node2.opcode == LOAD):
        str2 = (f"{wordArr[node2.opcode]} r{node2.vr1} => r{node2.vr3}")
    elif (node2.opcode == STORE):
        str2 = (f"{wordArr[node2.opcode]} r{node2.vr1} => r{node2.vr2}")
    elif (node2.opcode == LOADI):
        str2 = (f"{wordArr[node2.opcode]} {node2.sr1} => r{node2.vr3}")
    elif (node2.opcode == ADD or node2.opcode == SUB or node2.opcode == MULT or node2.opcode == LSHIFT or node2.opcode == RSHIFT):
        str2 = (f"{wordArr[node2.opcode]} r{node2.vr1}, r{node2.vr2} => r{node2.vr3}")
    elif (node1.opcode == OUTPUT):
        #print("SOMETHING HAPPENS HERE 2")
        str2 = (f"{wordArr[node2.opcode]} {node2.sr1}")
    else:
        str2 = (f"{wordArr[node2.opcode]}") 
    
    return str1, str2                
               
def schedule(leaves, map):
    
    cycle = 1
    
    readySet = leaves
    map2 = map
    activeSet = set()
    op1 = ScheduleNode(-3)
    dummynop = IRNode(-1)
    dummynop.opcode = NOP
   
    while ((len(readySet) + len(activeSet)) != 0):
        print("NEW CYCLE NEW CYCLE ------------------- " + str(cycle))
        op1 = ScheduleNode(-3)
        i = 0
        for leaf in readySet: 
            # print("new leaf weight is " + str(leaf.weight))
            # print("old op weight is " + str(op1.weight))
            if leaf.weight > op1.weight:
                op1 = leaf
                # print("op1 updated")
        if (op1.index != -3):
            readySet.remove(op1)
            op1.status = ACTIVE
            op1.startcycle = cycle
            activeSet.add(op1)
            
        ### this got here and makes enough sense, it did go through the weights and update properly    
        
        op1opcode = map2[op1.index].opcode
        #if op1opcode == OUTPUT:
            #print("output node is " + str(map2[op1.index])) 
        # op1node = map2[op1.index]
        # op1node.printVR()
        # print("op1 index is " + str(op1.index))
        # print("#########")
        
        op2 = ScheduleNode(-3)
        for leaf in readySet:
            
            leafop = map2[leaf.index].opcode
            if (leafop == LOAD or leafop == STORE) and (op1opcode == LOAD or op1opcode == STORE):
                continue
            if leafop == MULT and op1opcode == MULT:
                continue
            if leafop == OUTPUT and op1opcode == OUTPUT:
                print("does it go in here?")
                continue
            if leaf.weight > op2.weight:
                op2 = leaf
        if op2.index != -3:
            readySet.remove(op2)
            activeSet.add(op2)
            op2.status = ACTIVE
            op2.startcycle = cycle
        # print("After finding op1 and op1, the length of the ready set is " + str(len(readySet)) + " and the length of the active set is " + str(len(activeSet)))
        # print("op2 is " )
        # map2[op2.index].printVR()
        # print("########")
        if map2[op1.index].opcode == MULT:
            temp = op1
            op1 = op2
            op2 = temp
        if map2[op2.index].opcode == LOAD or map2[op2.index].opcode == STORE:
            temp = op1
            op1 = op2
            op2 = temp
        
        node1 = dummynop
        if op1.index != -3:
            node1 = map2[op1.index]
        
        node2 = dummynop
        if op2.index != -3:
            node2 = map2[op2.index]

        f0, f1 = printScheduleNodes(node1, node2) 

        print("[ " + f0 + " ; " + f1 + " ]")   
        
        cycle += 1
        # print("length of active set is " + str(len(activeSet)))
        to_be_retired = set()
        for anode in activeSet:
            # print("anode is " + str(map2[anode.index].printVR()))
            nodeweight = weights[map2[anode.index].opcode]
            print("Node weight is " + str(nodeweight) + " its startcycle " + str(anode.startcycle) + " current cycle " + str(cycle))
            if nodeweight + anode.startcycle - cycle == 0:
                anode.status = RETIRED
                to_be_retired.add(anode)
                for kid in anode.kids:
                    allgood = True
                    for parent in kid[1].parents:
                        if (parent[1].status == RETIRED or (parent[1].status == ACTIVE and parent[0] == 1)):
                            continue
                        else:
                            allgood = False
                    if allgood == True:
                        print("it added a kid")
                        if (kid[1].status == READY):
                            print("BAD")
                        kid[1].status == READY
                        readySet.add(kid[1])
                        # print("node added is ")
                        map2[kid[1].index].printVR
            elif cycle - anode.startcycle == 1:
                for kid in anode.kids:
                    allgood = True
                    for parent in kid[1].parents:
                        print("new parent")
                        map2[parent[1].index].printVR()
                        if (parent[1].status == RETIRED or (parent[1].status == ACTIVE and parent[0] == 1)):
                            continue
                        else:
                            allgood = False
                    if allgood == True:
                        print("it added a kid")
                        if (kid[1].status == READY):
                            print("BAD")
                        kid[1].status == READY
                        readySet.add(kid[1])
        for anode in to_be_retired:
            if anode.status == RETIRED:
                activeSet.remove(anode)
                # print("NODE REMOVED")
                # map2[anode.index].printVR()
        # print("length of ready set is " + str(len(readySet)))
        # print("length of active set is " + str(len(activeSet)))
    return

if __name__ == "__main__":
    main()