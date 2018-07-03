from polity.models import Polity

# Context processor for showing menu list with polities.
def polities(request):

    polities = Polity.objects.all()

    # The parent/children map is only to reduce database calls.
    parent_children_map = {}
    for polity in polities:
        if not parent_children_map.has_key(polity.id):
            parent_children_map[polity.id] = []

        if polity.parent_id:
            parent_children_map[polity.parent_id].append(polity)

    # Result variable.
    polity_menulist = []

    # Function to recursively add sub-polities.
    def add_to_menulist(polity_menulist, polity, depth):
        polity_menulist.append({
            'polity_id': polity.id,
            'name': polity.name,
            'depth': depth,
        })

        # Iterate through children (see above) and add them as well.
        for subpolity in parent_children_map[polity.id]:
            add_to_menulist(polity_menulist, subpolity, depth + 1)

    # Add "root" polities with a depth of 0.
    root_polities = Polity.objects.filter(parent_id=None)
    if len(root_polities) == 1:
        # If there is only one root polity, we'll only want to add its
        # children, and not the root polity itself.
        for subpolity in parent_children_map[root_polities[0].id]:
            add_to_menulist(polity_menulist, subpolity, 0)
    else:
        for root_polity in root_polities:
            add_to_menulist(polity_menulist, root_polity, 0)

    ctx = {
        'polity_menulist': polity_menulist,
    }
    return ctx
