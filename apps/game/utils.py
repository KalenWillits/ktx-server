def calculate_modifier(*attributes: int) -> float:
    '''
    Calculate a skill modifier based on primary attributes.
    '''
    num_attributes = len(attributes)
    sum_attributes = sum(attributes)

    return float((sum_attributes/num_attributes)/2)
