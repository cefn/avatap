import milecastles
import engine

storyIds = [
    "corbridge",
    "arbeia",
    "housesteads",
    "senhouse",
]

def cacheTemplates():
    for storyId in storyIds:
        story = milecastles.loadStory(storyId)
        nodeTable = story._get_table(milecastles.Node)
        for nodeUid, node in nodeTable.items():
            nodeType = type(node)
            if nodeType.templateNames is not None:
                for templateName in nodeType.templateNames:
                    engine.cacheTemplate(story, node, templateName)