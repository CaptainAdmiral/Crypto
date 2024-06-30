from dialogue import Dialogue, DialogueEnum, register_dialogue


dialogue1 = Dialogue(DialogueEnum.REQUEST_NODE_LIST)
dialogue1.send_header().expect(lambda data, state, protocol: data)

dialogue2 = Dialogue(DialogueEnum.REQUEST_NODE_LIST)
dialogue2.accept_header().do(lambda data, state, protocol: data)

register_dialogue(dialogue1, dialogue2)