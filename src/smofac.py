# TODO: parse the map to build each cell's nextcell and prevcell

# exit area
if X.fruit: # to the blender!
    del fruit
cell = X.prevcell
while cell != L:
    if cell.fruit:
        cell.nextcell.fruit = cell.fruit
        del cell.fruit
    cell = cell.prevcell

# loading cell
if L.fruit:
    if L.fruit.isleaving: # part of previous combo
        K.fruit = L.fruit
        del L.fruit
    elif L.fruit: # TODO: this will always happen
        if L.prevcell.fruit:
            if (L.fruit, L.prevcell.fruit) in recipes:
                K.fruit = L.fruit
                del L.fruit
                L.prevcell.fruit.isleaving = True
            else: # 2 fruits but no recipe matching
                L.nextcell.fruit = L.fruit
                del L.fruit
        else: # fruit in L, but not in L.prevcell: wait for more fruits to come
            pass # TODO: should set the fruit's sprite state to "standing" instead of "walking"

# looping area
cell = L.prevcell
while cell != L:
    if cell.fruit:
        cell.nextcell.fruit = cell.fruit
        del cell.fruit
    cell = cell.prevcell

# entrance area
if J.fruit:
    if J.nextcell.fruit:
        pass # TODO: sprite should be "standing" instead of "walking"
    else: # join the loop
        J.nextcell.fruit = J.fruit
        del J.fruit
cell = J.prevcell
while cell != E:
    if cell.fruit:
        if nextcell.fruit:
            pass # TODO: "standing" sprite 
        else: # no fruit ahead: move
            cell.nextcell.fruit = cell.fruit
            del cell.fruit
    cell = cell.prevcell