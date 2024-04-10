def union_victims(maps):
    if len(maps) == 0:
        return
    
    full_map = maps[0]
    for i in range(1, len(maps)):
        for key, value in maps[i]:
            if key not in full_map:
                full_map[key] = value

    return full_map
