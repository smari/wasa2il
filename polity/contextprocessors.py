from collections import OrderedDict
from polity.models import Polity

def navigation(request):

    # For now, we only support one level of sub-polities in the navigation.
    # This is mostly because we haven't designed the interface to accommodate
    # sub-sub-polities, and we're not likely to use them any time soon.
    #
    # This may seem overly convoluted (and hopefully adequately explained in
    # comments) but the effect we want is:
    #
    # a) All visible sub-polities of the uppermost polities being shown.
    # b) Only show polity types which actually contain sub-polities.
    # c) Order polity types as they are defined in the `Polity` model.
    # d) Sub-polity navigation being available from within sub-polities.

    # The resulting object, used in the template.
    polity_nav = OrderedDict()

    # Order of polity types as defined in Polity.POLITY_TYPES.
    type_order = [t[0] for t in Polity.POLITY_TYPES]

    # Get visible sub-polities of uppermost polity.
    polities = Polity.objects.visible().exclude(parent=None).filter(parent__parent=None)

    # Sort polities by type, in the order defined in Polity.POLITY_TYPES.
    polities = sorted(polities, key=lambda p: type_order.index(p.polity_type))

    # Add polities to the navigation, organized and ordered by type.
    for polity in polities:
        # Create the entry of the polity type if it doesn't exist.
        if polity.polity_type not in polity_nav:
            polity_nav[polity.polity_type] = {
                'polity_type_name': polity.get_polity_type_display(),
                'polities': [],
            }

        polity_nav[polity.polity_type]['polities'].append(polity)

    return { 'polity_nav': polity_nav }
