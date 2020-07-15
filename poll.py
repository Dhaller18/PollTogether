class PollRoom:

    def __init__(self, owner, room_id):
        self.polls = {}
        self.owner = owner
        self.roomID = room_id

class Poll:
    def __init__(self, room, question, response_type, choices, active=False):
        self.room = room
        self.question = question
        self.response_type = "Multiple choice"
        self.display_type = "pie chart"
        self.responses = choices
        self.active = active



class PollParticipant:
    def __init__(self, nickname, room):
        self.nickname = nickname
        assert isinstance(room, PollRoom)
        self.room = room

    @property
    def room(self):
        return self.room

    @property
    def nickname(self):
        return self.nickname


class PollResponse:
    def __init__(self, participant, response):
        """
        Constructs all the necessary attributes for a poll response

        :parameter:
        __________
            :type participant: PollParticipant
                response's owner
            :type response: str
                response to the question
        """
        assert isinstance(participant, PollParticipant)
        self.participant = participant
        self.response = response

    @property
    def participant(self):
        """
        Returns the participant who made this response
        :return: participant: PollParticipant
        """
        return self.participant
