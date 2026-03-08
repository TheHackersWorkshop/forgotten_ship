class ItemManager:
    def __init__(self, items):
        self.items = items

    def get_all_positions(self):
        result = {}
        for item in self.items:
            if item.get("position"):
                result[item["name"]] = tuple(item["position"])
        return result
