import milecastles
import engine
import boilerplate

def cacheTemplates():

    storyIds = [
        #"arbeia",
        #"corbridge",
        #"housesteads",
        "senhouse",
    ]

    qstrings = {
        "/flash",
        "/flash/lib",
        "boot.py",
        "nextNode",
        "falseNode",
        "trueNode",
        "faces",
        "stories",
        "templates",
        "font_5x7",
    }
    for storyId in storyIds:
        qstrings.add("stories." + storyId)
        story = milecastles.loadStory(storyId)
        nodeTable = story._get_table(milecastles.Node)
        for nodeUid, node in nodeTable.items():
            nodeType = type(node)
            if nodeType.templateNames is not None:
                for templateName in nodeType.templateNames:
                    engine.cacheTemplate(story, node, templateName)

                    # calculate the qstrings which will be used to load info
                    moduleName = boilerplate.getTemplateModuleName(engine.getTemplateId(story, node, templateName))
                    qstrings.add(moduleName)
                    for moduleNameFrag in moduleName.split("."):
                        qstrings.add(moduleNameFrag)
                        for refName in moduleNameFrag.split("_"): # gets the node ids, story ids, and template names
                            qstrings.add(refName)
    for qstring in sorted(qstrings):
        print("Q({})".format(qstring))