# Vk-Tree
 Designed to analyze friendships

# Example
To take friends tree:

    import parcer
    parce_man = parcer.Manager(id=MIAN_ID,
                               name=MAIN_NAME,
                               deep=DEEP,
                               login=LOGIN,
                               password=PASSWORD)
    parce_man.build_tree()
    tree = parce_man.get_tree()

    print(tree[1])
    [{'id':21345634, 'name':"Vova Vova", 'img':"https://image.jpg"},
    ...]
