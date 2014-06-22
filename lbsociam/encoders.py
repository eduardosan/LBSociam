import json

class JSONEncoder(json.JSONEncoder):
    """
    Encode objects to JSON
    """
    def default(self, obj):
        """
        Return dict as default
        """
        return obj.__dict__

