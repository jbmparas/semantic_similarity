# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 13:32:14 2019

@author: parmal

Notation :
    
    1. gram (gram1, gram2) --> parsed sentense 
    2. subt --> Subtree 
    3. partree --> Parents Tree
    4. start_node --> Start Concept or word
    5. end_node ---> Targeted Concept or word
    6. first_item --> all concept of start_node 
    7. second_item --> all concept of end/targeted_node
    8. gram1_le --> List of words in parsed sentence1
    9. gram2_le --> List of words in parsed sentence2
    10. gram1_label --> List of label of words in parsed sentence1
    11. gram2_label --> List of label of words in parsed sentence2
    12. parse_sent1 --> parsed sentence1
    13. parse_sent2 --> parsed sentence2
    

"""

# import important libaries 


from stat_parser import Parser
from nltk.tree import *
import nltk
import sys
import requests
import tqdm
import matplotlib.pyplot as plt
import networkx as nx

parser=Parser()


class tree_parser:
    def __init__(self):
#        self.sent1 = sent1
#        self.sent2 = sent2
        pass
    
    def __sub_tree_parser(self,gram):
        '''
            This function gives all subtrees of a Tree and parent trees of subtrees
        '''
        tree = Tree.fromstring(str(gram))
        ptree = ParentedTree.convert(tree)
        sub_tree = []
        parent_tree = []
        for subtree in ptree.subtrees(): #(lambda t: t.height() > 2)
            sub_tree.append(subtree)
            parent_tree.append(subtree.parent())
        return(sub_tree,parent_tree)
        
    def match_tree(self,sent1,sent2):
        '''
            This function matches the two trees nodes. If a node is common in both the trees,
            then that node will removed from both the trees
            final output will come as not matched_tree
        '''
        Flag = False
        if len(sent2.split()) > len(sent1.split()):
            pass
        else:
            temp = sent1
            sent1 = sent2
            sent2 = temp
            Flag = True
        gram=parser.parse(sent1.lower())
        gram1=parser.parse(sent2.lower())
        subt1, partree1 = self.__sub_tree_parser(gram1)
        subt, partree = self.__sub_tree_parser(gram)
        index = 0
        while index <= len(subt1)+1:
            # Do something to my_list[index]
            for i in range(len(subt1)):
                if subt1[i] in subt:
                    k = subt1[i]
    #                 print('Matched',k)
                    l = subt[subt.index(k)]
        #             k.pretty_print()
                    try:
                        del gram1[k.treeposition()]
                        del gram[l.treeposition()]
                    except:
                        print('Exact Same sentence')
                        sys.exit('Exact Same sentence')
                    break
            index += 1
            subt1, partree1 = self.__sub_tree_parser(gram1)
            subt, partree = self.__sub_tree_parser(gram)
    #     gram.pretty_print()
    #     gram1.pretty_print()  
        if Flag:
    #         gram1.pretty_print()
    #         gram.pretty_print() 
            return(gram1, gram)
        else:
    #         gram.pretty_print()
    #         gram1.pretty_print()  
            return(gram, gram1)
            
class ConceptNet_graph:
    def __init__(self):
#        self.sent1 = sent1
#        self.sent2 = sent2
        pass   
    
    def __compaire(self,start_node, second_item, end_node):
        '''
            This function compaire the Level concept with end_nodes's concept and return the common concept 
            between them
        '''
        first_item = [start_node]
    #     print('First',start_node,end_node)
        start_node1 = requests.get('http://api.conceptnet.io/uri?language=en&text=' + ' '.join(start_node.split('_'))).json()["@id"]
    #     end_node = requests.get('http://api.conceptnet.io/uri?language=en&text=' + ' '.join(end_node.split('_'))).json()["@id"]
       
        response = requests.get('http://api.conceptnet.io/query?start='+start_node1+'&limit=1000')
        obj = response.json()
        
        for edge in obj['edges'] :
            try:
                if edge['end']['language']=='en' and edge['weight']>=1 and edge['end']['term'].split('/')[-1] != 'n':
                    first_item.append(edge['end']['term'].split('/')[-1])
            except:
                pass
        con = set(first_item).intersection(set(second_item))
        if len(con)>0:
    #         print('Second',start_node,end_node)
            edges = [(start_node,k) for  k in list(con)]
            edges1 = [(k,end_node) for  k in list(con)]
            edges.extend(edges1)
            return(first_item,list(con),edges, True)
        else:
            return(first_item, list(con), False,False)
            
    def __node(self,start_node,end_node,url):
        '''
            This function returns all concept of stat_node & end_node, common concept between stat_node & end_node and all edges 
            between stat_node & end_node at Level-1
        '''
        first_item = [start_node]
        second_item = [end_node]
        start_node1 = requests.get('http://api.conceptnet.io/uri?language=en&text=' + ' '.join(start_node.split('_'))).json()["@id"]
        end_node1 = requests.get('http://api.conceptnet.io/uri?language=en&text=' + ' '.join(end_node.split('_'))).json()["@id"]
        
        response = requests.get('http://api.conceptnet.io/query?start='+start_node1+url)
        obj = response.json()
        
        for edge in obj['edges'] :
            try:
                if edge['end']['language']=='en' and edge['weight']>=1 and edge['end']['term'].split('/')[-1] != 'n':
                    first_item.append(edge['end']['term'].split('/')[-1])
            except:
                pass
        response = requests.get('http://api.conceptnet.io/query?start='+end_node1+url)
        obj = response.json()
        
        for edge in obj['edges'] :
            try:
                if edge['end']['language']=='en' and edge['weight']>=1 and edge['end']['term'].split('/')[-1] != 'n':
                    second_item.append(edge['end']['term'].split('/')[-1])
            except:
                pass
    
        con = set(first_item).intersection(set(second_item))
        if len(con)>0:
            
            edges = [(start_node,k) for  k in list(con)]
            edges1 = [(k,end_node) for  k in list(con)]
            edges.extend(edges1)
            return(first_item,second_item,list(con),edges, True)
        else:
            return(first_item,second_item, list(con), False,False)
            
    def __get_concept_graph(self,start_node,end_node, lev = 2):
        '''
            This function use to get path between start_node and end_node upto the level 3. For a level it goes upto 5 words only.
        '''
    
        url1 = '&limit=1000'
        G=nx.Graph()
        # G.add_node("a")
        G.add_nodes_from([start_node,end_node])
        nodes_from = []
        for level in tqdm.tqdm(range(1,lev+1)):
            lis_lev = []
            node_lev = []
            if level==1:
                first_item,second_item, con, edges, status = self.__node(start_node,end_node,url1)
                if status:
                    G.add_nodes_from(con)
                    G.add_edges_from(edges)
                    temp = [[start_node,start_node,[i for i in first_item if i not in con]]]
                else:
                    temp = [[start_node,start_node,first_item.copy()]]
        #         print(level,con)
            else:
    #             print(level,con)
                if len(con)>0:
                    break
                else:
                    i = 1
                    j = 1
                    for m in temp:
                        for k in m[2]:
                            k_item, con, edges, status = self.__compaire(k, second_item,end_node)
                            if status:
                                node_lev.append(m[0])
                                G.add_nodes_from(con)
                                edges.append((m[0],m[1]))
                                edges.append((m[1],k))
    
                                G.add_edges_from(edges)
                                i= i+1
    #                             print(i,con,edges)
                            else:
    #                             print('else',k,con,j,edges)
                                G.add_edges_from([(m[0],m[1])])
                                lis_lev.append([m[1],k,[i for i in k_item if((i not in m[2]) or (i not in list(G.nodes())))]])
                                j = j+1
    
                            if i > 3 or j > 10:
                                break
                        if i > 3:
                            break
                    nodes_from.append(node_lev)
                    temp = lis_lev.copy()
        pos = nx.spring_layout(G,k=0.5,iterations=20)
        nx.draw(G,pos, with_labels=True, node_color='orange', node_size=400, edge_color='black', linewidths=10, font_size=10)
    
        plt.figure(figsize=(250,250))
        # plt.savefig("simple_path.jpeg") # save as png
        plt.show()
        return(G)
        
    def get_relation_path(self,start_node,end_node):
        url = '&rel=/r/IsA&limit=1000'
        url1 = '&limit=1000'
        first_item,second_item, con, edges, status = self.__node(start_node,end_node,url)
        
        if len(con)>0:
            con = [con[0]]
            con.insert(0,start_node)
            con.append(end_node)
            return([con])
        else:
            first_item,second_item, con, edges, status = self.__node(start_node,end_node,url1)
            if len(con)>0:
                con = [con[0]]
                con.insert(0,start_node)
                con.append(end_node)
                return [con]
            else:
                G = self.__get_concept_graph(start_node,end_node)
                try:
                    zz=[p for p in nx.all_shortest_paths(G,source= start_node,target= end_node)]
                    return zz
                except:
                    return([[start_node,'None',end_node]])

    def __get_rel_label(self,start_node,end_node):
        '''
            Get the all relation between start_node,end_node
        '''
        start_node = requests.get('http://api.conceptnet.io/uri?language=en&text=' + ' '.join(start_node.split('_'))).json()["@id"]
        end_node = requests.get('http://api.conceptnet.io/uri?language=en&text=' + ' '.join(end_node.split('_'))).json()["@id"]
        response = requests.get('http://api.conceptnet.io/query?node='+start_node+'&other='+end_node+'&limit=1000')
        obj = response.json()
        return([i.get('rel').get('label') +'_'+ i['end']['label'] for i in obj['edges'] ])
        
    ### Calculate the relationship
    def all_relation(self,rel):
        '''
            Get the all relation between all nodes [apple, fruit, orange] >>>> apple---> fruit ---> orange
        '''
        temp = []
        for re in rel:
            for m in range(len(re)-1):
                temp.extend(self.__get_rel_label('_'.join(re[m].split()),'_'.join(re[m+1].split())))
        return(list(set(temp)))
        
    def edit(self,wor,tree,change_sent):
        '''
            Replace the leaf node with new relation or PP/VP/QP
        '''
        t = nltk.Tree.fromstring(str(tree))
        for leafPos in t.treepositions('leaves'):
            if t[leafPos] == wor:
                t[leafPos] =  change_sent 
        return(t)
        
class execution:
    def __init__(self,conceptObj):
        self.conceptObj = conceptObj
#        self.sent2 = sent2
    def __get_intersection(self,gram1_le,gram2_le,parse_sent1,parse_sent2, label):
        '''
            This function will calculate the intersection at Pharse level, It will run for only one Pharse
        '''
        label_flag = False
        node_diff = []
        rel_diff = []
    #     print(parse_sent)
        start_node = '_'.join(gram1_le.split('-'))
        end_node = '_'.join(gram2_le.split('-'))
        print(start_node,end_node)
        rel = self.conceptObj.get_relation_path(start_node,end_node)
        if str(rel[0][1]) == 'None':
            rel[0][1] = label
            label_flag = True
            print(rel[0][1],label,'reached')
    #         print(rel,rel[0][1])
        node_diff.append((start_node,end_node))
    
        ### Calculate the relationship
        temp_rel = self.conceptObj.all_relation(rel)
        if len(temp_rel)==0:
            rel_diff.append(['None'])
        else:
            rel_diff.append(self.conceptObj.all_relation(rel))
        for leb in gram1_le.split('-'):
            if label_flag:
                parse_sent1 = self.conceptObj.edit(leb,parse_sent1,str('-->'.join(rel[0][1:-1])))
            else:
                parse_sent1 = self.conceptObj.edit(leb,parse_sent1,str(['-->'.join(rel[0][1:-1])]))
        for leb1 in gram2_le.split('-'):
            if label_flag:
                parse_sent2 = self.conceptObj.edit(leb1,parse_sent2,str('-->'.join(rel[0][1:-1])))
            else:
                parse_sent2 = self.conceptObj.edit(leb1,parse_sent2,str(['-->'.join(rel[0][1:-1])]))
        return (parse_sent1,parse_sent2,node_diff,rel_diff)
    
    def __get_chunk(self,gram1, condi):
        '''
            This function take input as parsed tree and list of pharse, It will return (list of Pharse trees and remain tree 
            which do not  have pharse) 
        '''
        PP = []
        for i in gram1.treepositions()[::-1]:
    #         print(gram1[i])
    #         try:
    #             if(gram1[i].label() in ['DT','CC'] ):
    #                 del gram1[i]
    #         except:
    #             pass
            try: 
                if(gram1[i].label() in condi ):
                    if len(gram1[i].leaves()) !=0:
                        PP.append(gram1[i])
                    del gram1[i]
    #                 gram1[i].pretty_print()
            except:
                pass
        return(gram1,PP)
        
    def __get_final_leaves_tag(self,gram1,p1):
        # Normal
        sent1_leaves = gram1.leaves()
        sent1_tag = [k[1] for k in gram1.pos()]
        # NP
        for k in range(len(p1)):
            sent1_leaves.extend(p1[k].leaves()) 
        for k in range(len(p1)):
            sent1_tag.extend([l[1] for l in p1[k].pos()])
        return(sent1_leaves,sent1_tag)
        
    def __execute_me(self,gram1_le,gram2_le,gram1_label,gram2_label,parse_sent1,parse_sent2):
        if len(gram2_le) == 0:
            gram2_le = ['']
            gram2_label= ['OTHR']
        elif len(gram1_le) == 0:
            gram1_le = ['']
            gram1_label= ['OTHR']
        else:
            pass
        combinations = [(a,b) for a in gram1_le for b in gram2_le]
        combinations_tag = [(a,b) for a in gram1_label for b in gram2_label]
    #     print(combinations,combinations_tag)
        word_diff = [] # make the list of tuple of different words which we are comparing like[(apple, orange)]
        relation_diff = [] # List of relation between two words like [IsA fruit, IsA food] etc.
        word_tag1 = [] # list of the pos_tag of words which we compaire [(NP,NP)] --> because apple is a NN, orange is a NN
    #     flag=0
        '''
            We will create all combination for all the words and tags
    
            If both the words has same tag then we will calculate the relation otherwise we will pass at first step and handle
            it into next for loop
    
            Next for loop :--- Please read below
        '''
        for k,tag in zip(combinations,combinations_tag):
            if tag[0]==tag[1]:
                print(k[0],k[1],tag[0],tag[1])
                parse_sent1,parse_sent2,node_diff,rel_diff = self.__get_intersection(k[0],k[1],parse_sent1,parse_sent2,tag[0]) #check label
                word_diff.append(node_diff)
                relation_diff.append(rel_diff)
                word_tag1.append([[tag[0],tag[1]]])
            else:
                pass
        '''
          Cont. .. Above we already calculate the realtion for words which has same pos_tag.
    
          Here we will check if words do not have same pos_tag then we will replace that word to their pos_tag
        '''
        for k,tag in zip(combinations,combinations_tag):
            if tag[0]==tag[1]:
                pass
            else:
                for n in k[0].split('-'):
                    if n in parse_sent1.leaves():
                        word_diff.append([(n,k[1])]) ####
                        relation_diff.append([['None']]) #####
                        word_tag1.append([[tag[0],tag[1]]])
                        parse_sent1 = self.conceptObj.edit(n,parse_sent1,tag[0])
                for m in k[1].split('-'):
                    if m in parse_sent2.leaves():
                        parse_sent2 = self.conceptObj.edit(m,parse_sent2,tag[1])
        return(parse_sent1,parse_sent2,word_diff,relation_diff,word_tag1)
        
        
    def calculate_intersection_differance(self,sent1,sent2):
        ### Change the order of sentence based on their length
        if len(sent1.split()) > len(sent2.split()):
            pass
        else:
            temp = sent1
            sent1 = sent2
            sent2 = temp
    
        gram1, gram2 = tree_parser().match_tree(sent1,sent2) ## Pass throw both the sentence to match_tree function and get the gram1 & gram2 as
                                                # not matched part of the tree
        word = [] # define the list for group of word which are different in both the trees like [[(apple, orange)],[(new_york,new_jersy)]]
        realtion = [] # List of relation between two different words
        word_tag =[] # Pos tag of words which are different in the both trees
        parse_sent1 = parser.parse(sent1.lower())
        parse_sent2 = parser.parse(sent2.lower())
        #     print('Before PP')
        #     gram1.pretty_print() ############################
        #     gram2.pretty_print()
        tree1, pp1 = self.__get_chunk(gram1,['PP','VP', 'QP']) # Further parse the gram1 and gram2 to segregate the PP, Vp, QP etc.
        tree2, pp2 = self.__get_chunk(gram2,['PP','VP', 'QP'])
        t1, p1 = self.__get_chunk(gram1,['NP'])
        t2, p2 = self.__get_chunk(gram2,['NP'])
        
        '''
            Part 1 : This will execute on leaves whichever is reamin in gram1 and gram2
        after doing segragation on PP, VP, QP
    
        ''' 
        gram1_le,gram1_label = self.__get_final_leaves_tag(gram1,p1)
        gram2_le,gram2_label =  self.__get_final_leaves_tag(gram2,p2)
        
        parse_sent1,parse_sent2,word_diff,relation_diff,word_tag1 = self.__execute_me(gram1_le,gram2_le,gram1_label,gram2_label,parse_sent1,parse_sent2)
        
        word.append(word_diff)
        realtion.append(relation_diff)
        word_tag.append(word_tag1)
        
        '''
            Part 2 : This will execute on leaves whichever is part of  PP, VP, QP. 
            Based on pp1, and pp2, we will define the rules
        '''    
        gram1_le = []
        gram1_label = []
        gram2_le = []
        gram2_label = []
    
        '''
            Condition:1-->
            If prepositional phrase in both sentences, then we will get the chunks for NP (To get accurate conceptNet relation [It will
            makes the company ---> the_company, the building ----> the_building])
    
            Get the leaves for both the sentences
        '''
        if len(pp1)>0 and len(pp2)>0:
            for i in pp1:
                t, pp_1 = self.__get_chunk(i,['NP'])
                lev, tag_ = self.__get_final_leaves_tag(i,pp_1)
                gram1_le.extend(lev)
                gram1_label.extend(tag_)
            for i in pp2:
                t, pp_2 = self.__get_chunk(i,['NP'])
                lev, tag_ = self.__get_final_leaves_tag(i,pp_2)
                gram2_le.extend(lev)
                gram2_label.extend(tag_)
            print('Both PP',gram1_le,gram2_le)
    
            '''
                Condition:2-->
                If prepositional phrase in second sentence, then we will get the chunks for NP (To get accurate conceptNet relation [It will
                makes the company ---> the_company, the building ----> the_building]) 
    
                Get the leaves for second sentence
            '''
        elif len(pp1)==0 and len(pp2)>0:
            print('Second PP')
            for i in pp2:
                t, pp_2 = self.__get_chunk(i,['NP'])
                lev, tag_ = self.__get_final_leaves_tag(i,pp_2)
                gram2_le.extend(lev)
                gram2_label.extend(tag_)
            '''
                Condition:3-->
                If prepositional phrase in first sentence, then we will get the chunks for NP (To get accurate conceptNet relation [It will
                makes the company ---> the_company, the building ----> the_building]) 
    
                Get the leaves for first sentence
            '''
        elif len(pp1)> 0 and len(pp2)==0:
            for i in pp1:
                t, pp_1 = self.__get_chunk(i,['NP'])
                lev, tag_ = self.__get_final_leaves_tag(i,pp_1)
                gram1_le.extend(lev)
                gram1_label.extend(tag_)
            print('First PP')
        else:
            print('No PP')
        #     parse_sent = parser.parse(sent1.lower())
        ### Call the function execute_me to get the relation between two words, to find the common words between two words and tag of the words 
        print(gram1_le,gram2_le,gram1_label,gram2_label)
        parse_sent1,parse_sent2,word_diff,relation_diff,word_tag1 = self.__execute_me(gram1_le,gram2_le,gram1_label,gram2_label,parse_sent1,parse_sent2)
        word.append(word_diff)
        realtion.append(relation_diff)
        word_tag.append(word_tag1)
        return(parse_sent1,parse_sent2,word,realtion,word_tag)
        #     parse_sent.pretty_print()
        
    def changes_in_tree(self,gram1):
    #     gram1.pretty_print()
        PP = []
        for i in gram1.treepositions()[::-1]:
            try: 
                if(gram1[i].label() in ['VP','PP','QP'] ):
                    if len(gram1[i].leaves()) !=0:
                        PP.append(i)
    #                     print(gram1[i].pos())
            except:
                pass
        for k in PP:
        #     print(gram1[k].label())
            match = [j[0]==j[1] if j[1] not in ['IN','CC','PP','VP','QP'] else True for j in gram1[k].pos()]
            if sum(match)/len(match)>=0.6:
                if gram1[k].label() == 'VP':
                    gram1[k] = nltk.tree.Tree.fromstring('(VP [Verb-Phrase])')
                elif gram1[k].label() == 'PP':
                    gram1[k] = nltk.tree.Tree.fromstring('(PP [Prepositional-Phrase])')
                elif gram1[k].label() == 'QP':
                    gram1[k] = nltk.tree.Tree.fromstring('(QP [Q-phrase])')
    #             elif gram1[k].label() == 'NP':
    #                 gram1[k] = nltk.tree.Tree.fromstring('(NP [N-phrase])')
                else:
                    pass
        gram1.pretty_print()
        
    def get_tree_differance(self,word, realtion,word_tag):
        for j,k,l in zip(word, realtion,word_tag):
        #     print(k)
            for p,q,r in zip(j,k,l):
        #         print(p,r,q)
                for a,b,c in zip(p,q,r):
                    print(str(a)+' // '+ str(c)+' // '+str(b))
        
    def get_tree_intersection(self,parse_sent1,parse_sent2):
        '''
            This function matches the two trees nodes. If a node is common in both the trees,
            then that node will removed from both the trees
        '''
        l2 = list(parse_sent2.subtrees())
        for i in parse_sent1.treepositions()[::-1]:
            try:
                if parse_sent1[i].height() ==2 and parse_sent1[i] not in l2:
    #                 print(parse_sent1[i])
                    del parse_sent1[i] 
            except:
                pass
    
        l1 = list(parse_sent1.subtrees())
        for i in parse_sent2.treepositions()[::-1]:
            try:
                if parse_sent2[i].height() ==2 and parse_sent2[i] not in l1:
    #                 print(parse_sent2[i])
                    del parse_sent2[i] 
            except:
                pass
        parse_sent1.pretty_print()
        parse_sent2.pretty_print()