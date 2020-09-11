![Example](https://i.ibb.co/M2Rsvgb/example.png)
# vk-tree
 Designed to analyze friendships

# Example
To take friends tree:

    from vktree import *
     
    parcer = Parcer(login='login', password='password')
    tree = parcer.download_tree('id', 2)
     
    print_tree(tree, 0)
     
    len_tree(tree)
