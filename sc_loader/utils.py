class Empty:
    pass

def to_vars(data):
    return [
        [
            data[lin][col]
            for lin in range(1, len(data))
            if data[lin][col] != Empty
        ]
        for col in range(len(data[0]))
    ]
