from dialogue import Dialogue, DialogueEnum, register_dialogue


dialogue1 = Dialogue(DialogueEnum.HANDSHAKE)
dialogue1.send_header().expect_acknowledgement()

dialuge2 = Dialogue(DialogueEnum.HANDSHAKE)
dialuge2.accept_header().acknowledge()

register_dialogue(dialogue1, dialuge2)