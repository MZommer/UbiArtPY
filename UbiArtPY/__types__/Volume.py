class Volume:
    db: float

    def __init__(self, db):
        self.db = float(db)
    
    def __str__(self):
        return str(self.db)
    
    def __eq__(self, __value) -> bool:
        if isinstance(__value, Volume):
            return self.db == __value.db
        if isinstance(__value, float):
            return self.db == __value
        return False
