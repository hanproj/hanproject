def draw_network(fname, savename):
    
    alt.data_transformers.disable_max_rows()
    data = pd.read_csv(fname, delimiter = '\t')
    character_vowels = dict(zip(data['RHYME_WORD'], data['VOWEL']))
    character_vowels['慍'] = 'u'
    rhymes = get_rhymes(fname)
    pos = nx.spring_layout(rhymes)
    
    nx.set_node_attributes(rhymes, character_vowels, name = 'vowel')
    nx.set_node_attributes(rhymes, {node: node for node in rhymes.nodes()}, name = 'character')
    
    graph = nxa.draw_networkx(
    G=rhymes,
    pos=pos,
    node_size=300,
    node_color='vowel',
    cmap='accent',
    node_label = 'character'
)
    graph = graph.interactive()
    graph = graph.properties(height = 1000, width = 1000)
    graph.save(savename)
    return graph