# """
# Retrieve the BuildOrder associated with the build string.

# Called from KnowledgeBot inheritor.
# """
# from sharpy.plans import BuildOrder

# # from .opening import LingRush, MacroBuild


# def retrieve_build(build: str) -> BuildOrder:
#     """
#     Retrieves BuildOrder class based on selected build.

#     Args:
#         build (str): name of build order

#     Returns:
#         BuildOrder: the selected build order
#     """
#     if build == "LingRush":
#         order = LingRush()
#     else:
#         order = MacroBuild()
#     return order
