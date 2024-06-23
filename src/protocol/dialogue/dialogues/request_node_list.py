from dialogue import Dialogue, DialogueEnum, register_dialogue


dialogue1 = Dialogue(DialogueEnum.REQUEST_NODE_LIST)
dialogue1.send_header()

dialuge2 = Dialogue(DialogueEnum.REQUEST_NODE_LIST)
dialuge2.accept_header()

register_dialogue(dialogue1, dialuge2)