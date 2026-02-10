produtos = {
    "Camisa": 79.90, 
    "Calca": 119.90, 
    "Bone": 29.90, 
    "chinelo": 54.60, 
    "sapato": 84.90
}

produtos["Calca"] = 100
produtos.update({"Calca":30, "bone":10})
print(produtos)