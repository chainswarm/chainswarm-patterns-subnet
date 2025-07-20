# CREATE HERE SQL ALCHEMY FILES FOR STORING PATTERNS

# Patterns Table
# Id (big int auto increment), Pattern_Id (string max), Network (string), Asset Symbol, Asset Contract (native by default), Data (varchar max), TimeStamp, Importance (int)

# Acknowledged Patterns

# Id (bit ing), Pattern_Id (foreign key), Validator_HotKey (string), TimeStamp


# create data manager class
# we need to return patter which was not acknowledged byt the validator with given key, ordered by id and importance

# second methos is about adding new entry into acknowledged patters ( patter id, validator hotkey)